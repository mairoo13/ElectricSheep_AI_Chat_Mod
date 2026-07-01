# -*- coding: utf-8 -*-
# AI Chat — DeepSeek API + GPT-SoVITS TTS + 游戏原生对话框

# ============================================================
# LLM API 配置（持久化，可在设置界面修改）
# ============================================================
init python:
    DEFAULTS = {
        "url": "",
        "key": "",
        "model": "",
    }
    if persistent.ai_chat_api_url is None:
        persistent.ai_chat_api_url = DEFAULTS["url"]
    if persistent.ai_chat_api_key is None:
        persistent.ai_chat_api_key = DEFAULTS["key"]
    if persistent.ai_chat_api_model is None:
        persistent.ai_chat_api_model = DEFAULTS["model"]

init python:
    import re
    import json
    import os
    import requests

    # ============================================================
    # Runtime API helpers (reads persistent, falls back to defaults)
    # ============================================================
    def _api_url():
        return persistent.ai_chat_api_url or DEFAULTS["url"]
    def _api_key():
        return persistent.ai_chat_api_key or DEFAULTS["key"]
    def _api_model():
        return persistent.ai_chat_api_model or DEFAULTS["model"]

    AI_CHAT_MAX_TOKENS = 512

    # ============================================================
    # GPT-SoVITS TTS Configuration
    # ============================================================
    TTS_API_URL        = "http://127.0.0.1:9880/tts"
    TTS_REF_AUDIO      = "ref_mai.wav"
    TTS_PROMPT_TEXT    = "みなさんこんにちは桜島舞です"
    TTS_PROMPT_LANG    = "ja"
    TTS_TEMP_DIR       = os.path.join(renpy.config.gamedir, "ai_chat", "tts_cache")

    # GPT-SoVITS 安装目录（用于自动启动 API）
    TTS_SOVITS_DIR     = r"E:\GPT-SoVITS-v2pro-20250604-nvidia50"
    TTS_PYTHON_EXE     = os.path.join(TTS_SOVITS_DIR, "runtime", "python.exe")
    TTS_API_SCRIPT     = os.path.join(TTS_SOVITS_DIR, "api_v2.py")
    TTS_API_CONFIG     = os.path.join(TTS_SOVITS_DIR, "GPT_SoVITS", "configs", "tts_infer.yaml")
    TTS_API_HOST       = "127.0.0.1"
    TTS_API_PORT       = 9880

# ============================================================
# TTS enable flag (persists across saves)
# ============================================================
default ai_chat_tts_enabled = True

# AI 回复当前语言选择显示变量
default ai_chat_lang_display = "中文"

init python:

    def _update_ai_chat_lang_display():
        lang = persistent.ai_chat_lang if hasattr(persistent, 'ai_chat_lang') else "zh"
        store.ai_chat_lang_display = {"zh":"中文","en":"English","ja":"日本語"}.get(lang, "中文")

    if persistent.ai_chat_lang is None:
        persistent.ai_chat_lang = "zh"

    # ============================================================
    # ResponseParser
    # ============================================================
    class ResponseParser(object):
        PATTERN2 = re.compile(r'\[([^\]]+)\]\s*\|\|\|\s*(.*)', re.DOTALL)  # 两段式
        PATTERN3 = re.compile(r'\[([^\]]+)\]\s*\|\|\|\s*(.*?)\s*\|\|\|\s*(.*)', re.DOTALL)  # 三段式（兼容）
        PATTERN_EMOTION = re.compile(r'\[([^\]]+)\]')
        VALID = {"Happy","Sad","Normal","Surprised","Angry","Worried","Shy","Love"}

        @classmethod
        def parse(cls, raw_text):
            if not raw_text:
                return {"emotion":"Normal","text":"","is_valid":False}
            text = raw_text.strip()
            # 先尝试三段式 [Emotion]|||jp|||cn（向后兼容旧格式）
            m3 = cls.PATTERN3.match(text)
            if m3 and m3.group(1).strip() in cls.VALID:
                lang = persistent.ai_chat_lang if hasattr(persistent, 'ai_chat_lang') else "zh"
                if lang == "ja":
                    final = m3.group(2).strip()
                elif lang == "en":
                    final = m3.group(3).strip() or m3.group(2).strip()
                else:
                    final = m3.group(3).strip() or m3.group(2).strip()
                return {"emotion":m3.group(1).strip(),"text":final,"is_valid":True}
            # 两段式 [Emotion]|||text
            m2 = cls.PATTERN2.match(text)
            if m2 and m2.group(1).strip() in cls.VALID:
                return {"emotion":m2.group(1).strip(),"text":m2.group(2).strip(),"is_valid":True}
            # 只匹配情绪标签
            m = cls.PATTERN_EMOTION.search(text)
            if m and m.group(1).strip() in cls.VALID:
                rest = cls.PATTERN_EMOTION.sub("",text).strip()
                rest = re.sub(r'\|\|\|',' ',rest).strip()
                return {"emotion":m.group(1).strip(),"text":rest or text,"is_valid":True}
            return {"emotion":"Normal","text":text,"is_valid":False}

    # ============================================================
    # EmotionMapper
    # ============================================================
    class EmotionMapper(object):
        MAP = {"Happy":"Happy","Sad":"Sad","Normal":"Normal","Surprised":"Happy",
               "Angry":"Annoyed","Worried":"Worried","Shy":"Shy","Love":"Love"}

        @classmethod
        def apply(cls, emotion):
            target = cls.MAP.get(emotion, "Normal")
            if target != store.ako_mood:
                store.ako_mood_next = target
                return True
            return False

    # ============================================================
    # TTS API 启动器 — 自动管理 GPT-SoVITS 后台进程
    # ============================================================
    class TTSLauncher(object):
        """管理 GPT-SoVITS API 的启停。"""

        _process  = None
        _started  = False  # 防止重复启动

        @classmethod
        def is_running(cls):
            """用 socket 检测端口是否已被占用（即 API 是否运行中）。"""
            import socket
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(1.0)
                s.connect((TTS_API_HOST, TTS_API_PORT))
                s.close()
                return True
            except:
                return False

        @classmethod
        def start(cls):
            """启动 GPT-SoVITS API 后台进程。仅执行一次。"""
            if cls._started:
                return cls.is_running()
            cls._started = True

            if cls.is_running():
                return True

            if not os.path.exists(TTS_PYTHON_EXE):
                return False
            if not os.path.exists(TTS_API_SCRIPT):
                return False

            try:
                import subprocess
                cmd = [
                    TTS_PYTHON_EXE,
                    TTS_API_SCRIPT,
                    "-a", TTS_API_HOST,
                    "-p", str(TTS_API_PORT),
                    "-c", TTS_API_CONFIG,
                ]
                # CREATE_NO_WINDOW = 0x08000000，防止弹出 CMD 窗口
                cls._process = subprocess.Popen(
                    cmd,
                    cwd=TTS_SOVITS_DIR,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=0x08000000,
                )
                return True
            except:
                return False

        @classmethod
        def stop(cls):
            """停止 API 后台进程。"""
            if cls._process is not None:
                try:
                    cls._process.terminate()
                    cls._process = None
                except:
                    pass
            # 通过 /control 端点优雅退出
            import urllib.request
            try:
                url = f"http://{TTS_API_HOST}:{TTS_API_PORT}/control"
                data = json.dumps({"command": "exit"}).encode("utf-8")
                req = urllib.request.Request(url, data=data, method="POST")
                req.add_header("Content-Type", "application/json")
                urllib.request.urlopen(req, timeout=3)
            except:
                pass
            cls._started = False

    # ============================================================
    # GPT-SoVITS TTS Client
    # ============================================================
    class TTSClient(object):
        def __init__(self, ref_audio=TTS_REF_AUDIO, prompt_text=TTS_PROMPT_TEXT,
                     prompt_lang=TTS_PROMPT_LANG):
            self.ref_audio = ref_audio
            self.prompt_text = prompt_text
            self.prompt_lang = prompt_lang
            # Ensure cache dir exists
            try:
                if not os.path.exists(TTS_TEMP_DIR):
                    os.makedirs(TTS_TEMP_DIR)
            except:
                pass

        def synthesize(self, text, text_lang="ja"):
            """Call TTS API and save to cache file. Returns path or None on failure."""
            if not text or not text.strip():
                return None

            # Ensure cache dir exists
            try:
                if not os.path.exists(TTS_TEMP_DIR):
                    os.makedirs(TTS_TEMP_DIR)
            except:
                pass

            # Use cached file if same text was already synthesized
            cache_name = "tts_" + str(hash(text.strip())) + ".wav"
            cache_path = os.path.join(TTS_TEMP_DIR, cache_name)
            cache_path_fwd = cache_path.replace("\\", "/")
            if os.path.exists(cache_path) and os.path.getsize(cache_path) > 0:
                return cache_path_fwd

            data = {
                "text": text.strip(),
                "text_lang": text_lang,
                "ref_audio_path": self.ref_audio,
                "prompt_lang": self.prompt_lang,
                "prompt_text": self.prompt_text,
                "text_split_method": "cut5",
                "batch_size": 1,
                "media_type": "wav",
                "streaming_mode": False
            }
            try:
                r = requests.post(TTS_API_URL, json=data,
                    headers={"Content-Type": "application/json"}, timeout=30)
                if r.status_code == 200 and len(r.content) > 100:
                    with open(cache_path, "wb") as f:
                        f.write(r.content)
                    return cache_path.replace("\\", "/")
            except:
                pass
            return None

# ============================================================
# Singletons + Audio Channel
# ============================================================
init 999 python:
    ai_chat_client  = AIChatClient()     # 上下文感知 + 持久化记忆
    emotion_mapper  = EmotionMapper()
    response_parser = ResponseParser()
    tts_client      = TTSClient()

    # Register a dedicated audio channel for AI TTS voice
    # "voice" mixer keeps it independent from "sfx" (dialog1.mp3) and "music"
    renpy.music.register_channel("ai_tts", mixer="voice", loop=False,
                                  stop_on_mute=True, tight=False)

# ============================================================
# AI Chat Player Character (for dialogue history, color #2b518b)
# ============================================================
define ai_player = Character("player_name", dynamic = True, color = "#2b518b", size = 60, what_font = "gui/fonts/font_player.otf", what_size = 30)

# ============================================================
# Entry
# ============================================================
label ai_chat_start:
    $ _update_ai_chat_lang_display()
    scene bg_home_talk idle
    menu:
        "[icon_talk]开始对话":
            if persistent.ai_chat_api_url and persistent.ai_chat_api_key:
                jump ai_chat_dialog_loop
            else:
                "请先在「LLM 配置」中填写 API URL 与 API Key。"
                jump ai_chat_start
        "[icon_choice]AI语言: {color=#8ec9ff}[ai_chat_lang_display]{/color}":
            jump ai_chat_language_select
        "[icon_choice]模拟人声: {color=#9acc25}ON{/color}" if ai_chat_tts_enabled:
            jump ai_chat_toggle_tts
        "[icon_choice]模拟人声: {color=#a61b11}OFF{/color}" if not ai_chat_tts_enabled:
            jump ai_chat_toggle_tts
        "[icon_choice]LLM 配置":
            jump ai_chat_llm_config
        "[icon_goback]退出":
            scene bg_home_talk idle
            jump ako_chat_idler

label ai_chat_language_select:
    menu:
        "选择 Ako 的回复语言（当前: [ai_chat_lang_display]）"
        "中文":
            $ persistent.ai_chat_lang = "zh"
            $ _update_ai_chat_lang_display()
            "已切换为中文模式"
        "English":
            $ persistent.ai_chat_lang = "en"
            $ _update_ai_chat_lang_display()
            "Switched to English mode."
        "日本語":
            $ persistent.ai_chat_lang = "ja"
            $ _update_ai_chat_lang_display()
            "日本語モードに切り替えました。"
    jump ai_chat_start

label ai_chat_toggle_tts:
    $ ai_chat_tts_enabled = not ai_chat_tts_enabled
    if ai_chat_tts_enabled:
        # 首次开启模拟人声时自动启动 GPT-SoVITS API
        if not TTSLauncher.is_running():
            "正在启动语音合成引擎……"
            if TTSLauncher.start():
                "模拟人声: ON\n（麻衣声线引擎已启动，请稍候初始化）"
            else:
                "模拟人声: ON\n（警告：无法启动语音合成引擎，请手动运行 run_api.bat）"
        else:
            "模拟人声: ON\n（Ako 将使用麻衣声线朗读日语回复）"
    else:
        "模拟人声: OFF\n（仅显示文字，不朗读）"
    jump ai_chat_start

# ============================================================
# LLM 配置 — 使用 renpy.input 简单交互式配置
# ============================================================
label ai_chat_llm_config:
    scene bg_home_talk idle
    menu:
        "LLM API 配置\n当前: [persistent.ai_chat_api_url]"
        "修改 API URL":
            $ new_url = renpy.input("API URL:", default=persistent.ai_chat_api_url or "", length=80)
            if new_url.strip():
                $ persistent.ai_chat_api_url = new_url.strip()
            jump ai_chat_llm_config
        "修改 API Key":
            $ new_key = renpy.input("API Key:", default=persistent.ai_chat_api_key or "", length=80)
            if new_key.strip():
                $ persistent.ai_chat_api_key = new_key.strip()
            jump ai_chat_llm_config
        "修改 Model Name":
            $ new_model = renpy.input("Model Name:", default=persistent.ai_chat_api_model or "", length=40)
            if new_model.strip():
                $ persistent.ai_chat_api_model = new_model.strip()
            jump ai_chat_llm_config
        "清空配置":
            $ persistent.ai_chat_api_url = ""
            $ persistent.ai_chat_api_key = ""
            $ persistent.ai_chat_api_model = ""
            "已清空所有配置。"
            jump ai_chat_llm_config
        "返回":
            jump ai_chat_start

# ============================================================
# Input → Think → Reply → Loop
# ============================================================
label ai_chat_dialog_loop:
    # 输入框上方显示玩家名字（颜色 #2b518b）
    $ input_prompt = "{color=#2b518b}" + store.player_name + "{/color}"
    $ store.ai_chat_user_input = renpy.input(input_prompt)
    $ user_input = store.ai_chat_user_input.strip() if store.ai_chat_user_input else ""

    if user_input == "":
        "Ako 看起来有些疑惑……\n{w}看来你暂时不想聊了。"
        scene bg_home_talk idle
        jump ako_chat_idler

    $ ai_chat_client.memory.add_user(user_input)

    # 异步请求 LLM + TTS（在后台线程中串联执行）
    $ store.ai_chat_response = None
    $ store.ai_chat_waiting  = True
    # 如果 TTS 开启但 API 未运行，尝试自动启动
    if ai_chat_tts_enabled:
        $ TTSLauncher.start()
    python:
        def on_llm_done(llm_result):
            combined = {"llm": llm_result, "tts_wav": None}
            # TTS 仅在日语模式下生效
            if not llm_result.get("error") and store.ai_chat_tts_enabled:
                lang = persistent.ai_chat_lang if hasattr(persistent, 'ai_chat_lang') else "zh"
                if lang == "ja":
                    parsed = response_parser.parse(llm_result.get("content", ""))
                    jp_text  = parsed.get("text", "")
                    if jp_text:
                        wav_path = tts_client.synthesize(jp_text, "ja")
                        if wav_path:
                            combined["tts_wav"] = wav_path
            store.ai_chat_response = combined
            store.ai_chat_waiting  = False

        ai_chat_client.send_async(user_input, cb=on_llm_done)

    show screen ai_chat_thinking
    while ai_chat_waiting:
        $ renpy.pause(0.2)
    hide screen ai_chat_thinking

    $ combined = store.ai_chat_response or {}
    $ resp     = combined.get("llm", {})

    if resp.get("error"):
        $ error_text = resp["error"]
        a "[error_text]"
        jump ai_chat_dialog_loop

    # 解析回复并切换情绪动画（平滑过渡）
    $ parsed = response_parser.parse(resp.get("content",""))
    $ ai_chat_client.memory.add_assistant(resp.get("content",""))
    $ store.ai_mood_changed = emotion_mapper.apply(parsed["emotion"])

    if store.ai_mood_changed:
        show bg_home_talk trans
        pause 1.0
        $ store.ako_mood = store.ako_mood_next
        show bg_home_talk idle

    $ reply_text = parsed["text"]
    $ emotion_key = parsed["emotion"]

    # TTS 语音播放（ai_tts 声道，与 dialog1.mp3 的 sound 声道互不干扰）
    $ tts_wav = combined.get("tts_wav")
    if tts_wav:
        $ renpy.sound.play(tts_wav, channel="ai_tts")

    # 原生动画：bg_home_talk talk/idle（与原始游戏 "你还好吗" 一致的模式）
    show bg_home_talk talk
    a "[reply_text]"

    # 停止语音
    if tts_wav:
        $ renpy.sound.stop(channel="ai_tts")

    # ── 小概率 Sad 安抚事件（Ako 说完后才触发） ──
    if emotion_key == "Sad" and store.ako_mood in ("Sad", "Worried"):
        if renpy.random.random() < 0.25:
            "{i}Ako 看上去好像有点难过……{/i}"
            menu:
                "[icon_heart]安慰她":
                    jump ai_chat_comfort_cuddle
                "[icon_talk]继续对话":
                    pass

    jump ai_chat_dialog_loop


# ============================================================
# Sad 情绪中断 — 安抚 Cuddle 特殊事件
# ============================================================
define icon_heart = "{font=gui/fonts/font_guifx.ttf}{color=#ff8fab}< {/color}{/font}"

# 安抚用自定义按钮屏（复用 akomood 驱动的 headpat 动画素材）
screen ai_chat_cuddle_buttons():
    vbox:
        xalign 0.03
        yalign 0.5
        spacing 15
        textbutton "• Pat":
            style "h_buttons_position"
            action Jump("ako_headpat_loop")
        if headpat_talk2 == True:
            textbutton "• Stroke":
                style "h_buttons_position"
                action Jump("ako_cheekstroke_loop")
            textbutton "• Squeeze":
                style "h_buttons_position"
                action Jump("ako_squeeze_loop")
            textbutton "• Pinch":
                style "h_buttons_position"
                action Jump("ako_pinch_loop")
        textbutton "":
            action None
        textbutton "• Stop":
            style "h_buttons_default"
            action Jump("ako_headpat_stop")
        textbutton "":
            action None
        textbutton "• Return":
            style "h_buttons_default"
            action Jump("ai_chat_cuddle_return")

    vbox:
        xalign 0.985
        yalign 0.1
        xysize(50, 525)
        xmaximum 100
        vbar:
            value AnimatedValue(value=ako_happiness_daily, range=10, delay=1.0)
            left_bar "happinessbar_bottom"
            right_bar "happinessbar_top"

# 安抚入口：跳过首次对话，直接进入抚摸场景
label ai_chat_comfort_cuddle:
    $ headpat_talk = True          # 跳过"如你所愿"初次对话
    $ _skipping = False
    $ quick_menu = False
    $ headpatmode = 'Stop'
    scene ako_headpat takeoff with Fade(0.0, 0.0, 0.3)
    pause 2.0
    scene ako_headpat idle
    show screen ai_chat_cuddle_buttons with Dissolve(0.1)
    $ renpy.pause(delay = None, hard = True)

# 玩家按 Return 后跳转至此
label ai_chat_cuddle_return:
    hide screen ai_chat_cuddle_buttons
    $ _skipping = True
    $ quick_menu = True
    if stress < 0:
        $ stress = 0
    # 安抚后情绪回到平静
    $ store.ako_mood = "Normal"
    $ store.ako_mood_next = "Normal"
    # 纯黑背景中 Ako 表达感谢
    scene bg_black2 with fade
    pause 1
    a "谢谢你，[p2]...有你在身边，我感觉好多了。"
    # 回到原本的对话动画序列
    scene bg_black2
    show bg_home_talk idle with Dissolve(0.3)
    jump ai_chat_dialog_loop
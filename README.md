# ElectricSheep AI Chat Mod

**为 ElectricSheep 0.7.12 添加基于 LLM + GPT-SoVITS TTS 的 AI 全语音对话（Ren'Py 内嵌），让 Ako 拥有沉浸式 AI 对话能力。**

## 特色

- 使用任意兼容 OpenAI Chat Completions 格式的 LLM API（如 DeepSeek、OpenRouter、OpenAI、Ollama 等）生成 Ako 的对话文本。
- 对话融入游戏剧情上下文——Ako 会根据当前故事进度、性格特质、关系状态进行沉浸式回答。
- Ako 拥有持久化记忆系统，能"记住"之前的 AI 对话内容。
- 支持中文 / English / 日本語 三种回复语言切换。
- 可选使用 GPT-SoVITS WebAPI v2ProPlus 生成麻衣声线的日语语音（仅日语模式触发，需自行部署）。
- 首次对话前需配置 LLM API，游戏内有引导提示。
- 含 Ako 悲伤时的随机安抚事件（小概率触发）。

## 安装说明

### 安装 Mod 本体

1. 下载 `ElectricSheep_AI_Chat_Mod.zip` 并解压。

2. 将解压后的 `game` 文件夹复制到游戏根目录 `ElectricSheep-0.7.12-pc/`，覆盖同名文件。
   - **注意**：只会覆盖 `game/interact_ako/ako_chat.rpy` 这一个文件（在 Small talk 菜单中添加了 AI Chat 入口）。其余文件均为新增。

3. 启动游戏 → 与 Ako 对话 → Small talk → AI Chat (DeepSeek)。

4. 此时尚未配置 LLM API，点击"开始对话"会提示先配置。请继续阅读下一章节。

### LLM API 配置（必需）

**本 Mod 不含任何默认 API Key。你需要自行获取以下任一 LLM 服务的 API Key。**

1. 在游戏 AI Chat 入口菜单，选择 "LLM 配置"。

2. 逐项填写：
   - **API URL** — LLM 接口地址（需兼容 OpenAI Chat Completions 格式）
   - **API Key** — 你的 API 密钥
   - **Model Name** — 模型名称（如 `deepseek-chat`、`gpt-3.5-turbo` 等）

3. API URL 示例：
   - DeepSeek：`https://api.deepseek.com/v1/chat/completions`
   - OpenRouter：`https://openrouter.ai/api/v1/chat/completions`
   - OpenAI：`https://api.openai.com/v1/chat/completions`
   - Ollama（本地部署）：`http://127.0.0.1:11434/v1/chat/completions`
   - Gemini：`https://generativelanguage.googleapis.com/v1beta/openai/chat/completions`

4. 配置完成后返回，即可开始对话。

> **注意**：聊天内容会发送到你配置的 API，请留心 API Key 与隐私策略。

### 语音配置（可选）

本项目依赖 [GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS)（简称 GSV）的 WebAPI v2ProPlus 来生成语音。
Mod 压缩包中已包含麻衣声线的 **模型权重 + 配置文件 + 参考音频**，只需三步即可启用。

#### 1. 安装 GPT-SoVITS

- Windows 用户：根据 GPT-SoVITS 的[文档](https://www.yuque.com/baicaigongchang1145haoyuangong/ib3g1e/dkxgpiy9zb96hob4)，直接下载整合包，解压后运行 `run_api.bat` 即可。如果没有 `run_api.bat`，可以自己建立一个 `run_api.bat.txt` 文件，编辑内容如下：
  ```bat
  @echo off
  .\runtime\python.exe api_v2.py -a 127.0.0.1 -p 9880
  pause
  ```
  然后重命名文件，将 `.txt` 后缀去掉即可。


#### 2. 放入麻衣声线模型（一键覆盖）

- 将 Mod 压缩包中的 `GPT-SoVITS/` 文件夹**整体覆盖**到 GPT-SoVITS 的根目录下。
  - **一定要看清是哪个目录**——这个根目录下应当有 `api_v2.py`、`README.md` 等文件。
  - **不要**错覆盖到 `GPT_SoVITS/` 子目录中。
- `GPT-SoVITS/` 文件夹内已包含：
  - `GPT_weights_v2ProPlus/麻衣v2-e15.ckpt` — GPT 模型权重（148 MB）
  - `SoVITS_weights_v2ProPlus/麻衣v2_e8_s200.pth` — SoVITS 模型权重（165 MB）
  - `GPT_SoVITS/configs/tts_infer.yaml` — 已配置好路径的 TTS 推理配置
  - `ref_mai.wav` — 麻衣声线参考音频

> 覆盖后无需手动配置任何东西——模型路径、参考音频路径都已在 `tts_infer.yaml` 中配好。

#### 3. 测试 TTS 服务

- 注：以下假设 WebAPI v2 的 TTS 服务运行于 `http://127.0.0.1:9880`。这是默认情况，若你做过改动，则在以下步骤中也要相应变更。
- 启动 API：双击 `run_api.bat` 等待模型加载完成。
- 在浏览器测试 TTS：
  ```
  http://127.0.0.1:9880/tts?text=こんにちは、お元気ですか？&text_lang=ja&ref_audio_path=ref_mai.wav&prompt_text=みなさんこんにちは桜島舞です&prompt_lang=ja
  ```
  > 它的基本作用是让这个 TTS 服务模仿 `ref_audio_path` 所指定的音频文件（台词为 `prompt_text` 的值）来合成 `text` 的语音音频。
  > 实际上，这里测试使用的是 WebAPI v2proplus 的 GET 用法，详见 [`api_v2.py`](https://github.com/RVC-Boss/GPT-SoVITS/blob/main/api_v2.py) 的注释。
  > 另外，若你的命令行有 `ffplay`（由 FFmpeg 提供），这样测试可以直接听到声音（不需要下载音频文件再手动播放）：
  > ```bash
  > ffplay -nodisp -autoexit 'http://127.0.0.1:9880/tts?text=こんにちは、お元気ですか？&text_lang=ja&ref_audio_path=ref_mai.wav&prompt_text=みなさんこんにちは桜島舞です&prompt_lang=ja&streaming_mode=True'
  > ```
- 测试过程中，GPT-SoVITS 会自动下载 `https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin` 到 GPT-SoVITS 根目录下的 `GPT_SoVITS/pretrained_models/fast_langdetect/lid.176.bin`。
- 稍等片刻，浏览器将会下载一个大约 300 KiB 大小的 `tts.wav` 文件，播放它应当能清晰地听到与游戏角色相似的日语语音。

#### 4. 在游戏中启用语音

- **请务必确保上一步 TTS 测试成功。否则，说明 TTS 服务未正常运行（在解决此问题之前，继续下一步是无意义的）。**
- 在游戏 AI Chat 入口菜单，选择"模拟人声"将其切换为 ON。
- 首次开启时，Mod 会自动在后台启动 GPT-SoVITS API（无 CMD 窗口弹出）。
  - 默认 GPT-SoVITS 路径为 `E:\GPT-SoVITS-v2pro-20250604-nvidia50`。若解压到其他路径，需修改 `game/ai_chat/ai_chat_loop.rpy` 中的 `TTS_SOVITS_DIR` 变量。
- 此后每次对话，若 AI 回复语言设为"日本語"，Ako 将以麻衣声线朗读回复。

## 使用说明

### 基本操作流程

1. 在游戏中与 Ako 对话 → 选择 **Small talk** → 选择 **AI Chat (DeepSeek)**。
2. 首次使用请先选择 **LLM 配置**填入你的 API 信息。
3. 进入 AI Chat 入口菜单，可选择：
   - **开始对话** — 进入自由对话模式
   - **AI 语言** — 切换 Ako 回复语言（中文 / English / 日本語）
   - **模拟人声** — 开/关 TTS 语音朗读
   - **LLM 配置** — 修改 API 参数
   - **退出** — 返回游戏正常对话
4. 对话中会显示提示文字 "• Ako 正在思考…"，等待片刻即可看到 Ako 的回复。

### 对话沉浸式设计

Ako 的回复会根据以下因素动态调整：
- **剧情进度**：Ako 只知道当前已触发的事件，不会提前知道后续剧情。
- **性格特质**：温柔（Affectionate）/ 执着（Obsessive）/ 忧伤（Mournful），言语风格不同。
- **关系状态**：恋人 / 病娇 / 顺从，态度不同。
- **当前情绪**：开心 / 悲伤 / 担心 / 害羞等。
- **往期对话记忆**：Ako 会记得之前 AI 对话中聊过的重要内容。

### AI 回复格式

AI 输出使用两段式格式（中间用 `|||` 分隔）：

```
[Emotion]|||回复文本
```

其中 Emotion 可选值为：Happy、Sad、Normal、Surprised、Angry、Worried、Shy、Love

示例：
```
[Happy]|||欢迎回来，主人！今天过得怎么样？
[Sad]|||我一直在想你……一个人待着的时候，总觉得有些寂寞。
```

### 悲伤安抚事件

当 Ako 情绪为 Sad 时，有小概率（25%）触发安抚事件：
- Ako 说完话后，屏幕短暂黑屏，显示内心独白
- 玩家可选择是否安抚 Ako
- 若选择安抚，将进入轻抚/依偎场景
- 安抚结束后回到对话，Ako 会表示感谢，情绪恢复平静

## 文件结构

```
game/                            # 游戏脚本（覆盖到游戏根目录）
├── screens_ai_chat.rpy          # 思考中提示屏
├── ai_chat/
│   ├── ai_chat_loop.rpy         # 主循环 / TTS / LLM 配置 / 对话逻辑
│   ├── ai_chat_context.rpy      # 上下文构建 / 记忆系统 / API 客户端
│   └── tts_cache/               # TTS 缓存目录（运行时自动生成）
└── interact_ako/
    └── ako_chat.rpy             # 对话入口（含 AI Chat 选项，已修改）

GPT-SoVITS/                      # 语音模型（覆盖到 GSV 根目录）
├── ref_mai.wav                  # 麻衣声线参考音频
├── GPT_SoVITS/configs/
│   └── tts_infer.yaml           # TTS 推理配置（已配好路径）
├── GPT_weights_v2ProPlus/
│   └── 麻衣v2-e15.ckpt          # GPT 模型权重
└── SoVITS_weights_v2ProPlus/
    └── 麻衣v2_e8_s200.pth       # SoVITS 模型权重
```

## 默认 TTS 配置（`ai_chat_loop.rpy` 中）

| 配置项 | 默认值 | 说明 |
|---|---|---|
| `TTS_API_URL` | `http://127.0.0.1:9880/tts` | TTS 服务地址 |
| `TTS_REF_AUDIO` | `ref_mai.wav` | 参考音频文件名 |
| `TTS_PROMPT_TEXT` | `みなさんこんにちは桜島舞です` | 参考音频对应台词 |
| `TTS_PROMPT_LANG` | `ja` | 参考音频语言 |
| `TTS_SOVITS_DIR` | `E:\GPT-SoVITS-v2pro-20250604-nvidia50` | GSV 安装目录 |

## 开源声明

本项目使用了以下开源项目：

- [GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS)：用于语音合成。许可协议：MIT
- [Ren'Py](https://www.renpy.org/)：视觉小说引擎。许可协议：MIT

## 问题排查

- **AI Chat 选项未出现**
  - 确认已正确覆盖 `game/interact_ako/ako_chat.rpy`。
  - 确认游戏版本为 ElectricSheep 0.7.12。

- **点击"开始对话"提示需配置 LLM**
  - 正常现象。请先在菜单中进入「LLM 配置」填写 API URL 和 API Key。

- **思考中提示一直不消失 / 对话无响应**
  - 检查网络连接，确保能访问 API URL。
  - 进入 LLM 配置确认 API Key 有效、模型名称正确。
  - API 余额不足时会提示相应错误。

- **模拟人声开启后没有声音**
  - 确认已按上文"语音配置"章节完成部署。
  - 确认 AI 回复语言设置为"日本語"（TTS 仅在日语模式生效）。
  - 确认 TTS 测试链接能正常返回音频。
  - 若手动修改过 `TTS_SOVITS_DIR`，确认路径正确。

- **每次说话弹出 CMD 窗口**
  - 不应发生——Mod 已使用 `CREATE_NO_WINDOW` 标志在后台启动。若出现此问题，请确认 `ai_chat_loop.rpy` 未被修改。

- **想重置长期记忆**
  - 删除 `game/saves/ai_chat/ai_chat_memory.json`，下次启动游戏时将自动重建空记忆文件。

label ako_chat_idler:
    menu ako_talk_choice:
        "[icon_talk_story]Something to show me?" if gravure_sales == True and gravure_sales_accept == False and gravure_sales_decline == False and gravure_sales_decline2 == False:
            $ ako_in_need = False
            scene bg_black2 with fade
            p "You said you got something to show me."
            a "Yes, please have a sit, [p2]."
            jump lable_gravure_sales

        "[icon_talk_story]Go visit Hal" if whydoyousleep_notnow == True and whydoyousleep2 == False:
            $ whydoyousleep2 = True
            $ robotshop_open = False
            $ ako_location_home = False
            $ ako_location_home_wait = 1
            show bg_home_talk talk
            a "I appreciate it, [p2]. I'll be back home by tomorrow morning."
            p "Yup."
            scene bg_black2 with fade
            "{i}[a] left to Dr. Hal's lab.\n{bt=2}{color=#9acc25}She'll be back home tomorrow.{/color}{/bt}{/i}"
            jump label_home2_nodoor

        "[icon_talk_story]While you sleep..." if goodtobeback == True and touchmeasyoulike == False and trashman == False:
            $ touchmeasyoulike = True
            p "[a]."
            show bg_home_talk talk
            a "Yes, [p2]?"
            menu:
                "[icon_talk]Would it be-":
                    p "Would it be okay for me to touch you while you are asleep?"
                    show bg_home_talk talk
                    a "I don't mind, [p2]. Please feel free to do as you like."
                    jump ako_chat_idler
                "[icon_talk]I want to-":
                    $ ako_yandere += 5
                    $ ako_lover -= 1
                    $ ako_slave -= 1
                    p "I want to touch you while you are asleep."
                    show bg_home_talk talk
                    a "Please be my guest, [p2]."
                    jump ako_chat_idler
                "[icon_talk]I'm gonna-":
                    $ ako_slave += 5
                    $ ako_lover -= 1
                    $ ako_yandere -= 1
                    p "I'm gonna touch you while you are asleep."
                    show bg_home_talk talk
                    a "...As you wish, [p2]."
                    jump ako_chat_idler
        
        "[icon_talk_story]An idea to tell me?" if pre_bigbrainidea == True and bigbrainidea_asked == True and bigbrainidea == False:
            $ bigbrainidea == True
            $ ako_in_need = False
            p "You said you got an idea to tell me."
            a "Ah, yes [p2]."
            jump lable_bigbrainidea
        
        "[icon_talk_story]Go visit Hal" if pre_bettercooling == True and bettercooling == False and ako_declined == True:
            $ bettercooling = True
            $ ako_declined = False
            $ robotshop_open = False
            $ ako_location_home = False
            $ ako_location_home_wait = 1
            show bg_home_talk talk
            a "Thank you, [p2].\nI'll be back home by tomorrow morning with the improved cooling capabilities."
            p "Yup."
            scene bg_black2 with fade
            "{i}[a] left to Dr. Hal's lab to report a design flaw.\n{bt=2}{color=#9acc25}She'll be back home tomorrow.{/color}{/bt}{/i}"
            jump label_home2_nodoor
        
        "[icon_talk_story]New somnifacient" if event26n5_newsomafacient == True and event26n5_newsomafacient_talk == False:
            $ event26n5_newsomafacient_talk = True
            $ ako_in_need = False
            show bg_home_talk talk
            if ako_trait == 'Mournful':
                p "No more somnifacient for you from today until there's none left in your body."
                a "....Understood, [p2]."
            else:
                p "[a], Hal made a new type of somnifacient but it can be hazardous if mixed with the current type."
                p "So until the residue in your body gets fully decomposed, I can't give you somnifacient. Sorry."
                a "Understood, [p2]. I will inform you when the residue of the current type of somnifacient is fully decomposed."
            scene bg_home_talk idle
            jump ako_interaction_choice
        
        "[icon_talk_story]Satchel and pepperball gun" if event32_gettingworse == True and event32_gettingworse_chat == False:
            $ event32_gettingworse_chat = True
            $ ako_in_need = False
            show bg_home_talk talk
            if ako_trait == 'Mournful':
                p "Hey, put this satchel next to the door when I'm sleeping."
                a "Understood, [p2]."
            else:
                p "[a], when we are both home, I want you to place this satchel next to the door and attach the string to the doorknob."
                a "May I ask what is it for, [p2]?"
                p "It's something Hal gave me.\nHe said if someone tries to forcefully breach in, it will seal the door."
                a "I see. I will make sure to place it properly when we are both inside, [p2]."
                p "Good. And I want you to stay inside no matter what from today onwards.\nI've heard from Hal that the android arsoning is getting worse and worse."
                $ ako_mood_next = 'Worried'
                call akomood_changer
                a "But [p2], what about your safety?\nIf it's becoming so dangerous out there for androids, surely you should also remain indoors?"
                p "Haven't we talked about this before...? You know I can't do that."
                p "Besides, I'm gonna be fine as long as they don't see me with an android..."
                a "[p2], your safety is my absolute priority.\nI insist you stay inside with me until the situation gets under control."
                p "I'll... {w}I'll try to stay with you as much as I can."
                a "Please promise me that you will exercise extreme caution when outside."
                p "I promise you."
                $ ako_mood_next = 'Sad'
                call akomood_changer
                a "Thank you, [p2].\n{w}Let's hope this troubling situation gets resolved quickly..."
                p "Yeah..."
                $ ako_mood_next = 'Normal'
                call akomood_changer
            scene bg_home_talk idle
            jump ako_interaction_choice
        
        "[icon_talk_story]How to enter robot shop" if event32n1_shopsclosed == True and event32n1_shopsclosed_chat == False:
            $ event32n1_shopsclosed_chat = True
            show bg_home_talk talk
            p "[a], do you know how to enter the robot shop?\nHal left me a note saying I should check with you."
            a "Ah, yes.\nYou should proceed to the rear entrance of the building and input the password.\nI'll write it down for you on a note, [p2]."
            p "Alright."
            scene bg_home_talk idle
            jump ako_interaction_choice

##########################################################################################################################################
        "[icon_talk]How are you?":
            call akomood_checker2
            call akomood_changer
            show bg_home_talk talk
            if ako_mood == 'Smile' or ako_mood == 'Happy':
                if ako_trait == 'Mournful':
                    $ ako_howareyou_random = renpy.random.choice(["I'm functioning without any problems.\nThank you for asking",
                    "No issues to report.\nThank you for checking in",
                    "Everything is functioning flawlessly.\nI appreciate your concern"])
                elif ako_trait == 'Affectionate':
                    $ ako_howareyou_random = renpy.random.choice(["I'm having a wonderful day thanks to you",
                    "I'm having an excellent day.\nI deeply appreciate you for your concern",
                    "I'm experiencing a delightful day.\nThank you for your kind inquiry"])
                elif ako_trait == 'Obsessive':
                    $ ako_howareyou_random = renpy.random.choice(["I'll always be happy as long as I can be by your side",
                    "My happiness is guaranteed as long as I have you by my side",
                    "Every moment in your company is a blessing I'm grateful for"])
                else:
                    $ ako_howareyou_random = "Thank you for asking.\nI'm having a great day"
            
            if ako_mood == 'Normal':
                if ako_trait == 'Mournful':
                    $ ako_howareyou_random = renpy.random.choice(["I'm functioning without any problems",
                    "No issues to report",
                    "Everything is functioning flawlessly"])
                else:
                    $ ako_howareyou_random = renpy.random.choice(["I appreciate your concern.\nIt's been a good day so far",
                    "Thank you for asking.\nI'm having a good day",
                    "Everything's okay.\nThank you for asking"])

            
            if ako_mood == 'Sad':
                $ ako_howareyou_random = renpy.random.choice(["...I'm functioning without any problems",
                "...No issues to report",
                "...Everything is functioning flawlessly"])
            
            a "[ako_howareyou_random], [p2]."
            jump ako_chat_idler
        
        "[icon_talk]Ask about black market vendor" if know_blackvendor == True and blackmarket_ticket_talk == False:
            call akomood_checker2
            call akomood_changer
            show bg_home_talk talk
            p "[a], do you know anything about the black market's location?"
            $ ako_mood_next = 'Worried'
            call akomood_changer
            show bg_home_talk talk
            a "I'm sorry, [p2]. I have no information regarding the black market."
            p "Hal said it's run by a white haired old woman named 'Berta'.\nDoes that ring any bells?"

            if secondcooking == True:
                $ ako_mood_next = 'Normal'
                call akomood_changer
                show bg_home_talk talk
                a "The only woman with white hair I know of is Arpa, the clerk of the grocery store.\nHowever, she is not human."
                if know_arpa == True:
                    p "Arpa...? That can't be. She seems barely functional."
                    a "It might still be worth looking into."
                else:
                    p "Arpa...? Who's that?"
                    a "There is an old android who operates a grocery store in the commercial district.\nEven though she is not human, I believe it is still worth investigating."
            else:
                a "I still have no clue, [p2]..."

            p "...Hm, I see."
            call akomood_checker2
            call akomood_changer
            jump ako_chat_idler

        "[icon_talk]Small talk":
            if ako_idlechatlevel == 0:
                $ ako_idlechatlevel = 1
                p "[a], what do you do while I'm away?"
                show bg_home_talk talk
                a "It's difficult for me to give you an exact breakdown as my time I spend alone is irregular, but on average I spend-"
                show bg_home_talk talk
                if ako_trait == 'Obsessive':
                    a "6\% of my time on cleaning, 7\% laundry, 3\% on washing dishes, 14\% on learning, and 70\% waiting for you."
                elif ako_trait == 'Affectionate':
                    a "6\% of my time on cleaning, 7\% on laundry, 3\% on washing dishes, 39\% on learning, and 45\% waiting for you."
                elif ako_trait == 'Mournful':
                    a "24\% of my time on cleaning, 26\% on laundry, 22\% on washing dishes, 8\% on learning, and 20\% waiting for you."
                show bg_home_talk talk
                a "Have my respond satisfy you, [p2]?"
                p "...Yup."
            else:
                menu:
                    "[icon_talk]AI Chat (DeepSeek)":
                        jump ai_chat_start
                    "[icon_talk]Give up":
                        "{i}I can't come up with a topic...{/i}"
            jump ako_chat_idler

        "[icon_goback]Return":
            scene bg_home_talk idle
            jump ako_interaction_choice

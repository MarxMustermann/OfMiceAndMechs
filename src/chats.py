####################################################################################################################
###
##    chats and chat realated code belongs here
#     bad pattern: chats should have a parent class
#
####################################################################################################################

# import the other internal libs
import src.interaction

'''
the main class for chats
'''
class Chat(src.interaction.SubMenu):

   def removeFromChatOptions(self,character):
        # find self in the characters chat options
        toRemove = None
        for item in character.basicChatOptions:

            # handle class notation
            if not isinstance(item,dict):
                if item == type(self):
                    toRemove = item
                    break

            # handle dictionary notation
            else:
                if item["chat"] == type(self):
                    toRemove = item
                    break

        # actually remove the chat
        if toRemove:
            character.basicChatOptions.remove(toRemove)
        else:
            debugMessages.append("removed chat option that wasn't there")

'''
the chat for collecting the reward
'''
class RewardChat(Chat):
    id = "RewardChat"

    '''
    call superclass with less params
    '''
    def __init__(subSelf,partner):
        super().__init__()
             
    '''
    call the solver to assign reward
    '''
    def handleKey(self, key):
        self.persistentText = "here is your reward"
        self.set_text(self.persistentText)
        
        # bad code: calling solver directly seems like a bad idea
        self.quest.getQuest.solver(self.character)

        # bad code: this is propably needed but this comes out of nowhere
        if self.quest.moveQuest:
            self.quest.moveQuest.postHandler()

        self.done = True
        return True

    '''
    add internal state
    bad pattern: chat option stored as references to class complicates this
    '''
    def setUp(self,state):
        self.quest = state["quest"]
        self.character = state["character"]

'''
the chat to proof the player is able to chat
bad code: story specific
'''
class TutorialSpeechTest(Chat):
    id = "TutorialSpeechTest"
    type = "TutorialSpeechTest"

    '''
    straightforward state setting
    '''
    def __init__(self,partner):
        self.done = False
        self.persistentText = ""
        self.firstRun = True
        super().__init__()

    '''
    add internal state
    bad pattern: chat option stored as references to class complicates this
    '''
    def setUp(self,state):
        self.firstOfficer = state["firstOfficer"]
        self.phase = state["phase"]

    '''
    show the dialog for one keystroke
    '''
    def handleKey(self, key):
        # do all activity on the first run
        if self.firstRun:
            # show fluffed up information
            self.persistentText = "indeed.\n\nI am "+self.firstOfficer.name+" and do the acceptance tests. This means i order you to do some things and you will comply.\n\nYour implant will store the orders given. When you press q you will get a list of your current orders. Try to get familiar with the implant,\nit is an important tool for keeping things in order.\n\nDo not mind that the tests seem somewhat without purpose, protocol demands them and after you complete the test you will serve as an hooper on the Falkenbaum."
            messages.append("press q to see your questlist")
            src.interaction.submenue = None
            self.set_text(self.persistentText)

            # remove chat option
            # bad code: this removal results in bugs if chats of the same type exist
            # bad pattern: chat option stored as references to class complicates this
            for item in self.firstOfficer.basicChatOptions:

                # check class notation
                if not isinstance(item,dict):
                    if item == TutorialSpeechTest:
                        toRemove = item
                        break

                # check dictionary notation
                else:
                    if item["chat"] == TutorialSpeechTest:
                        toRemove = item
                        break
            # remove item
            self.firstOfficer.basicChatOptions.remove(toRemove)

            # trigger further action
            self.phase.examineStuff()

            return False

        # finish Chat
        else:
            self.done = True
            return True

'''
dialog to unlock a furnace firering option
'''
class FurnaceChat(Chat):
    id = "FurnaceChat"
    type = "FurnaceChat"

    '''
    straightforward state setting
    '''
    def __init__(self,partner):
        self.state = None
        self.partner = partner
        self.firstRun = True
        self.done = False
        self.persistentText = ""
        self.submenue = None
        super().__init__()

    '''
    add internal state
    bad pattern: chat option stored as references to class complicates this
    '''
    def setUp(self,state):
        self.firstOfficer = state["firstOfficer"]
        self.terrain = state["terrain"]
        self.phase = state["phase"]

    '''
    offer the player a option to go deeper
    '''
    def handleKey(self, key):

        # set up the chat
        if self.firstRun:

            # show information
            self.persistentText = ["There are some growth tanks (",displayChars.indexedMapping[displayChars.growthTank_filled],"/",displayChars.indexedMapping[displayChars.growthTank_unfilled],"), walls (",displayChars.indexedMapping[displayChars.wall],"), a pile of coal (",displayChars.indexedMapping[displayChars.pile],") and a furnace (",displayChars.indexedMapping[displayChars.furnace_inactive],"/",displayChars.indexedMapping[displayChars.furnace_active],")."]
            self.set_text(self.persistentText)

            # add new chat option
            self.firstOfficer.basicChatOptions.append({"dialogName":"Is there more i should know?","chat":InfoChat,"params":{"firstOfficer":self.firstOfficer}})
                        
            # offer a selection of different story phasses
            options = [(self.phase.fireFurnaces,"yes"),(self.phase.noFurnaceFirering,"no")]
            self.submenue = src.interaction.SelectionMenu("Say, do you like furnaces?",options)
            self.firstRun = False
            return False

        if self.submenue:
            # try to let the selection option handle the keystroke
            if not self.submenue.handleKey(key):
                return False

            # tear down the submenue
            else:
                self.done = True

                # remove chat option
                self.removeFromChatOptions(self.firstOfficer)
             
                # clear submenue
                # bad code: direct state setting
                src.interaction.submenue = None
                src.interaction.loop.set_alarm_in(0.0, callShow_or_exit, '~')

                # do the selected action
                self.submenue.selection()
                return True

        return False

'''
a monologe explaining automovement
bad code: should be abstracted
'''
class SternChat(Chat):
    id = "SternChat"
    type = "SternChat"

    '''
    straight forward state setting
    '''
    def __init__(self,partner):
        self.submenue = None
        self.firstRun = True
        self.done = False
        super().__init__()

    '''
    add internal state
    bad pattern: chat option stored as references to class complicates this
    '''
    def setUp(self,state):
        self.firstOfficer = state["firstOfficer"]

    '''
    show the dialog for one keystroke
    '''
    def handleKey(self, key):
        # show information on first run
        if self.firstRun:
            # show fluffed up information
            self.persistentText = """Stern did not actually modify the implant. The modification was done elsewhere.
But that is concerning the artworks, thats nothing you need to know.

You need to know however that Sterns modification enhanced the implants guidance, control and communication abilities.
If you stop thinking and allow the implant to take control, it will do so and continue your task.
You can do so by pressing """+commandChars.autoAdvance+"""

It is of limited practability though. It is mainly useful for stupid manual labor and often does not 
do things the most efficent way. It will even try to handle conversion, wich does not allways lead to optimal results"""
            messages.append("press "+commandChars.autoAdvance+" to let the implant take control ")
            self.set_text(self.persistentText)
            self.firstRun = False

            # punish / reward player
            if mainChar.reputation:
                mainChar.reputation = mainChar.reputation//2+2
            else:
                mainChar.reputation += 2
            return False
        
        # tear down on second run
        else:
            # remove chat option
            self.removeFromChatOptions(self.firstOfficer)
            self.removeFromChatOptions(terrain.waitingRoom.firstOfficer)

            # finish
            self.done = True
            return True

'''
an instruction to ask questions and hinting at the auto mode
bad code: should be abstracted
'''
class InfoChat(Chat):
    id = "InfoChat"
    type = "InfoChat"

    '''
    straight forward state setting
    '''
    def __init__(self,partner):
        self.submenue = None
        self.firstRun = True
        self.done = False
        super().__init__()

    '''
    add internal state
    bad pattern: chat option stored as references to class complicates this
    '''
    def setUp(self,state):
        self.firstOfficer = state["firstOfficer"]

    '''
    show the dialog for one keystroke
    '''
    def handleKey(self, key):
        # do all activity on first run
        if self.firstRun:
            # show fluffed up information
            self.persistentText = """yes and a lot of it. I will give you two of these things on your way:\n
1. You will need to pick up most of the Information along the way. Ask around and talk to people.
Asking questions may hurt your reputation, since you will apear like new growth. 
You are, so do not heasitate to learn the neccesary Information before you have a reputation to loose.\n
2. Do not rely on the implant to guide you through dificult tasks. 
Sterns modifications are doing a good job for repetitive tasks but are no replacement
for a brain.\n\n"""
            self.set_text(self.persistentText)
            self.firstRun = False

            # punish / reward player
            if mainChar.reputation:
                mainChar.reputation = mainChar.reputation//2+2
            else:
                mainChar.reputation += 2
            return False

        # tear down on second run
        else:
            # remove chat option
            self.removeFromChatOptions(self.firstOfficer)

            # add follow up chat
            self.firstOfficer.basicChatOptions.append({"dialogName":"What did Stern modify on the implant?","chat":SternChat,"params":{"firstOfficer":self.firstOfficer}})
            terrain.waitingRoom.firstOfficer.basicChatOptions.append({"dialogName":"What did Stern modify on the implant?","chat":SternChat,"params":{"firstOfficer":self.firstOfficer}})

            self.done = True
            return True

'''
a dialog for reentering the command chain
bad code: story specific
'''
class ReReport(src.interaction.SubMenu):
    id = "ReReport"
    type = "ReReport"

    '''
    state initialization
    '''
    def __init__(self,partner):
        self.persistentText = ""
        self.firstRun = True
        super().__init__()

    '''
    add internal state
    bad pattern: chat option stored as references to class complicates this
    '''
    def setUp(self,state):
        self.phase = state["phase"]

    '''
    scold the player and start intro
    '''
    def handleKey(self, key):
        if self.firstRun:
            # show message
            self.persistentText = "It seems you did not report for duty immediately. Try to not repeat that"
            self.set_text(self.persistentText)
            self.done = True
            self.firstRun = False

            # punish player
            mainChar.reputation -= 1
            messages.append("rewarded -1 reputation")

            # remove chat option
            self.removeFromChatOptions(terrain.waitingRoom.firstOfficer)

            # start intro
            self.phase.getIntro()
            return True
        else:
            return False

'''
the dialog for asking somebody somewhat important for a job
'''
class JobChatFirst(Chat):
    id = "JobChatFirst"
    type = "JobChatFirst"

    '''
    add internal state
    bad pattern: chat option stored as references to class complicates this
    '''
    def setUp(self,state):
        self.mainChar = state["mainChar"]
        self.terrain = state["terrain"]
        self.hopperDutyQuest = state["hopperDutyQuest"]

    '''
    basic state initialization
    '''
    def __init__(subSelf,partner):
        subSelf.state = None
        subSelf.partner = partner
        subSelf.firstRun = True
        subSelf.done = False
        subSelf.persistentText = ""
        subSelf.dispatchedPhase = False
        subSelf.selectedQuest = None
        super().__init__()

    '''
    show dialog and assign quest 
    '''
    def handleKey(subSelf, key):
        # handle chat termination
        if key == "esc":

           # quit dialog
           if self.partner.reputation < 2*mainChar.reputation:
               return True

           # refuse to quit dialog
           else:
               self.persistentText = self.partner.name+": \""+mainChar.name+" improper termination of conversion is not compliant with the communication protocol IV. \nProper behaviour is expected.\"\n"
               mainChar.reputation -= 2
               messages.append("you were rewarded -2 reputation")
               main.set_text((urwid.AttrSpec("default","default"),self.persistentText))
               self.skipTurn = True
               return False
                             
        # handle chat termination
        if subSelf.firstRun:
            # job
            if not subSelf.dispatchedPhase:

                # do not assign job
                if subSelf.mainChar.reputation < 10:
                    subSelf.persistentText = "I have some work thats needs to be done, but you will have to proof your worth some more untill you can be trusted with this work.\n\nMaybe "+subSelf.terrain.waitingRoom.secondOfficer.name+" has some work you can do"

                # do not assign job
                elif not subSelf.hopperDutyQuest.active:
                    subSelf.persistentText = "your sesponsibilities are elsewhere"

                # do not assign job
                elif not "FireFurnaceMeta" in subSelf.mainChar.questsDone: # bad code: is bugged
                    subSelf.persistentText = "Several Officers requested new assistants. The boiler room would be the first target, but you need to have fired a furnace or you cannot take the job"

                # assign job
                else:
                    # show fluff
                    subSelf.persistentText = "Several Officers requested new assistants. First go to to the boiler room and apply for the position"

                    # start next story phase
                    quest = quests.MoveQuestMeta(subSelf.terrain.tutorialMachineRoom,3,3,creator=void)
                    phase = story.BoilerRoomWelcome()
                    quest.endTrigger = {"container":phase,"method":"start"}
                    subSelf.hopperDutyQuest.deactivate()
                    subSelf.mainChar.quests.remove(subSelf.hopperDutyQuest)
                    subSelf.mainChar.assignQuest(quest,active=True)
                    subSelf.dispatchedPhase = True

            # do not assign job
            else:
                subSelf.persistentText = "Not right now"

            # show text
            subSelf.set_text(subSelf.persistentText)
            subSelf.done = True
            subSelf.firstRun = False

            return True
        else:
            return False

'''
the dialog for asking somebody for a job
'''
class JobChatSecond(Chat):
    id = "JobChatSecond"
    type = "JobChatSecond"

    '''
    basic state initialization
    '''
    def __init__(self,partner):
        self.state = None
        self.partner = partner
        self.firstRun = True
        self.done = False
        self.persistentText = ""
        self.submenue = None
        self.selectedQuest = None
        super().__init__()

    '''
    add internal state
    bad pattern: chat option stored as references to class complicates this
    '''
    def setUp(self,state):
        self.mainChar = state["mainChar"]
        self.terrain = state["terrain"]
        self.hopperDutyQuest = state["hopperDutyQuest"]

    '''
    show dialog and assign quest 
    '''
    def handleKey(self, key):
        # handle termination of this chat
        if key == "esc":
           # quit dialog
           if self.partner.reputation < 2*mainChar.reputation:
               return True
           # refuse to quit dialog
           else:
               self.persistentText = self.partner.name+": \""+mainChar.name+" improper termination of conversion is not compliant with the communication protocol IV. \nProper behaviour is expected.\"\n"
               mainChar.reputation -= 2
               messages.append("you were rewarded -2 reputation")
               main.set_text((urwid.AttrSpec("default","default"),self.persistentText))
               self.skipTurn = True
               return False
                             
        # let the superclass do the selection
        if self.submenue:
            if not self.submenue.handleKey(key):
                return False
            else:
                self.selectedQuest = self.submenue.selection
                self.submenue = None

            self.firstRun = False

        # refuse to issue new quest if the old one is not done yet
        # bad code: this is because the hopperquest cannot handle multiple sub quests
        if not self.hopperDutyQuest.getQuest:
            self.persistentText = "please finish what you are dooing first"
            self.set_text(self.persistentText)
            self.done = True

            return True

        # assign the selected quest
        if self.selectedQuest:
            self.hopperDutyQuest.getQuest.getQuest.quest = self.selectedQuest
            self.hopperDutyQuest.getQuest.getQuest.recalculate()
            if self.hopperDutyQuest.getQuest:
                self.hopperDutyQuest.getQuest.recalculate()
            self.terrain.waitingRoom.quests.remove(self.selectedQuest)
            self.done = True
            return True

        # refuse to give two quests
        if self.hopperDutyQuest.actualQuest:
            # bad pattern: should be proportional to current reputation
            self.persistentText = "you already have a quest. Complete it and you can get a new one."
            self.set_text(self.persistentText)
            self.done = True

            return True

        # offer list of quests to the player
        if self.terrain.waitingRoom.quests:
            # show fluff
            self.persistentText = "Well, yes."
            self.set_text(self.persistentText)
                        
            # let the player select the quest to do
            options = []
            for quest in self.terrain.waitingRoom.quests:
                addition = ""
                if self.mainChar.reputation < 6:
                    addition += " ("+str(quest.reputationReward)+")"
                options.append((quest,quest.description.split("\n")[0]+addition))
            self.submenue = src.interaction.SelectionMenu("select the quest",options)

            return False
        
        # refuse to give quests
        self.persistentText = "Not right now. Ask again later"
        self.set_text(self.persistentText)
        self.done = True

        return True

'''
the chat for making the npc stop firing the furnace
'''
class StopChat(Chat):
    id = "StopChat"
    type = "StopChat"

    '''
    basic state initialization
    '''
    def __init__(self,partner):
        self.state = None
        self.partner = partner
        self.firstRun = True
        self.done = False
        self.persistentText = ""
        super().__init__()

    '''
    stop furnace quest and correct dialog
    '''
    def handleKey(self, key):
        # show information on first run
        if self.firstRun:
            # stop firing the furnace
            self.persistentText = "OK, stopping now"
            self.set_text(self.persistentText)
            self.done = True
            global quest
            quest.deactivate()

            # replace dialog option
            for option in self.partner.basicChatOptions:
                 if not option["chat"] == StopChat:
                     continue
                 self.partner.basicChatOptions.remove(option)
                 break
            self.partner.basicChatOptions.append({"dialogName":"fire the furnaces","chat":StartChat})

            self.firstRun = False

            return True
        # do nothing on later runs
        else:
            return False

'''
the chat for making the npc start firering the furnace
'''
class StartChat(Chat):
    id = "StartChat"
    type = "StartChat"

    '''
    basic state initialization
    '''
    def __init__(self,partner):
        self.state = None
        self.partner = partner
        self.firstRun = True
        self.done = False
        self.persistentText = ""
        super().__init__()

    '''
    start furnace quest and correct dialog
    '''
    def handleKey(self, key):
        # show information on first run
        if self.firstRun:

            # start firing the furnace
            self.persistentText = "Starting now. The engines should be running in a few ticks"
            self.set_text(self.persistentText)
            self.done = True
            global quest
            quest = quests.KeepFurnaceFiredMeta(self.partner.room.furnaces[0],creator=void)
            self.partner.assignQuest(quest,active=True)

            # replace dialog option
            for option in self.partner.basicChatOptions:
                 if not option["chat"] == StartChat:
                     continue
                 self.partner.basicChatOptions.remove(option)
                 break
            self.partner.basicChatOptions.append({"dialogName":"stop fireing the furnaces","chat":StopChat})

            self.firstRun = False

            return True
        # do nothing on later runs
        else:
            return False

'''
the chat option for recruiting a character
'''
class RecruitChat(Chat):
    dialogName = "follow my orders." # the name for this chat when presented as dialog option

    '''
    straightforward state initialization
    '''
    def __init__(self,partner):
        self.type = "RecruitChat"
        self.state = None
        self.partner = partner
        self.firstRun = True
        self.done = False
        self.persistentText = ""
        super().__init__()

    '''
    show dialog and recruit character depending on success
    bad code: showing the messages should be handled in __init__ or a setup method
    bad code: the dialog and reactions should be generated within the characters
    '''
    def handleKey(self, key):
        # exit submenu
        if key == "esc":
            return True

        # show dialog
        if self.firstRun:

            # add player text
            self.persistentText += mainChar.name+": \"come and help me.\"\n"

            # reject player request
            if self.partner.reputation > mainChar.reputation:
                if mainChar.reputation <= 0:
                    # reject player very harshly
                    self.persistentText += self.partner.name+": \"No.\""
                    mainChar.reputation -= 5
                    messages.append("You were rewarded -5 reputation")
                else:
                    # reject player harshly
                    if self.partner.reputation//mainChar.reputation:
                        self.persistentText += self.partner.name+": \"you will need at least have to have "+str(self.partner.reputation//mainChar.reputation)+" times as much reputation to have me consider that\"\n"
                        messages.append("You were rewarded -"+str(2*(self.partner.reputation//mainChar.reputation))+" reputation")
                        mainChar.reputation -= 2*(self.partner.reputation//mainChar.reputation)
                    # reject player somewhat nicely
                    else:
                        self.persistentText += self.partner.name+": \"maybe if you come back later\""
                        mainChar.reputation -= 2
                        messages.append("You were rewarded -2 reputation")
            # consider player request
            else:

                # reject player
                if gamestate.tick%2:
                    self.persistentText += self.partner.name+": \"sorry, too busy.\"\n"
                    mainChar.reputation -= 1
                    messages.append("You were rewarded -1 reputation")

                # allow the recruitment
                else:
                    self.persistentText += self.partner.name+": \"on it!\"\n"
                    mainChar.subordinates.append(self.partner)

            # show dialog
            text = self.persistentText+"\n\n-- press any key --"
            main.set_text((urwid.AttrSpec("default","default"),text))
            self.firstRun = False
            return True
        # continue after the first keypress
        # bad code: the first keystroke is the second keystroke that is handled
        else:
            self.done = True
            return False

'''
a chat with a character, partially hardcoded partially dynamically generated 
'''
class ChatMenu(Chat):

    '''
    straightforward state initialization
    '''
    def __init__(self,partner=None):
        self.type = "ChatMenu"
        self.state = None
        self.partner = partner
        self.subMenu = None
        self.skipTurn = False
        super().__init__()
        self.objectsToStore.append("partner")

    '''
    get state as dictionary
    '''
    def getState(self):
        state = super().getState()
        if self.subMenu:
            state["subMenu"] = self.subMenu.getState()
        else:
            state["subMenu"] = None

        return state
    
    '''
    set internal state from state as dictionary
    '''
    def setState(self,state):
        super().setState(state)

        if "subMenu" in state:
            if state["subMenu"]:
                self.subMenu = getSubmenuFromState(state["subMenu"])
            else:
                self.subMenu = None

    '''
    show the dialog options and wrap around the corresponding submenus
    bad code: showing the messages should be handled in __init__ or a setup method
    bad code: the dialog should be generated within the characters
    '''
    def handleKey(self, key):
        # smooth over impossible state
        if self.partner == None:
           debugMessages.append("chatmenu spawned without partner")
           return False

        # wake up character instead of speaking
        if self.partner.unconcious:
            messages.append("wake up!")
            self.partner.wakeUp()
            return True

        # maybe exit the submenu
        if key == "esc":
           # abort the chat
           if self.partner.reputation < 2*mainChar.reputation:
               return True
           # refuse to abort the chat
           else:
               self.persistentText = self.partner.name+": \""+mainChar.name+" improper termination of conversion is not compliant with the communication protocol IV. \nProper behaviour is expected.\"\n"
               mainChar.reputation -= 1
               messages.append("you were rewarded -1 reputation")
               main.set_text((urwid.AttrSpec("default","default"),self.persistentText))
               self.skipTurn = True
               return False
                             
        # skip a turn
        if self.skipTurn:
           self.skipTurn = False
           key = "."

        # show interaction
        header.set_text((urwid.AttrSpec("default","default"),"\nConversation menu\n"))
        out = "\n"

        # wrap around chat submenue
        if self.subMenu:
            # let the submenue handle the key
            if not self.subMenu.done:
                self.subMenu.handleKey(key)
                if not self.subMenu.done:
                    return False

            # return to main dialog menu
            self.subMenu = None
            self.state = "mainOptions"
            self.selection = None
            self.lockOptions = True
            self.chatOptions = []

        # display greetings
        if self.state == None:
            self.state = "mainOptions"
            self.persistentText += self.partner.name+": \"Everything in Order, "+mainChar.name+"?\"\n"
            self.persistentText += mainChar.name+": \"All sorted, "+self.partner.name+"!\"\n"

        # show selection of sub chats
        if self.state == "mainOptions":
            # set up selection for the main dialog options 
            if not self.options and not self.getSelection():
                # add the chat partners special dialog options
                options = []
                for option in self.partner.getChatOptions(mainChar):
                    if not isinstance(option,dict):
                        options.append((option,option.dialogName))
                    else:
                        options.append((option,option["dialogName"]))

                # add default dialog options
                options.append(("showQuests","what are you dooing?"))
                options.append(("exit","let us proceed, "+self.partner.name))

                # set the options
                self.setOptions("answer:",options)

            # let the superclass handle the actual selection
            if not self.getSelection():
                super().handleKey(key)

            # spawn the dialog options submenu
            if self.getSelection():
                if not isinstance(self.selection,str):
                    # spawn the selected dialog option
                    if not isinstance(self.selection,dict):
                        self.subMenu = self.selection(self.partner)
                    else:
                        self.subMenu = self.selection["chat"](self.partner)
                        if "params" in self.selection:
                            self.subMenu.setUp(self.selection["params"])

                    self.subMenu.handleKey(key)
                elif self.selection == "showQuests":
                    # spawn quest submenu for partner
                    global submenue
                    submenue = QuestMenu(char=self.partner)
                    submenue.handleKey(key)
                    return False
                elif self.selection == "exit":
                    # end the conversation
                    self.state = "done"
                self.selection = None
                self.lockOptions = True
            else:
                return False

        # say goodbye
        if self.state == "done":
            if self.lockOptions:
                self.persistentText += self.partner.name+": \"let us proceed, "+mainChar.name+".\"\n"
                self.persistentText += mainChar.name+": \"let us proceed, "+self.partner.name+".\"\n"
                self.lockOptions = False
            else:
                return True

        # show redered text via urwid
        # bad code: urwid code should be somewere else
        if not self.subMenu:
            main.set_text((urwid.AttrSpec("default","default"),self.persistentText))

        return False

# a map alowing to get classes from strings
chatMap = {
             "TutorialSpeechTest":TutorialSpeechTest,
             "FurnaceChat":FurnaceChat,
             "SternChat":SternChat,
             "StartChat":StartChat,
             "StopChat":StopChat,
             "InfoChat":InfoChat,
             "ReReport":ReReport,
             "JobChatFirst":JobChatFirst,
             "JobChatSecond":JobChatSecond,
             "RewardChat":RewardChat,
			 "RecruitChat":RecruitChat,
			 "ChatMenu":ChatMenu,
          }

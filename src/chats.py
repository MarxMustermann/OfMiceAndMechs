import src.interaction as interaction

# bad pattern: chats should have a parent class

'''
the chat to proof the player is able to chat
bad code: story specific
'''
class FirstChat(interaction.SubMenu):
    id = "FirstChat"
    type = "FirstChat"

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
        if self.firstRun:
            # show fluffed up information
            self.persistentText = "indeed.\n\nI am "+self.firstOfficer.name+" and do the acceptance tests. This means i order you to do some things and you will comply.\n\nYour implant will store the orders given. When you press q you will get a list of your current orders. Try to get familiar with the implant,\nit is an important tool for keeping things in order.\n\nDo not mind that the tests seem somewhat without purpose, protocol demands them and after you complete the test you will serve as an hooper on the Falkenbaum."
            messages.append("press q to see your questlist")
            interaction.submenue = None
            self.set_text(self.persistentText)

            # remove chat option
            # bad code: this removal results in bugs if to chats of the same type exist
            # bad pattern: chat option stored as references to class complicates this
            for item in self.firstOfficer.basicChatOptions:
                if not isinstance(item,dict):
                    if item == FirstChat:
                        toRemove = item
                        break
                else:
                    if item["chat"] == FirstChat:
                        toRemove = item
                        break
            self.firstOfficer.basicChatOptions.remove(toRemove)

            # trigger further action
            self.phase.examineStuff()
            return False
        else:
            # finish
            self.done = True
            return True

'''
dialog to unlock a furnace firering option
'''
class FurnaceChat(interaction.SubMenu):
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
        if self.submenue:
            if not self.submenue.handleKey(key):
                # let the selection option hande the keystroke
                return False
            else:
                self.done = True

                # remove self from the characters chat options
                for item in self.firstOfficer.basicChatOptions:
                    if not isinstance(item,dict):
                        if item == FurnaceChat:
                            toRemove = item
                            break
                    else:
                        if item["chat"] == FurnaceChat:
                            toRemove = item
                            break
                self.firstOfficer.basicChatOptions.remove(toRemove)
             
                # clear submenue
                # bad code: direct state setting
                interaction.submenue = None
                interaction.loop.set_alarm_in(0.0, callShow_or_exit, '~')

                # do the selected action
                self.submenue.selection()
                return True

        # do first part of the dialog
        if self.firstRun:
            # show information
            self.persistentText = ["There are some growth tanks (",displayChars.indexedMapping[displayChars.growthTank_filled],"/",displayChars.indexedMapping[displayChars.growthTank_unfilled],"), walls (",displayChars.indexedMapping[displayChars.wall],"), a pile of coal (",displayChars.indexedMapping[displayChars.pile],") and a furnace (",displayChars.indexedMapping[displayChars.furnace_inactive],"/",displayChars.indexedMapping[displayChars.furnace_active],")."]
            self.set_text(self.persistentText)

            # add new chat option
            self.firstOfficer.basicChatOptions.append({"dialogName":"Is there more i should know?","chat":InfoChat,"params":{"firstOfficer":self.firstOfficer}})
                        
            # offer a selection of different story phasses
            options = [(self.phase.fireFurnaces,"yes"),(self.phase.noFurnaceFirering,"no")]
            self.submenue = interaction.SelectionMenu("Say, do you like furnaces?",options)

        return False

'''
a monologe explaining automovement
'''
class SternChat(interaction.SubMenu):
    id = "SternChat"
    type = "SternChat"

    '''
    straight forwar state setting
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
            mainChar.reputation = mainChar.reputation//2+2
            return False
        else:
            # remove self from the characters chat options
            for item in self.firstOfficer.basicChatOptions:
                if not isinstance(item,dict):
                    if item == SternChat:
                        toRemove = item
                        break
                else:
                    if item["chat"] == SternChat:
                        toRemove = item
                        break
            # bad code: crashes
            self.firstOfficer.basicChatOptions.remove(toRemove)

            # finish
            self.done = True
            return True

'''
a instruction to ask questions and hinting at the auto mode
'''
class InfoChat(interaction.SubMenu):
    id = "InfoChat"
    type = "InfoChat"

    '''
    straight forwar state setting
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
            mainChar.reputation = mainChar.reputation//2+2
            return False
        else:
            # remove chat option
            for item in self.firstOfficer.basicChatOptions:
                if not isinstance(item,dict):
                    if item == InfoChat:
                        toRemove = item
                        break
                else:
                    if item["chat"] == InfoChat:
                        toRemove = item
                        break
            # bad code: crashes
            self.firstOfficer.basicChatOptions.remove(toRemove)

            # finish
            self.firstOfficer.basicChatOptions.append({"dialogName":"What did Stern modify on the implant?","chat":SternChat,"params":{"firstOfficer":self.firstOfficer}})
            self.done = True
            return True

'''
a dialog for reentering the command chain
'''
class ReReport(interaction.SubMenu):
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
    scold the player and start intro
    '''
    def handleKey(self, key):
        if self.firstRun:
            # show message
            self.persistentText = "It seems you did not report for duty imediatly. Try to not repeat that"
            self.set_text(self.persistentText)
            self.done = True
            self.firstRun = False

            # punish player
            mainChar.reputation -= 1
            messages.append("rewarded -1 reputation")

            # remove chat option
            for item in terrain.waitingRoom.firstOfficer.basicChatOptions:
                if not isinstance(item,dict):
                    if item == ReReport:
                        toRemove = item
                        break
                else:
                    if item["chat"] == ReReport:
                        toRemove = item
                        break
            # bad code: crashes
            terrain.waitingRoom.firstOfficer.basicChatOptions.remove(toRemove)

            # start intro
            # bad code: crashes
            self.getIntro()
            return True
        else:
            return False

'''
the dialog for asking somebody somewhat important for a job
bad code: nameing
'''
class JobChat(interaction.SubMenu):
    id = "JobChat"
    type = "JobChat"

    dialogName = "Can you use some help?"

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
        if key == "esc":
           if self.partner.reputation < 2*mainChar.reputation:
               return True
           else:
               self.persistentText = self.partner.name+": \""+mainChar.name+" improper termination of conversion is not compliant with the communication protocol IV. \nProper behaviour is expected.\"\n"
               mainChar.reputation -= 2
               messages.append("you were rewarded -2 reputation")
               main.set_text((urwid.AttrSpec("default","default"),self.persistentText))
               self.skipTurn = True
               return False
                             
        if subSelf.firstRun:
            if not subSelf.dispatchedPhase:
                if subSelf.mainChar.reputation < 10:
                    # deny the request
                    subSelf.persistentText = "I have some work thats needs to be done, but you will have to proof your worth some more untill you can be trusted with this work.\n\nMaybe "+subSelf.terrain.waitingRoom.secondOfficer.name+" has some work you can do"
                else:
                    # show fluff
                    subSelf.persistentText = "Several Officers requested new assistants. First go to to the boiler room and apply for the position"

                    # start next story phase
                    quest = quests.MoveQuestMeta(subSelf.terrain.tutorialMachineRoom,3,3,creator=void)
                    phase = story.FirstTutorialPhase()
                    quest.endTrigger = {"container":phase,"method":"start"}
                    subSelf.hopperDutyQuest.getQuest.quest = subSelf.selectedQuest
                    subSelf.hopperDutyQuest.getQuest.recalculate()
                    subSelf.dispatchedPhase = True
            else:
                # deny the request
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
bad code:
bad code: xxx2
'''
class JobChat2(interaction.SubMenu):
    id = "JobChat2"
    type = "JobChat2"
    dialogName = "Can you use some help?" # bad code: deprecated

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
        if key == "esc":
           if self.partner.reputation < 2*mainChar.reputation:
               return True
           else:
               self.persistentText = self.partner.name+": \""+mainChar.name+" improper termination of conversion is not compliant with the communication protocol IV. \nProper behaviour is expected.\"\n"
               mainChar.reputation -= 2
               messages.append("you were rewarded -2 reputation")
               main.set_text((urwid.AttrSpec("default","default"),self.persistentText))
               self.skipTurn = True
               return False
                             
        # let the superclass do the selections
        if self.submenue:
            if not self.submenue.handleKey(key):
                return False
            else:
                self.selectedQuest = self.submenue.selection
                self.submenue = None

            self.firstRun = False

        if not self.hopperDutyQuest.getQuest:
            self.persistentText = "please collect your reward first"
            self.set_text(self.persistentText)
            self.done = True

            return True

        if not self.selectedQuest:
            if self.hopperDutyQuest.actualQuest:
                # refuse to give two quests
                self.persistentText = "you already have a quest. Complete it and you can get a new one."
                self.set_text(self.persistentText)
                self.done = True

                return True
            elif self.terrain.waitingRoom.quests:
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
                self.submenue = interaction.SelectionMenu("select the quest",options)

                return False
            else:
                # refuse to give quests
                self.persistentText = "Not right now. Ask again later"
                self.set_text(self.persistentText)
                self.done = True

                return True
        else:
            # assign the selected quest
            self.hopperDutyQuest.getQuest.getQuest.quest = self.selectedQuest
            self.hopperDutyQuest.getQuest.getQuest.recalculate()
            if self.hopperDutyQuest.getQuest:
                self.hopperDutyQuest.getQuest.recalculate()
            self.terrain.waitingRoom.quests.remove(self.selectedQuest)
            self.done = True
            return True


chatMap = {
             "FirstChat":FirstChat,
             "FurnaceChat":FurnaceChat,
             "SternChat":SternChat,
             "InfoChat":InfoChat,
             "ReReport":ReReport,
             "JobChat":JobChat,
             "JobChat2":JobChat2,
          }

import src.interaction as interaction

# bad pattern: chats should have a parent class

'''
the chat to proof the player is able to chat
bad code: story specific
'''
class FirstChat(interaction.SubMenu):
    id = "FirstChat"
    type = "FirstChat"

    dialogName = "You wanted to have a chat" # bad code: deprecated, remove

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

    dialogName = "What are these machines in this room?" # bad code: deprecated, remove

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

                # remove self from the chracters chat
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
            self.firstOfficer.basicChatOptions.append(InfoChat)
                        
            # offer a selection of different story phasses
            options = {}
            niceOptions = {}
            counter = 1
            for quest in self.terrain.waitingRoom.quests:
                options[str(counter)] = quest
                niceOptions[str(counter)] = quest.description.split("\n")[0]
                counter += 1
            options = {1:self.phase.fireFurnaces,2:self.phase.noFurnaceFirering}
            niceOptions = {1:"Yes",2:"No"}
            self.submenue = interaction.SelectionMenu("Say, do you like furnaces?",options,niceOptions)

        return False

'''
a monologe explaining automovement
'''
class SternChat(interaction.SubMenu):
    id = "SternChat"
    type = "SternChat"

    dialogName = "What did Stern modify on the implant?" # bad code: deprecated, remove

    '''
    straight forwar state setting
    '''
    def __init__(self,partner):
        self.submenue = None
        self.firstRun = True
        self.done = False
        super().__init__()

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
            return False
        else:
            # remove chat option and finish
            # bad code: crashes
            firstOfficer.basicChatOptions.remove(SternChat)
            self.done = True
            return True

'''
a instruction to ask questions and hinting at the auto mode
'''
class InfoChat(interaction.SubMenu):
    id = "InfoChat"
    type = "InfoChat"

    dialogName = "Is there more i should know?" # bad code: deprecated, remove

    '''
    straight forwar state setting
    '''
    def __init__(self,partner):
        self.submenue = None
        self.firstRun = True
        self.done = False
        super().__init__()

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
            return False
        else:
            # remove chat option and finish
            # bad code: crashes
            firstOfficer.basicChatOptions.remove(InfoChat)
            firstOfficer.basicChatOptions.append(SternChat)
            self.done = True
            return True

'''
a dialog for reentering the command chain
'''
class ReReport(interaction.SubMenu):
    id = "ReReport"
    type = "ReReport"

    dialogName = "I want to report for duty" # bad code: deprecated, remove

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

            # remove dialog option
            terrain.waitingRoom.firstOfficer.basicChatOptions.remove(ReReport)

            # start intro
            # bad code: crashes
            self.getIntro()
            return True
        else:
            return False

chatMap = {
             "FirstChat":FirstChat,
             "FurnaceChat":FurnaceChat,
             "SternChat":SternChat,
             "InfoChat":InfoChat,
             "ReReport":ReReport,
          }

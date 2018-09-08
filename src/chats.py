import src.interaction as interaction

'''
the chat to proof the player is able to chat
'''
class FirstChat(interaction.SubMenu):
    id = "FirstChat"
    type = "FirstChat"

    dialogName = "You wanted to have a chat"

    '''
    straightforward state setting
    '''
    def __init__(subSelf,partner):
        subSelf.done = False
        subSelf.persistentText = ""
        subSelf.firstRun = True
        super().__init__()

    def setUp(self,state):
        self.firstOfficer = state["firstOfficer"]
        self.phase = state["phase"]

    '''
    show the dialog for one keystroke
    '''
    def handleKey(subSelf, key):
        if subSelf.firstRun:
            # show fluffed up information
            subSelf.persistentText = "indeed.\n\nI am "+subSelf.firstOfficer.name+" and do the acceptance tests. This means i order you to do some things and you will comply.\n\nYour implant will store the orders given. When you press q you will get a list of your current orders. Try to get familiar with the implant,\nit is an important tool for keeping things in order.\n\nDo not mind that the tests seem somewhat without purpose, protocol demands them and after you complete the test you will serve as an hooper on the Falkenbaum."
            messages.append("press q to see your questlist")
            interaction.submenue = None
            subSelf.set_text(subSelf.persistentText)

            # remove chat option
            for item in subSelf.firstOfficer.basicChatOptions:
                if not isinstance(item,dict):
                    if item == FirstChat:
                        toRemove = item
                        break
                else:
                    if item["chat"] == FirstChat:
                        toRemove = item
                        break
            subSelf.firstOfficer.basicChatOptions.remove(toRemove)

            # trigger further action
            subSelf.phase.examineStuff()
            return False
        else:
            # finish
            subSelf.done = True
            return True

'''
dialog to unlock a furnace firering option
'''
class FurnaceChat(interaction.SubMenu):
    id = "FurnaceChat"
    type = "FurnaceChat"

    dialogName = "What are these machines in this room?"

    '''
    straightforward state setting
    '''
    def __init__(subSelf,partner):
        subSelf.state = None
        subSelf.partner = partner
        subSelf.firstRun = True
        subSelf.done = False
        subSelf.persistentText = ""
        subSelf.submenue = None
        super().__init__()

    def setUp(self,state):
        self.firstOfficer = state["firstOfficer"]
        self.terrain = state["terrain"]
        self.phase = state["phase"]

    '''
    offer the player a option to go deeper
    '''
    def handleKey(subSelf, key):
        if subSelf.submenue:
            if not subSelf.submenue.handleKey(key):
                # let the selection option hande the keystroke
                return False
            else:
                subSelf.done = True

                # let the selection option hande the keystroke
                for item in subSelf.firstOfficer.basicChatOptions:
                    if not isinstance(item,dict):
                        if item == FurnaceChat:
                            toRemove = item
                            break
                    else:
                        if item["chat"] == FirstChat:
                            toRemove = item
                            break
                subSelf.firstOfficer.basicChatOptions.remove(toRemove)
             
                interaction.submenue = None
                interaction.loop.set_alarm_in(0.0, callShow_or_exit, '~')
                subSelf.submenue.selection()
                return True

        # do first part of the dialog
        if subSelf.firstRun:
            # show information
            subSelf.persistentText = ["There are some growth tanks (",displayChars.indexedMapping[displayChars.growthTank_filled],"/",displayChars.indexedMapping[displayChars.growthTank_unfilled],"), walls (",displayChars.indexedMapping[displayChars.wall],"), a pile of coal (",displayChars.indexedMapping[displayChars.pile],") and a furnace (",displayChars.indexedMapping[displayChars.furnace_inactive],"/",displayChars.indexedMapping[displayChars.furnace_active],")."]
            subSelf.set_text(subSelf.persistentText)

            # add new chat option
            subSelf.firstOfficer.basicChatOptions.append(InfoChat)
                        
            # set up the selection
            options = {}
            niceOptions = {}
            counter = 1
            for quest in subSelf.terrain.waitingRoom.quests:
                options[str(counter)] = quest
                niceOptions[str(counter)] = quest.description.split("\n")[0]
                counter += 1
            options = {1:subSelf.phase.fireFurnaces,2:subSelf.phase.noFurnaceFirering}
            niceOptions = {1:"Yes",2:"No"}
            subSelf.submenue = interaction.SelectionMenu("Say, do you like furnaces?",options,niceOptions)

        return False

'''
a monologe explaining automovement
'''
class SternChat(interaction.SubMenu):
    id = "SternChat"
    type = "SternChat"

    dialogName = "What did Stern modify on the implant?"

    '''
    straight forwar state setting
    '''
    def __init__(subSelf,partner):
        subSelf.submenue = None
        subSelf.firstRun = True
        subSelf.done = False
        super().__init__()

    '''
    show the dialog for one keystroke
    '''
    def handleKey(subSelf, key):
        if subSelf.firstRun:
            # show fluffed up information
            subSelf.persistentText = """Stern did not actually modify the implant. The modification was done elsewhere.
But that is concerning the artworks, thats nothing you need to know.

You need to know however that Sterns modification enhanced the implants guidance, control and communication abilities.
If you stop thinking and allow the implant to take control, it will do so and continue your task.
You can do so by pressing """+commandChars.autoAdvance+"""

It is of limited practability though. It is mainly useful for stupid manual labor and often does not 
do things the most efficent way. It will even try to handle conversion, wich does not allways lead to optimal results"""
            messages.append("press "+commandChars.autoAdvance+" to let the implant take control ")
            subSelf.set_text(subSelf.persistentText)
            subSelf.firstRun = False
            return False
        else:
            # remove chat option and finish
            firstOfficer.basicChatOptions.remove(SternChat)
            subSelf.done = True
            return True

'''
a instruction to ask questions and hinting at the auto mode
'''
class InfoChat(interaction.SubMenu):
    id = "InfoChat"
    type = "InfoChat"

    dialogName = "Is there more i should know?"

    '''
    straight forwar state setting
    '''
    def __init__(subSelf,partner):
        subSelf.submenue = None
        subSelf.firstRun = True
        subSelf.done = False
        super().__init__()

    '''
    show the dialog for one keystroke
    '''
    def handleKey(subSelf, key):
        if subSelf.firstRun:
            # show fluffed up information
            subSelf.persistentText = """yes and a lot of it. I will give you two of these things on your way:\n
1. You will need to pick up most of the Information along the way. Ask around and talk to people.
Asking questions may hurt your reputation, since you will apear like new growth. 
You are, so do not heasitate to learn the neccesary Information before you have a reputation to loose.\n
2. Do not rely on the implant to guide you through dificult tasks. 
Sterns modifications are doing a good job for repetitive tasks but are no replacement
for a brain.\n\n"""
            subSelf.set_text(subSelf.persistentText)
            subSelf.firstRun = False
            return False
        else:
            # remove chat option and finish
            firstOfficer.basicChatOptions.remove(InfoChat)
            firstOfficer.basicChatOptions.append(SternChat)
            subSelf.done = True
            return True

'''
a dialog for reentering the command chain
'''
class ReReport(interaction.SubMenu):
    id = "ReReport"
    type = "ReReport"

    dialogName = "I want to report for duty"

    '''
    state initialization
    '''
    def __init__(subSelf,partner):
        subSelf.persistentText = ""
        subSelf.firstRun = True
        super().__init__()

    '''
    scold the player and start intro
    '''
    def handleKey(subSelf, key):
        if subSelf.firstRun:
            # show message
            subSelf.persistentText = "It seems you did not report for duty imediatly. Try to not repeat that"
            subSelf.set_text(subSelf.persistentText)
            subSelf.done = True
            subSelf.firstRun = False

            # punish player
            mainChar.reputation -= 1
            messages.append("rewarded -1 reputation")

            # remove dialog option
            terrain.waitingRoom.firstOfficer.basicChatOptions.remove(ReReport)

            # start intro
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

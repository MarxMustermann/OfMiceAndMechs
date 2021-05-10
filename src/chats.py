####################################################################################################################
###
##    chats and chat realated code belongs here
#     bad pattern: chats should have a parent class
#
####################################################################################################################

urwid = None

# import the other internal libs
import src.interaction
import src.canvas
import src.logger
import src.quests
import config
import src.gamestate

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
            src.logger.debugMessages.append("removed chat option that wasn't there")

    def setUp(self,state):
        pass

class OneTimeMessage(Chat):
    id = "OneTimeMessage"

    '''
    '''
    def __init__(self,text=""):
        super().__init__()
        self.firstRun = True
        self.persistentText = text

    '''
    '''
    def handleKey(self, key, noRender=False):
        if self.firstRun:
            self.set_text(self.persistentText)
            self.done = False
            self.firstRun = False
            return False
        self.done = True
        return True

'''
the chat for getting a hopper duty intro
'''
class ConfigurableChat(Chat):
    id = "ConfigurableChat"

    '''
    '''
    def __init__(self,discardParam = None):
        super().__init__()
        self.subMenu = None
        self.allowExit = True

    '''
    '''
    def handleKey(self, key, noRender=False):
        if self.subMenu:
             if not self.subMenu.handleKey(key, noRender=noRender):
                 return False
             self.subMenu = None

        self.persistentText = self.text

        if not self.options and not self.getSelection():
            # add the chat partners special dialog options
            options = []
            for option in self.info:
                options.append((option,option["name"]))

            # add default dialog options
            if self.allowExit:
                options.append(("exit","let us proceed"))

            # set the options
            self.setOptions("answer:",options)

        # let the superclass handle the actual selection
        if not self.getSelection():
            super().handleKey(key, noRender=noRender)

        # spawn the dialog options submenu
        if self.getSelection():
            if self.selection == "exit":
                self.done = True
                return True

            if self.selection["type"] == "text":
                self.subMenu = OneTimeMessage(self.selection["text"])
                self.subMenu.handleKey("~", noRender=noRender)
            elif self.selection["type"] == "sub":
                self.subMenu = ConfigurableChat()
                self.subMenu.setUp({"text":self.selection["text"],"info":self.selection["sub"]})
                self.subMenu.handleKey("~", noRender=noRender)
            else:
                self.set_text("NIY")

            if "trigger" in self.selection and self.selection["trigger"]:
                self.callIndirect(self.selection["trigger"])
            if "follow" in self.selection:
                self.info.extend(self.selection["follow"])
            if "delete" in self.selection and self.selection["delete"]:
                self.info.remove(self.selection)
            if "quitAfter" in self.selection and self.selection["quitAfter"]:
                self.done = True
                return True
            self.selection = None

        self.done = False
        return False

    '''
    add internal state
    bad pattern: chat option stored as references to class complicates this
    '''
    def setUp(self,state):
        self.text = state["text"]
        self.info = state["info"]
        if "allowExit" in state:
            self.allowExit = state["allowExit"]
             
'''
the chat for collecting the reward
bad code: subSelf
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
    def handleKey(self, key, noRender=False):
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
bad code: story specific
'''
class GrowthTankRefillChat(Chat):
    id = "GrowthTankRefillChat"
    type = "GrowthTankRefillChat"

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
    def handleKey(self, key, noRender=False):
        # do all activity on the first run
        if self.firstRun:
            # show fluffed up information
            self.persistentText = ["""
    please refill your flask and use it to refill the growthtanks. 

    Empty growthtanks look like this: """,src.canvas.displayChars.indexedMapping[src.canvas.displayChars.growthTank_unfilled],""" full ones look like this: """,src.canvas.displayChars.indexedMapping[src.canvas.displayChars.growthTank_filled],"""
    
Activate these, while having a full bottle in your inventory, but leave the full ones alone"""]
            mainChar.addMessage("please refill your flask and use it to refill the growthtanks")
            src.interaction.submenue = None
            self.set_text(self.persistentText)
            # remove chat option
            # bad code: this removal results in bugs if chats of the same type exist
            # bad pattern: chat option stored as references to class complicates this
            for item in self.firstOfficer.basicChatOptions:

                # check class notation
                if not isinstance(item,dict):
                    if item == GrowthTankRefillChat:
                        toRemove = item
                        break

                # check dictionary notation
                else:
                    if item["chat"] == GrowthTankRefillChat:
                        toRemove = item
                        break
            # remove item
            self.firstOfficer.basicChatOptions.remove(toRemove)

            # trigger further action
            self.phase.doTask1()

            return False

        # finish Chat
        else:
            self.done = True
            return True

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
    def handleKey(self, key, noRender=False):
        # do all activity on the first run
        if self.firstRun:
            # show fluffed up information
            self.persistentText = "indeed. There are some things that need to be done.\n\nFirst exmaine the room a bit and find your way around, but try not activate anything important.\n\nYour implant will store the orders given. When you press q you will get a list of your current orders.\nTry to get familiar with the implant, it is an important tool for keeping things in order.\n\n"
            mainChar.addMessage("press q to see your questlist")
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
    def handleKey(self, key, noRender=False):
        # set up the chat
        if self.firstRun:

            # show information
            self.persistentText = ["There are some growth tanks (",src.canvas.displayChars.indexedMapping[src.canvas.displayChars.growthTank_filled],"/",src.canvas.displayChars.indexedMapping[src.canvas.displayChars.growthTank_unfilled],"), walls (",src.canvas.displayChars.indexedMapping[src.canvas.displayChars.wall],"), a pile of coal (",src.canvas.displayChars.indexedMapping[src.canvas.displayChars.pile],") and a furnace (",src.canvas.displayChars.indexedMapping[src.canvas.displayChars.furnace_inactive],"/",src.canvas.displayChars.indexedMapping[src.canvas.displayChars.furnace_active],")."]
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
            if not self.submenue.handleKey(key, noRender=noRender):
                return False

            # tear down the submenue
            else:
                self.done = True

                # remove chat option
                self.removeFromChatOptions(self.firstOfficer)
             
                # clear submenue
                # bad code: direct state setting
                src.interaction.submenue = None
                src.interaction.loop.set_alarm_in(0.0, src.interaction.callShow_or_exit, '~')

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
    def handleKey(self, key, noRender=False):
        # show information on first run
        if self.firstRun:
            # show fluffed up information
            self.persistentText = """Stern did not actually modify the implant. The modification was done elsewhere.
But that is concerning the artworks, thats nothing you need to know.

You need to know however that Sterns modification enhanced the implants guidance, control and communication abilities.
If you stop thinking and allow the implant to take control, it will do so and continue your task.
You can do so by pressing """+config.commandChars.autoAdvance+"""

It is of limited practability though. It is mainly useful for stupid manual labor and often does not 
do things the most efficent way. It will even try to handle conversion, wich does not allways lead to optimal results"""
            mainChar.addMessage("press "+config.commandChars.autoAdvance+" to let the implant take control ")
            self.set_text(self.persistentText)
            self.firstRun = False

            # punish / reward player
            mainChar.revokeReputation(fraction=2,reason="asking a question")
            mainChar.awardReputation(amount=2,reason="gaining knowledge")
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
    def handleKey(self, key, noRender=False):
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
            mainChar.revokeReputation(fraction=2,reason="asking a question")
            mainChar.awardReputation(amount=2,reason="gaining knowledge")
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
    def handleKey(self, key, noRender=False):
        if self.firstRun:
            # show message
            self.persistentText = "It seems you did not report for duty immediately. Try to not repeat that"
            self.set_text(self.persistentText)
            self.done = True
            self.firstRun = False

            # punish player
            mainChar.revokeReputation(amount=1,reason="not reporting for duty in timely manner")

            # remove chat option
            self.removeFromChatOptions(terrain.waitingRoom.firstOfficer)

            # start intro
            self.phase.acknowledgeTransfer()
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
    def handleKey(self, key, noRender=False):
        # handle chat termination
        if key == "esc":

           return True
                             
        # handle chat termination
        if subSelf.firstRun:
            # job
            if not subSelf.dispatchedPhase:

                # do not assign job
                if subSelf.mainChar.reputation < 10:
                    subSelf.persistentText = "I have some work thats needs to be done, but you will have to proof your worth some more untill you can be trusted with this work.\n\nMaybe "+subSelf.terrain.waitingRoom.secondOfficer.name+" has some work you can do"

                # do not assign job
                elif not subSelf.hopperDutyQuest.active:
                    subSelf.persistentText = "your responsibilities are elsewhere"

                # do not assign job
                elif not "FireFurnaceMeta" in subSelf.mainChar.questsDone: # bad code: is bugged
                    subSelf.persistentText = "Several Officers requested new assistants. The boiler room would be the first target, but you need to have fired a furnace or you cannot take the job"

                # assign job
                else:
                    # show fluff
                    subSelf.persistentText = "Several Officers requested new assistants. Find them and offer them your service"

                    subSelf.hopperDutyQuest.deactivate()
                    subSelf.mainChar.quests.remove(subSelf.hopperDutyQuest)
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
    def handleKey(self, key, noRender=False):
        # handle termination of this chat
        if key == "esc":
           # quit dialog
           return True
                             
        # let the superclass do the selection
        if self.submenue:
            if not self.submenue.handleKey(key, noRender=noRender):
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

class RoomDutyChat(Chat):
    id = "RoomDutyChat"
    type = "RoomDutyChat"

    def __init__(self,partner):
        self.partner = partner
        super().__init__()

    def setUp(self,state):
        self.superior = state["superior"]
        
    def handleKey(self, key, noRender=False):

        if src.gamestate.gamestate.tick%2:
            self.persistentText = "yes, you may."
            quest = src.quests.Serve(superior=self.superior,creator=self)
            mainChar.assignQuest(quest,active=True)
            self.superior.subordinates.append(mainChar)
            self.set_text(self.persistentText)
            self.done = True

            return True

        else:
            self.persistentText = "Not right now. Ask again later"
            self.set_text(self.persistentText)
            self.done = True

            return True

class RoomDutyChat2(Chat):
    id = "RoomDutyChat2"
    type = "RoomDutyChat2"

    def __init__(self,partner):
        self.partner = partner
        super().__init__()

    def setUp(self,state):
        pass
        
    def handleKey(self, key, noRender=False):
        self.persistentText = "Drink something"

        quest = src.quests.PickupQuestMeta(self.partner.room.bean)
        mainChar.assignQuest(quest,active=True)
        quest = src.quests.ActivateQuestMeta(self.partner.room.bean)
        mainChar.assignQuest(quest,active=True)

        self.set_text(self.persistentText)
        self.done = True
        return True

'''
the dialog for asking somebody for a job
'''
class JobChatThird(Chat):
    id = "JobChatThird"
    type = "JobChatThird"

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
        self.containerQuest = state["hopperDutyQuest"]

    '''
    show dialog and assign quest 
    '''
    def handleKey(self, key, noRender=False):
        # handle termination of this chat
        if key == "esc":
           # quit dialog
           return True
                             
        # let the superclass do the selection
        if self.submenue:
            if not self.submenue.handleKey(key, noRender=noRender):
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
    def handleKey(self, key, noRender=False):
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
    def handleKey(self, key, noRender=False):
        # show information on first run
        if self.firstRun:

            # start firing the furnace
            self.persistentText = "Starting now. The engines should be running in a few ticks"
            self.set_text(self.persistentText)
            self.done = True
            global quest
            quest = src.quests.KeepFurnaceFiredMeta(self.partner.room.furnaces[0])
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
    def handleKey(self, key, noRender=False):
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
                    mainChar.revokeReputation(amount=5,reason="asking a superior for service")
                else:
                    # reject player harshly
                    if self.partner.reputation//mainChar.reputation:
                        self.persistentText += self.partner.name+": \"you will need at least have to have "+str(self.partner.reputation//mainChar.reputation)+" times as much reputation to have me consider that\"\n"
                        mainChar.revokeReputation(amount=2*(self.partner.reputation//mainChar.reputation),reason="asking a superior for service")
                    # reject player somewhat nicely
                    else:
                        self.persistentText += self.partner.name+": \"maybe if you come back later\""
                        mainChar.revokeReputation(amount=2,reason="asking a superior for service")
            # consider player request
            else:

                # reject player
                if src.gamestate.gamestate.tick%2:
                    self.persistentText += self.partner.name+": \"sorry, too busy.\"\n"
                    mainChar.revokeReputation(amount=1,reason="getting service refused")

                # allow the recruitment
                else:
                    self.persistentText += self.partner.name+": \"on it!\"\n"
                    mainChar.subordinates.append(self.partner)

            # show dialog
            text = self.persistentText+"\n\n-- press any key --"
            self.set_text((urwid.AttrSpec("default","default"),text))
            self.firstRun = False
            return True
        # continue after the first keypress
        # bad code: the first keystroke is the second keystroke that is handled
        else:
            self.done = True
            return False

'''
'''
class JoinMilitaryChat(Chat):
    id = "CaptainChat"

    '''
    straightforward state initialization
    '''
    def __init__(self,partner):
        self.type = "CaptainChat"
        self.state = None
        self.partner = partner
        self.firstRun = True
        self.done = False
        self.persistentText = ""
        self.wait = False
        super().__init__()

    '''
    show dialog and recruit character depending on success
    bad code: showing the messages should be handled in __init__ or a setup method
    bad code: the dialog and reactions should be generated within the characters
    '''
    def handleKey(self, key, noRender=False):
        # exit submenu
        if key == "esc":
            return True
        
        # show dialog
        if self.firstRun:

            # add player text
            self.persistentText += mainChar.name+": \"i want to join the military.\"\n"

            # reject player request
            if mainChar.reputation < 10:
                self.persistentText += self.partner.name+": \"No. Go kill yourself\""

                quest = src.quests.MurderQuest(toKill=mainChar,creator=self)
                mainChar.assignQuest(quest,active=True)
            else:
                self.persistentText += self.partner.name+": \"No.\""

            # show dialog
            text = self.persistentText+"\n\n-- press any key --"
            self.set_text((urwid.AttrSpec("default","default"),text))
            self.firstRun = False
            return True
        # continue after the first keypress
        # bad code: the first keystroke is the second keystroke that is handled
        else:
            self.done = True
            return False

'''
'''
class CaptainChat(Chat):
    id = "CaptainChat"

    '''
    straightforward state initialization
    '''
    def __init__(self,partner):
        self.type = "CaptainChat"
        self.state = None
        self.partner = partner
        self.firstRun = True
        self.done = False
        self.persistentText = ""
        self.wait = False
        super().__init__()

    '''
    show dialog and recruit character depending on success
    bad code: showing the messages should be handled in __init__ or a setup method
    bad code: the dialog and reactions should be generated within the characters
    '''
    def handleKey(self, key, noRender=False):
        # exit submenu
        if key == "esc":
            return True
        
        if self.wait:
            self.wait = False
            src.gamestate.gamestate.gameWon = True
            return False

        # show dialog
        if self.firstRun:

            # add player text
            self.persistentText += mainChar.name+": \"i want to be captain.\"\n"

            # reject player request
            if not mainChar == self.partner.room.secondOfficer:
                self.persistentText += self.partner.name+": \"Only my second in command could possibly succeed me\""
            # consider player request
            else:
                self.persistentText += self.partner.name+": \"Ok.\""
                self.wait = True

            # show dialog
            text = self.persistentText+"\n\n-- press any key --"
            self.set_text((urwid.AttrSpec("default","default"),text))
            self.firstRun = False
            return True
        # continue after the first keypress
        # bad code: the first keystroke is the second keystroke that is handled
        else:
            self.done = True
            return False

'''
'''
class FactionChat1(Chat):
    id = "FactionChat1"

    '''
    straightforward state initialization
    '''
    def __init__(self,partner):
        self.type = "CaptainChat"
        self.state = None
        self.partner = partner
        self.firstRun = True
        self.done = False
        self.persistentText = ""
        self.wait = False
        super().__init__()

    '''
    '''
    def handleKey(self, key, noRender=False):
        # exit submenu
        if key == "esc":
            return True
        
        # show dialog
        if self.firstRun:

            # add player text
            self.persistentText += mainChar.name+": \"the requirements for an alliance are:.\"\n"
            self.persistentText += "\n\n"
            self.persistentText += "minRep: %s\n"%(self.partner.minRep,)
            self.persistentText += "maxAliance: %s\n"%(self.partner.maxAliance,)
            self.persistentText += "repGain: %s\n"%(self.partner.repGain,)
            self.persistentText += "excludes: \n"
            for exclude in self.partner.excludes:
                self.persistentText += "%s "%(exclude.name,)
            self.persistentText += "\n\n"

            # show dialog
            text = self.persistentText+"\n\n-- press any key --"
            self.set_text((urwid.AttrSpec("default","default"),text))
            self.firstRun = False
            return True
        # continue after the first keypress
        # bad code: the first keystroke is the second keystroke that is handled
        else:
            self.done = True
            return False

'''
'''
class FactionChat2(Chat):
    id = "FactionChat2"

    '''
    straightforward state initialization
    '''
    def __init__(self,partner):
        self.type = "CaptainChat"
        self.state = None
        self.partner = partner
        self.firstRun = True
        self.done = False
        self.persistentText = ""
        self.wait = False
        super().__init__()

    '''
    '''
    def handleKey(self, key, noRender=False):
        # exit submenu
        if key == "esc":
            return True
        
        # show dialog
        if self.firstRun:

            if not self.partner in mainChar.aliances:
                if mainChar.reputation < self.partner.minRep:
                    self.persistentText += mainChar.name+": \"not enough rep.\"\n"
                elif len(mainChar.aliances) > self.partner.maxAliance:
                    self.persistentText += mainChar.name+": \"too many aliances.\"\n"
                else:
                    found = False
                    for exclude in self.partner.excludes:
                        if exclude in mainChar.aliances:
                            found = True

                    if found:
                        self.persistentText += mainChar.name+": \"bad aliance.\"\n"
                    else:
                        self.persistentText += mainChar.name+": \"OK\"\n"
                        mainChar.awardReputation(amount=self.partner.repGain,reason="forging an aliance")
                        mainChar.aliances.append(self.partner)

            else:
                # add player text
                self.persistentText += mainChar.name+": \"we are already alianced.\"\n"

            # show dialog
            text = self.persistentText+"\n\n-- press any key --"
            self.set_text((urwid.AttrSpec("default","default"),text))
            self.firstRun = False
            return True
        # continue after the first keypress
        # bad code: the first keystroke is the second keystroke that is handled
        else:
            self.done = True
            return False



'''
'''
class CaptainChat2(Chat):
    id = "CaptainChat2"

    '''
    straightforward state initialization
    '''
    def __init__(self,partner):
        self.type = "CaptainChat"
        self.state = None
        self.partner = partner
        self.firstRun = True
        self.done = False
        self.persistentText = ""
        self.wait = False
        super().__init__()

    '''
    show dialog and recruit character depending on success
    bad code: showing the messages should be handled in __init__ or a setup method
    bad code: the dialog and reactions should be generated within the characters
    '''
    def handleKey(self, key, noRender=False):
        # exit submenu
        if key == "esc":
            return True
        
        if self.wait:
            self.wait = False
            self.partner.room.secondOfficer = mainChar
            return False

        # show dialog
        if self.firstRun:

            # add player text
            self.persistentText += mainChar.name+": \"i want to be your second in command.\"\n"

            if not self.partner.room.secondOfficer.dead:
                self.persistentText += self.partner.name+": \"No. i have a second in command\""
            else:
                if mainChar.reputation < 100:
                    self.persistentText += self.partner.name+": \"No. I do not trust you\""
                # consider player request
                else:
                    self.persistentText += self.partner.name+": \"Ok.\""
                    self.wait = True

            # show dialog
            text = self.persistentText+"\n\n-- press any key --"
            self.set_text((urwid.AttrSpec("default","default"),text))
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
        self.macro = None
        super().__init__()
        self.objectsToStore.extend(["partner","macro"])

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
    def handleKey(self, key, noRender=False):
        # smooth over impossible state
        if self.partner == None:
           src.logger.debugMessages.append("chatmenu spawned without partner")
           return False

        # wake up character instead of speaking
        if self.partner.unconcious:
            mainChar.addMessage("wake up!")
            self.partner.wakeUp()
            return True

        # maybe exit the submenu
        if key == "esc" and not self.subMenu:
           # abort the chat
           return True
                             
        # skip a turn
        if self.skipTurn:
           self.skipTurn = False
           key = "."

        # show interaction
        out = "\n"

        # wrap around chat submenue
        if self.subMenu:
            # let the submenue handle the key
            if not self.subMenu.done:
                self.subMenu.handleKey(key, noRender=noRender)
                if not self.subMenu.done:
                    return False
                self.handleKey(config.commandChars.wait, noRender=noRender)

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
                options.append(("showFrustration","are you frustrated?"))
                options.append(("goToChar","go to my position"))
                options.append(("activate","activate item on Floor"))
                options.append(("pickUp","pick up items"))
                options.append(("dropAll","drop everyting"))
                options.append(("stopCommand","stop"))
                options.append(("moveWest","move west"))
                options.append(("moveNorth","move north"))
                options.append(("moveSouth","move south"))
                options.append(("moveEast","move east"))
                """
                for option in self.partner.getChatOptions(mainChar):
                    if not isinstance(option,dict):
                        options.append((option,option.dialogName))
                    else:
                        options.append((option,option["dialogName"]))
                options.append(("copyMacros","copy my macros"))
                options.append(("runMacro","run a macro"))

                # add default dialog options
                if not self.partner.silent:
                    options.append(("showQuests","what are you dooing?"))
                """
                options.append(("exit","let us proceed, "+self.partner.name))

                # set the options
                self.setOptions("answer:",options)

            # let the superclass handle the actual selection
            if not self.getSelection():
                super().handleKey(key, noRender=noRender)

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

                    self.subMenu.handleKey(key, noRender=noRender)
                elif self.selection == "showQuests":
                    # spawn quest submenu for partner
                    submenue = src.interaction.QuestMenu(char=self.partner)
                    self.subMenu = submenue
                    submenue.handleKey(key, noRender=noRender)
                    return False
                elif self.selection == "copyMacros":
                    self.partner.macroState["macros"] = mainChar.macroState["macros"]
                    mainChar.addMessage("copy macros")
                    return True
                elif self.selection == "showFrustration":
                    submenue = src.interaction.OneKeystrokeMenu(text = "my frustration is: %s"%(self.partner.frustration))
                    self.subMenu = submenue
                elif self.selection == "goToChar":
                    xDiff = mainChar.xPosition-self.partner.xPosition
                    yDiff = mainChar.yPosition-self.partner.yPosition

                    moveCommand = []

                    if xDiff < 0:
                        localMoveCommand = []
                        strXDiff = str(-xDiff)
                        for char in strXDiff:
                            localMoveCommand.append((char,["norecord"]))
                        localMoveCommand.append(("a",["norecord"]))
                        moveCommand = localMoveCommand + moveCommand
                    if yDiff < 0:
                        localMoveCommand = []
                        strYDiff = str(-yDiff)
                        for char in strYDiff:
                            localMoveCommand.append((char,["norecord"]))
                        localMoveCommand.append(("w",["norecord"]))
                        moveCommand = localMoveCommand + moveCommand
                    if yDiff > 0:
                        localMoveCommand = []
                        strYDiff = str(yDiff)
                        for char in strYDiff:
                            localMoveCommand.append((char,["norecord"]))
                        localMoveCommand.append(("s",["norecord"]))
                        moveCommand = localMoveCommand + moveCommand
                    if xDiff > 0:
                        localMoveCommand = []
                        strXDiff = str(xDiff)
                        for char in strXDiff:
                            localMoveCommand.append((char,["norecord"]))
                        localMoveCommand.append(("d",["norecord"]))
                        moveCommand = localMoveCommand + moveCommand

                    self.partner.macroState["commandKeyQueue"] = self.partner.macroState["commandKeyQueue"]+moveCommand
                    return True
                elif self.selection == "activate":
                    self.partner.macroState["commandKeyQueue"] = self.partner.macroState["commandKeyQueue"]+[("j",[])]
                    return True
                elif self.selection == "pickUp":
                    self.partner.macroState["commandKeyQueue"] = self.partner.macroState["commandKeyQueue"]+[("1",[]),("0",[]),("k",[])]
                    return True
                elif self.selection == "dropAll":
                    self.partner.macroState["commandKeyQueue"] = self.partner.macroState["commandKeyQueue"]+[("1",[]),("0",[]),("l",[])]
                    return True
                elif self.selection == "moveWest":
                    self.partner.macroState["commandKeyQueue"] = self.partner.macroState["commandKeyQueue"]+[("a",[])]
                    return True
                elif self.selection == "moveNorth":
                    self.partner.macroState["commandKeyQueue"] = self.partner.macroState["commandKeyQueue"]+[("w",[])]
                    return True
                elif self.selection == "moveSouth":
                    self.partner.macroState["commandKeyQueue"] = self.partner.macroState["commandKeyQueue"]+[("s",[])]
                    return True
                elif self.selection == "moveEast":
                    self.partner.macroState["commandKeyQueue"] = self.partner.macroState["commandKeyQueue"]+[("d",[])]
                    return True
                elif self.selection == "stopCommand":
                    self.partner.macroState["commandKeyQueue"] = self.partner.macroState["commandKeyQueue"]+[("1",[]),("0",[]),("l",[])]
                    self.partner.macroState["commandKeyQueue"].clear()
                    self.partner.macroState["loop"] = []
                    self.partner.macroState["replay"].clear()
                    if "ifCondition" in self.partner.interactionState:
                        self.partner.interactionState["ifCondition"].clear()
                        self.partner.interactionState["ifParam1"].clear()
                        self.partner.interactionState["ifParam2"].clear()

                    return True
                elif self.selection == "runMacro":
                    submenue = src.interaction.OneKeystrokeMenu(text = "press key for the macro to run")
                    self.subMenu = submenue
                    self.subMenu.followUp = self.runMacro
                    submenue.handleKey(key, noRender=noRender)
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
            self.set_text((urwid.AttrSpec("default","default"),self.persistentText))

        return False

    def runMacro(self):

        if not self.subMenu.keyPressed in self.partner.macroState["macros"]:
            mainChar.addMessage("no macro found")
            return

        commands = []
        for command in self.partner.macroState["macros"][self.subMenu.keyPressed]:
            commands.append((command,[]))
        self.partner.macroState["commandKeyQueue"] = commands

        mainChar.addMessage("run macros - "+self.subMenu.keyPressed)

# a map alowing to get classes from strings
chatMap = {
             "TutorialSpeechTest":TutorialSpeechTest,
             "GrowthTankRefillChat":GrowthTankRefillChat,
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
             "ConfigurableChat":ConfigurableChat,
          }

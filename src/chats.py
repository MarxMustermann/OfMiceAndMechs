####################################################################################################################
###
##    chats and chat realated code belongs here
#     bad pattern: chats should have a parent class
#
####################################################################################################################

# import the other internal libs
import src.interaction

'''
the chat for collecting the reward
'''
class RewardChat(src.interaction.SubMenu):
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
bad code: naming
'''
class FirstChat(src.interaction.SubMenu):
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
                    if item == FirstChat:
                        toRemove = item
                        break

			    # check dictionary notation
                else:
                    if item["chat"] == FirstChat:
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
class FurnaceChat(src.interaction.SubMenu):
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
            # try to let the selection option handle the keystroke
            if not self.submenue.handleKey(key):
                return False

            # tear down the submenue
            else:
                self.done = True

                # find self in the characters chat options
				# bad code: repetetive code
                for item in self.firstOfficer.basicChatOptions:

				    # handle class notation
                    if not isinstance(item,dict):
                        if item == FurnaceChat:
                            toRemove = item
                            break

				    # handle dictionary notation
                    else:
                        if item["chat"] == FurnaceChat:
                            toRemove = item
                            break

				# actually remove the chat
                self.firstOfficer.basicChatOptions.remove(toRemove)
             
                # clear submenue
                # bad code: direct state setting
                src.interaction.submenue = None
                src.interaction.loop.set_alarm_in(0.0, callShow_or_exit, '~')

                # do the selected action
                self.submenue.selection()
                return True

        # do all action in the first part of the dialog
        # bad code: the first part of the chat should be on top
        if self.firstRun:
            # show information
            self.persistentText = ["There are some growth tanks (",displayChars.indexedMapping[displayChars.growthTank_filled],"/",displayChars.indexedMapping[displayChars.growthTank_unfilled],"), walls (",displayChars.indexedMapping[displayChars.wall],"), a pile of coal (",displayChars.indexedMapping[displayChars.pile],") and a furnace (",displayChars.indexedMapping[displayChars.furnace_inactive],"/",displayChars.indexedMapping[displayChars.furnace_active],")."]
            self.set_text(self.persistentText)

            # add new chat option
            self.firstOfficer.basicChatOptions.append({"dialogName":"Is there more i should know?","chat":InfoChat,"params":{"firstOfficer":self.firstOfficer}})
                        
            # offer a selection of different story phasses
            options = [(self.phase.fireFurnaces,"yes"),(self.phase.noFurnaceFirering,"no")]
            self.submenue = src.interaction.SelectionMenu("Say, do you like furnaces?",options)

        return False

'''
a monologe explaining automovement
bad code: should be abstracted
'''
class SternChat(src.interaction.SubMenu):
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
            # find self in the characters chat options
			# bad code: repetetive code
            for item in self.firstOfficer.basicChatOptions:
			    # handle class notation
                if not isinstance(item,dict):
                    if item == SternChat:
                        toRemove = item
                        break
			    # handle dictionary notation
                else:
                    if item["chat"] == SternChat:
                        toRemove = item
                        break

            # remove the chat
            self.firstOfficer.basicChatOptions.remove(toRemove)
            terrain.waitingRoom.firstOfficer.basicChatOptions.remove(toRemove)

            # finish
            self.done = True
            return True

'''
an instruction to ask questions and hinting at the auto mode
bad code: should be abstracted
'''
class InfoChat(src.interaction.SubMenu):
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
            # find chat option
			# bad code: repetetive code
            for item in self.firstOfficer.basicChatOptions:
			    # handle class notation
                if not isinstance(item,dict):
                    if item == InfoChat:
                        toRemove = item
                        break
			    # handle dictionary notation
                else:
                    if item["chat"] == InfoChat:
                        toRemove = item
                        break

            # actually remove chat
            self.firstOfficer.basicChatOptions.remove(toRemove)

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

            # find chat option
			# bad code: repetetive code
            for item in terrain.waitingRoom.firstOfficer.basicChatOptions:

			    # handle class notation
                if not isinstance(item,dict):
                    if item == ReReport:
                        toRemove = item
                        break

			    # handle dictionary notation
                else:
                    if item["chat"] == ReReport:
                        toRemove = item
                        break

            # actually renove the chat
            terrain.waitingRoom.firstOfficer.basicChatOptions.remove(toRemove)

            # start intro
            self.phase.getIntro()
            return True
        else:
            return False

'''
the dialog for asking somebody somewhat important for a job
'''
class JobChatFirst(src.interaction.SubMenu):
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
class JobChatSecond(src.interaction.SubMenu):
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
		# bad code: message does not always fit description
        if not self.hopperDutyQuest.getQuest:
            self.persistentText = "please collect your reward first"
            self.set_text(self.persistentText)
            self.done = True

            return True

        # show quest selection
		# bad code: if/else structure is not needed
        if not self.selectedQuest:
            if self.hopperDutyQuest.actualQuest:
                # refuse to give two quests
                # bad pattern: should be proportional to current reputation
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
                self.submenue = src.interaction.SelectionMenu("select the quest",options)

                return False
            else:
                # refuse to give quests
                self.persistentText = "Not right now. Ask again later"
                self.set_text(self.persistentText)
                self.done = True

                return True
        # assign the selected quest
        else:
            self.hopperDutyQuest.getQuest.getQuest.quest = self.selectedQuest
            self.hopperDutyQuest.getQuest.getQuest.recalculate()
            if self.hopperDutyQuest.getQuest:
                self.hopperDutyQuest.getQuest.recalculate()
            self.terrain.waitingRoom.quests.remove(self.selectedQuest)
            self.done = True
            return True

'''
the chat for making the npc stop firing the furnace
'''
class StopChat(src.interaction.SubMenu):
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
class StartChat(src.interaction.SubMenu):
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

# a map alowing to get classes from strings
chatMap = {
             "FirstChat":FirstChat,
             "FurnaceChat":FurnaceChat,
             "SternChat":SternChat,
             "StartChat":StartChat,
             "StopChat":StopChat,
             "InfoChat":InfoChat,
             "ReReport":ReReport,
             "JobChatFirst":JobChatFirst,
             "JobChatSecond":JobChatSecond,
             "RewardChat":RewardChat,
          }

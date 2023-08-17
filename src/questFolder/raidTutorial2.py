import src
import random

class RaidTutorial2(src.quests.MetaQuestSequence):
    type = "RaidTutorial2"

    def __init__(self, description="raid enemy base", creator=None, targetPosition=None, targetPositionBig=None,reason=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        self.shownPickedUpMachines = False

    def triggerCompletionCheck(self,character=None):
        if not character:
            return False

        return False

    def getNextStep(self,character,ignoreCommands=False):
        if self.subQuests:
            return (None,None)

        terrain = character.getTerrain()
        print(terrain.yPosition)
        print(terrain.xPosition)

        try:
            self.shownPickedUpMachines
        except:
            self.shownPickedUpMachines = False

        if (terrain.yPosition == 7 and terrain.xPosition == 6) and not self.shownPickedUpMachines:
            for item in character.inventory:
                if item.type == "Machine":
                    self.postHandler()
                    return (None,None)
            if character.inventory:
                quest = src.quests.questMap["ClearInventory"](returnToTile=False)
                return ([quest],None)
            if not character.getBigPosition() in ((0,7,0),(1,7,0)):
                quest = src.quests.questMap["GoToTile"](targetPosition=(1,7,0))
                return ([quest],None)
            if not character.getBigPosition() in ((0,7,0),):
                if not character.getSpacePosition() == (1,7,0):
                    quest = src.quests.questMap["GoToPosition"](targetPosition=(1,7,0))
                    return ([quest],None)
            return (None,("a","to cheat yourself onto the neighbour terrain"))

        if (terrain.yPosition == 7 and terrain.xPosition == 5):
            for room in terrain.rooms:
                if room.tag == "generalPurposeRoom":
                    targetRoom = room
                    break

            machinesToSteal = []
            for item in targetRoom.getItemsByType("Machine"):
                machinesToSteal.append(item)

            if machinesToSteal:
                if not character.container == targetRoom:
                    quest = src.quests.questMap["GoToTile"](targetPosition=targetRoom.getPosition())
                    return ([quest],None)

                for item in machinesToSteal:
                    quest = src.quests.questMap["CleanSpace"](targetPositionBig=targetRoom.getPosition(),targetPosition=item.getPosition())
                    return ([quest],None)


            if not self.shownPickedUpMachines:
                text = """
Great! you picked up the machines.

In the real game this raid would not only help you out a lot,
but it would also be very damaging to the enemy base.

Atrittioning your enemy might be a good way to get closer to obtaining their special item.

= press enter to continue =

"""
                src.interaction.showInterruptText(text)
                self.shownPickedUpMachines = True

            if not character.getBigPosition() in ((14,7,0),(13,7,0)):
                quest = src.quests.questMap["GoToTile"](targetPosition=(13,7,0))
                return ([quest],None)
            if not character.getBigPosition() in ((14,7,0),):
                if not character.getSpacePosition() == (13,7,0):
                    quest = src.quests.questMap["GoToPosition"](targetPosition=(13,7,0))
                    return ([quest],None)
            return (None,("d","to cheat yourself onto the neighbour terrain"))

        if (terrain.yPosition == 7 and terrain.xPosition == 6):
            if character.inventory:
                quest = src.quests.questMap["ClearInventory"](returnToTile=False)
                return ([quest],None)

            self.postHandler()
            return (None,None)

    def getSolvingCommandString(self, character, dryRun=True):
        nextStep = self.getNextStep(character)
        if nextStep == (None,None):
            return super().getSolvingCommandString(character)
        return self.getNextStep(character)[1]

    def generateSubquests(self, character=None):
        (nextQuests,nextCommand) = self.getNextStep(character,ignoreCommands=True)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
            return

    def solver(self, character):
        (nextQuests,nextCommand) = self.getNextStep(character)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
            return

        if nextCommand:
            character.runCommandString(nextCommand[0])
            return
        super().solver(character)

src.quests.addType(RaidTutorial2)

import src
import random

class RaidTutorial2(src.quests.MetaQuestSequence):
    type = "RaidTutorial2"

    def __init__(self, description="raid enemy base", creator=None, targetPosition=None, targetPositionBig=None,reason=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        self.shownPickUpMachines = False
        self.shownPickedUpMachines = False
        self.shownCheatText = False
        self.shownEnemyBaseIntro = False

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

            if not self.shownCheatText:
                text = """
To get to the neighbour terrain we have to cheat a little.
Just move left and ignore the big wall.

This will be done properly at some point.
The game is pretty bare bones in many places.


= press enter to continue =
"""
                src.interaction.showInterruptText(text)
                self.shownCheatText = True
            return (None,("a","to cheat yourself onto the neighbour terrain"))

        if (terrain.yPosition == 7 and terrain.xPosition == 5):
            if not self.shownEnemyBaseIntro:
                text = """
You reached enemy territory. The enemy has a base in the middle of the terrain.
The base works very similar to your base. Go check it out.
I placed the machines you need into their base, go fetch them.

Be careful, though. The base is hostile and workers will attack you, if you get too close to them.
The quest system might suggest paths that are suicidal. In that case use other paths.
I healed you again, just in case.

= press enter to continue =
"""
                src.interaction.showInterruptText(text)
                character.health = character.maxHealth
                self.shownEnemyBaseIntro = True

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

                if not self.shownPickUpMachines:
                    text = """
You reached the room with the machines to steal.
Dispatch any enemies in this room and pick up the machines.

= press enter to continue =
"""
                    src.interaction.showInterruptText(text)
                    self.shownPickUpMachines = True


                for item in machinesToSteal:
                    quest = src.quests.questMap["CleanSpace"](targetPositionBig=targetRoom.getPosition(),targetPosition=item.getPosition())
                    return ([quest],None)

            if not self.shownPickedUpMachines:
                text = """
Great! You picked up the machines.

Right now, their base contains nothing worth stealing besides the machines you stole.
Except one thing. Do you see the item shown as \\/ ?

There is only two of these special items in the world and they cannot be crafted.
You need two of those items to win the game. 
Their base is too busy to steal that item.

So go home and build better weapons


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

import src


class RaidTutorial2(src.quests.MetaQuestSequence):
    type = "RaidTutorial2"

    def __init__(self, description="raid enemy base", creator=None, targetPosition=None, targetPositionBig=None,reason=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        self.shownPickedUpMachines = False
        self.shownCheatText = False
        self.shownNearbyBaseText = False
        self.shownEnemyBaseIntro = False

    def triggerCompletionCheck(self,character=None):
        if not character:
            return False

        return False

    def getNextStep(self,character,ignoreCommands=False):
        if self.subQuests:
            return (None,None)

        terrain = character.getTerrain()

        if (terrain.yPosition == 7 and terrain.xPosition == 6) and not self.shownPickedUpMachines:
            for item in character.inventory:
                if item.type == "Machine":
                    self.postHandler()
                    return (None,None)
            if character.inventory:
                quest = src.quests.questMap["ClearInventory"](returnToTile=False)
                return ([quest],None)
            if character.getBigPosition() not in ((0,7,0),(1,7,0)):
                quest = src.quests.questMap["GoToTile"](targetPosition=(1,7,0))
                return ([quest],None)
            if character.getBigPosition() not in ((0,7,0),) and character.getSpacePosition() != (1, 7, 0):
                quest = src.quests.questMap["GoToPosition"](targetPosition=(1,7,0))
                return ([quest],None)

            if not self.shownCheatText:
                text = """
To get to the neighbor terrain we have to cheat a little.
Just move left and ignore the big wall.

This will be done properly at some point.
The game is pretty bare bones in many places.


= press enter to continue =
"""
                src.interaction.showInterruptText(text)
                self.shownCheatText = True
            return (None,("a","cheat yourself onto the neighbor terrain"))

        if (terrain.yPosition == 7 and terrain.xPosition == 5):
            if not self.shownEnemyBaseIntro:
                text = """
You reached enemy territory. The enemy has a base in the middle of the terrain.
The base works very similar to your base. Go check it out.

Be careful, though. The base is hostile and workers will attack you, if you get too close to them.
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

            if not self.shownNearbyBaseText:
                pos = (8,6,0)
                if targetRoom.getPosition() == (7,8,0):
                    pos = (8,8,0)
                if targetRoom.getPosition() == (6,7,0):
                    pos = (6,8,0)
                if character.getBigPosition() != pos:
                    quest = src.quests.questMap["GoToTile"](targetPosition=pos)
                    return ([quest],None)
                text = """
The machines are in the room next to you.
The machines look like this: X\\
The machines a color coded by the items they produce.

The enemies storage room is guarded and the enemies use rods as crude weapons.
Kill the guard and avoid the other NPCs that are passing through.
I healed you so that can take on the guard.

Collect the machines


= press enter to continue =
"""
                src.interaction.showInterruptText(text)
                character.health = character.maxHealth
                self.shownNearbyBaseText = True


            machinesToSteal = []
            for item in targetRoom.getItemsByType("Machine"):
                machinesToSteal.append(item)

            if machinesToSteal:
                if character.container != targetRoom:
                    quest = src.quests.questMap["GoToTile"](targetPosition=targetRoom.getPosition())
                    return ([quest],None)

                for item in machinesToSteal:
                    quest = src.quests.questMap["CleanSpace"](targetPositionBig=targetRoom.getPosition(),targetPosition=item.getPosition())
                    return ([quest],None)

            if not self.shownPickedUpMachines:
                text = """
Great! You picked up the machines.
Pause a moment before you run.

Right now, their base contains nothing worth stealing besides the machines you stole.
Except one thing. Do you see the item shown as \\/ ?

There is only two of these special items in the world and they cannot be crafted.
You need two of those items to win the game.
Their base is too busy to steal that item.

So go home and build better weapons


= press enter to continue =

"""
                text = """
Great! You picked up the machines.
Now get out of there and bring the loot home.


= press enter to continue =

"""
                src.interaction.showInterruptText(text)
                self.shownPickedUpMachines = True

            if character.getBigPosition() not in ((14,7,0),(13,7,0)):
                quest = src.quests.questMap["GoToTile"](targetPosition=(13,7,0))
                return ([quest],None)
            if character.getBigPosition() not in ((14,7,0),) and character.getSpacePosition() != (13, 7, 0):
                quest = src.quests.questMap["GoToPosition"](targetPosition=(13,7,0))
                return ([quest],None)
            return (None,("d","cheat yourself onto the neighbor terrain"))

        if (terrain.yPosition == 7 and terrain.xPosition == 6):
            if character.inventory:
                quest = src.quests.questMap["ClearInventory"](returnToTile=False)
                return ([quest],None)

            self.postHandler()
            return (None,None)
        return None

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

import src
import random

class RaidTutorial(src.quests.MetaQuestSequence):
    type = "RaidTutorial"

    def __init__(self, description="raid enemy base", creator=None, targetPosition=None, targetPositionBig=None,reason=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        self.shownCheatText = False
        self.shownEnemyBaseIntro = False
        self.specialItemText = False

    def triggerCompletionCheck(self,character=None):
        if not character:
            return False

        return False

    def getNextStep(self,character,ignoreCommands=False):
        if self.subQuests:
            return (None,None)

        terrain = character.getTerrain()

        try:
            self.shownEnemyBaseIntro
        except:
            self.shownEnemyBaseIntro = False

        if (terrain.yPosition == 7 and terrain.xPosition == 6) and not self.specialItemText:
            if character.inventory:
                quest = src.quests.questMap["ClearInventory"]()
                return ([quest],None)
            if not character.getBigPosition() in ((0,7,0),(1,7,0)):
                quest = src.quests.questMap["GoToTile"](targetPosition=(1,7,0))
                return ([quest],None)
            if not character.getBigPosition() in ((0,7,0),) and character.getSpacePosition() != (1, 7, 0):
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
            return (None,("a","to cheat yourself onto the neighbor terrain"))

        if (terrain.yPosition == 7 and terrain.xPosition == 5) and not self.specialItemText:
            if not self.shownEnemyBaseIntro:
                text = """
You reached enemy territory. The enemy has a base in the middle of the terrain.
The base works very similar to your base. Go check it out.

Be careful, though. The base is hostile and workers will attack you, if you get too close to them.
The quest system might suggest paths that are suicidal. In that case use other paths.
I healed you again, just in case.

= press enter to continue =
"""
                src.interaction.showInterruptText(text)
                character.health = character.maxHealth
                self.shownEnemyBaseIntro = True

            try:
                self.specialItemText
            except:
                self.specialItemText = False

            if not self.specialItemText:
                if character.getBigPosition() != (6, 8, 0):
                    quest = src.quests.questMap["GoToTile"](targetPosition=(6,8,0))
                    return ([quest],None)
                text = """
This enemy base works very similar to your base.
It has workers and it is expanding and should react to the environment.

Right now, their base contains nothing worth stealing.
Except one thing. Do you see the item shown as \\/ ?

There is only two of these special items in the world and they cannot be crafted.
You need two of those items to win the game.
Their base is too busy to steal that item.

So go home and prepare for a bigger raid.


= press enter to continue =
"""
                src.interaction.showInterruptText(text)
                self.specialItemText = True

        if (terrain.yPosition == 7 and terrain.xPosition == 5):
            if not character.getBigPosition() in ((14,7,0),(13,7,0)):
                quest = src.quests.questMap["GoToTile"](targetPosition=(13,7,0))
                return ([quest],None)
            if not character.getBigPosition() in ((14,7,0),) and character.getSpacePosition() != (13, 7, 0):
                quest = src.quests.questMap["GoToPosition"](targetPosition=(13,7,0))
                return ([quest],None)
            return (None,("d","to cheat yourself onto the neighbor terrain"))

        if (terrain.yPosition == 7 and terrain.xPosition == 6):
            text = """
So let's recap:

* There are 2 bases
* Your base and an enemy base
* The enemy base has something you want

So they have to die.
Return to your base and let's see how we do that.

(I healed you again)

= press enter to continue =
"""
            src.interaction.showInterruptText(text)
            character.health = character.maxHealth
            self.postHandler()
        2/0

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

src.quests.addType(RaidTutorial)

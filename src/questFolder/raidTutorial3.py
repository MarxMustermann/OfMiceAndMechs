import src
import random

class RaidTutorial3(src.quests.MetaQuestSequence):
    type = "RaidTutorial3"

    def __init__(self, description="raid enemy base", creator=None, targetPosition=None, targetPositionBig=None,reason=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        self.shownPickedUpMachines = False

    def triggerCompletionCheck(self,character=None):
        if not character:
            return False

        return False

    def getNextStep(self,character,ignoreCommands=False,dryRun=True):
        if self.subQuests:
            return (None,None)

        terrain = character.getTerrain()

        if character.health < 80 and character.canHeal():
            return (None,"JH","to heal")

        if (terrain.yPosition == 7 and terrain.xPosition == 6) and not self.shownPickedUpSpecialItemSlot:
            #if character.inventory:
            #    quest = src.quests.questMap["ClearInventory"](returnToTile=False)
            #    return ([quest],None)
            if not character.getBigPosition() in ((0,7,0),(1,7,0)):
                quest = src.quests.questMap["GoToTile"](targetPosition=(1,7,0))
                return ([quest],None)
            if not character.getBigPosition() in ((0,7,0),) and character.getSpacePosition() != (1, 7, 0):
                quest = src.quests.questMap["GoToPosition"](targetPosition=(1,7,0))
                return ([quest],None)
            return (None,("a","to cheat yourself onto the neighbor terrain"))

        if (terrain.yPosition == 7 and terrain.xPosition == 5):
            enemies = []
            for otherCharacter in terrain.characters:
                if isinstance(otherCharacter,src.characters.Monster):
                    continue
                if otherCharacter.faction == character.faction:
                    continue
                enemies.append(otherCharacter)

            for room in terrain.rooms:
                for otherCharacter in room.characters:
                    if isinstance(otherCharacter,src.characters.Monster):
                        continue
                    if otherCharacter.faction == character.faction:
                        continue
                    enemies.append(otherCharacter)

            for enemy in  enemies:
                if not enemy.container:
                    continue
                if enemy.getBigPosition() == (0,0,0):
                    continue
                quest = src.quests.questMap["SecureTile"](toSecure=enemy.getBigPosition(),endWhenCleared=True)
                return ([quest],None)

            if not dryRun:
                text = """
You defeated the enemy base.
This concludes the tutorial and feature show off.

I tried to keep it short and still teach the most important things.
I'd be happy to get feedback on how all of this worked out.

Since the actual game is not ready yet, i'll crash the game now.

= press space to continue =
"""
                src.interaction.showInterruptText(text)
                1/0

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
        (nextQuests,nextCommand) = self.getNextStep(character,dryRun=False)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
            return

        if nextCommand:
            character.runCommandString(nextCommand[0])
            return
        super().solver(character)

src.quests.addType(RaidTutorial3)

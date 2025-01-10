import random

import src

class DropItemsOutside(src.quests.MetaQuestSequence):
    type = "DropItemsOutside"

    def __init__(self, description="drop items outside", creator=None, toCollect=None, lifetime=None, reason=None):
        self.lastMoveDirection = None
        questList = []
        super().__init__(questList, creator=creator,lifetime=lifetime)
        self.metaDescription = description
        self.reason = reason
        if toCollect:
            self.metaDescription += " for "+toCollect
        self.toCollect = toCollect

    def generateTextDescription(self):
        out = []

        reason = ""
        text = """
Clear your inventory outside"""
        text += f"""{reason}."""
        text += """

This quest will end when your inventory is empty."""

        out.append(text)
        return out

    def triggerCompletionCheck(self,character=None):
        if not character:
            return False
        if not character.inventory:
            self.postHandler()
            return True
        return False

    def getNextStep(self,character,ignoreCommands=False, dryRun = True):

        if not character:
            return (None,None)

        if self.subQuests:
            return (None,None)

        terrain = character.getTerrain()

        # drop items
        if not terrain.getRoomByPosition(character.getBigPosition()):
            if not terrain.getItemByPosition(character.getPosition()) and not (character.getSpacePosition()[0] in (1,13) or character.getSpacePosition()[1] in (1,13)):
                return (None,("l","drop item"))
            # go somewhere else
            if random.random() > 0.1:
                pos = (random.randint(2,12),random.randint(2,12),0)
                quest = src.quests.questMap["GoToPosition"](targetPosition=pos,reason="move to a random point to drop items")
                return ([quest],None)

        # go somewhere else
        bigPos = (random.randint(2,12),random.randint(2,12),0)
        quest = src.quests.questMap["GoToTile"](targetPosition=bigPos,reason="move to a random tile to drop items")
        return ([quest],None)

    def droppedItem(self,extraInfo):
        self.triggerCompletionCheck(extraInfo[0])

    def assignToCharacter(self, character):
        if self.character:
            return None

        self.startWatching(character,self.droppedItem, "itemDropped")
        return super().assignToCharacter(character)

src.quests.addType(DropItemsOutside)

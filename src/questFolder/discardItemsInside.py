import random

import src

class DiscardItemsInside(src.quests.MetaQuestSequence):
    type = "DiscardItemsInside"

    def __init__(self, description="discard items inside", creator=None, toCollect=None, lifetime=None, reason=None):
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
Clear your inventory inside"""
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

        # go inside
        if not character.container.isRoom:
            quest = src.quests.questMap["GoHome"]()
            return ([quest],None)

        dropPositions = [(0,6,0),(12,6,0),(6,0,0),(6,12,0)]
        if character.getPosition() in dropPositions:
            return (None,("l","drop item"))

        for dropPosition in dropPositions:
            if character.container.getPositionWalkable(dropPosition):
                quest = src.quests.questMap["GoToPosition"](targetPosition=dropPosition)
                return ([quest],None)

        if dryRun:
            self.fail("no drop spot")
        return (None,None)

    def droppedItem(self,extraInfo):
        self.triggerCompletionCheck(extraInfo[0])

    def assignToCharacter(self, character):
        if self.character:
            return None

        self.startWatching(character,self.droppedItem, "itemDropped")
        return super().assignToCharacter(character)

src.quests.addType(DiscardItemsInside)

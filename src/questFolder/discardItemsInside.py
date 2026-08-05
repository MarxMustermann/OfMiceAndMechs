import random

import src

class DiscardItemsInside(src.quests.MetaQuestSequence):
    type = "DiscardItemsInside"
    lowLevel = True

    def __init__(self, description="discard items inside", creator=None, lifetime=None, reason=None, amount=None):
        self.lastMoveDirection = None
        questList = []
        super().__init__(questList, creator=creator,lifetime=lifetime)
        self.metaDescription = description
        self.reason = reason
        self.amount = amount

    def generateTextDescription(self):

        reasonText = (src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),".")
        if self.reason:
            reasonText = [(src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),","),f" to {self.reason}."]
        text = [f"""
""",(src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"Clear your inventory inside"),reasonText]
        text.append("""
Drop your items onto a doorstep and they will disappear.

This quest will end when your inventory is empty.""")

        if self.amount:
            text.append(f"""
Drop {self.amount} more items.
""")

        return text

    def triggerCompletionCheck(self,character=None,dryRun=True):
        if not character:
            return False
        if not character.inventory:
            if not dryRun:
                self.postHandler()
            return True
        return False

    def getNextStep(self,character,ignoreCommands=False, dryRun = True):

        # handle weird edge cases
        if not character:
            return (None,None)
        if self.subQuests:
            return (None,None)

        # set up helper variables
        terrain = character.getTerrain()

        # go inside
        if not character.container.isRoom:
            quest = src.quests.questMap["GoHome"](reason="get inside")
            return ([quest],None)

        # drop items in door frames
        dropPositions = [(0,6,0),(12,6,0),(6,0,0),(6,12,0)]
        if character.getPosition() in dropPositions:
            return (None,("l","drop item"))
        for dropPosition in dropPositions:
            if character.container.getPositionWalkable(dropPosition):
                quest = src.quests.questMap["GoToPosition"](targetPosition=dropPosition,reason="reach drop spot")
                return ([quest],None)

        # fail
        return self._solver_trigger_fail(dryRun,"no drop spot")

    def droppedItem(self,extraInfo):
        if self.amount:
            self.amount -= 1
            if self.amount == 0:
                self.postHandler()
                return
        self.triggerCompletionCheck(extraInfo[0],dryRun=False)

    def assignToCharacter(self, character):
        if self.character:
            return None

        self.startWatching(character,self.droppedItem, "dropped")
        return super().assignToCharacter(character)

src.quests.addType(DiscardItemsInside)

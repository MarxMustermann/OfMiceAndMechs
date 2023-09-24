import src
import random

class ScavengeTile(src.quests.MetaQuestSequence):
    type = "ScavengeTile"

    def __init__(self, description="scavenge tile", creator=None, targetPosition=None,toCollect=None, reason=None, endOnFullInventory=False):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description+" "+str(targetPosition)
        self.baseDescription = description
        self.toCollect = toCollect
        self.reason = reason
        self.endOnFullInventory = endOnFullInventory

        self.targetPosition = targetPosition

    def generateTextDescription(self):
        out = []

        reason = ""
        if self.reason:
            reason = f", to {self.reason}"
        text = f"""
Scavenge the tile {self.targetPosition}"""
        if self.toCollect:
            text += f" for {self.toCollect}"
        text += f"""{reason}."""
        text += """

This quest will end when the target tile has no items left."""

        out.append(text)
        return out

    def triggerCompletionCheck(self,character=None):

        if not character:
            return

        if self.endOnFullInventory:
            if not character.getFreeInventorySpace() > 0:
                self.postHandler()
                return

        if not self.getLeftoverItems(character):
            self.postHandler()
            return

        return

    def solver(self, character):
        self.triggerCompletionCheck(character=character)

        if not self.subQuests:
            hasIdleSubordinate = False
            for subordinate in character.subordinates:
                if len(subordinate.quests) < 2: 
                    hasIdleSubordinate = True

            if hasIdleSubordinate:
                character.runCommandString("Hjsssssj")
                return

            if not character.getFreeInventorySpace() > 0:
                if self.endOnFullInventory:
                    self.postHandler()
                    return
                quest = src.quests.questMap["ClearInventory"](reason="be able to pick up more items")
                self.addQuest(quest)
                return

            if not (character.getBigPosition() == (self.targetPosition[0],self.targetPosition[1],0)):
                quest = src.quests.questMap["GoToTile"](targetPosition=self.targetPosition,reason="go to target tile")
                self.addQuest(quest)
                return

            items = self.getLeftoverItems(character)
            if items:

                item = random.choice(items)

                quest = src.quests.questMap["CleanSpace"](targetPosition=item.getSmallPosition(),targetPositionBig=self.targetPosition,reason="pick up the items")
                self.addQuest(quest)
                return

        super().solver(character)

    def getLeftoverItems(self,character):
        terrain = character.getTerrain()
        leftOverItems = []
        items = terrain.itemsByBigCoordinate.get(self.targetPosition,[])
        for item in items:
            #if item.type == "Scrap":
            #    continue
            if self.toCollect and not item.type == self.toCollect:
                continue
            if item.bolted:
                continue

            leftOverItems.append(item)
        return leftOverItems

    def pickedUpItem(self,extraInfo):
        self.triggerCompletionCheck(extraInfo[0])

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.pickedUpItem, "itemPickedUp")
        return super().assignToCharacter(character)

    def getQuestMarkersTile(self,character):
        result = super().getQuestMarkersTile(character)
        result.append(((self.targetPosition[0],self.targetPosition[1]),"target"))
        return result

    def getQuestMarkersSmall(self,character,renderForTile=False):
        if isinstance(character.container,src.rooms.Room):
            if renderForTile:
                return []
        else:
            if not renderForTile:
                return []

        result = super().getQuestMarkersSmall(character,renderForTile=renderForTile)

        if renderForTile:
            if character.getBigPosition() == self.targetPosition:
                for item in character.getTerrain().itemsByBigCoordinate.get(self.targetPosition,[]):
                    if self.toCollect and not item.type == self.toCollect:
                        continue
                    result.append((item.getPosition(),"target"))

        return result

src.quests.addType(ScavengeTile)

import random

import src


class ScavengeTile(src.quests.MetaQuestSequence):
    type = "ScavengeTile"

    def __init__(self, description="scavenge tile", creator=None, targetPosition=None,toCollect=None, reason=None, endOnFullInventory=False,tryHard=False):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description+" "+str(targetPosition)
        self.baseDescription = description
        self.toCollect = toCollect
        self.reason = reason
        self.endOnFullInventory = endOnFullInventory

        self.targetPosition = targetPosition
        self.tryHard = tryHard

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

        if self.endOnFullInventory and not character.getFreeInventorySpace() > 0:
            self.postHandler()
            return

        if not self.getLeftoverItems(character):
            self.postHandler()
            return

        return

    def getNextStep(self,character,ignoreCommands=False, dryRun = True):
        self.triggerCompletionCheck(character=character)

        if not self.subQuests:
            hasIdleSubordinate = False
            for subordinate in character.subordinates:
                if len(subordinate.quests) < 2:
                    hasIdleSubordinate = True

            if hasIdleSubordinate:
                return (None,("Hjsssssj","make subordinate scavenge"))

            if character.getTerrain().alarm and not self.tryHard:
                if not dryRun:
                    self.fail("alarm")
                return (None,None)

            if not character.getFreeInventorySpace() > 0:
                if self.endOnFullInventory:
                    self.postHandler()
                    return (None,None)
                quest = src.quests.questMap["ClearInventory"](reason="be able to pick up more items")
                return ([quest],None)

            if character.getBigPosition() != (self.targetPosition[0], self.targetPosition[1], 0):
                quest = src.quests.questMap["GoToTile"](targetPosition=self.targetPosition,reason="go to target tile")
                return ([quest],None)


            items = self.getLeftoverItems(character)
            for item in items:
                path = character.getTerrain().getPathTile(character.getTilePosition(),character.getSpacePosition() ,item.getSmallPosition(),character=character,ignoreEndBlocked =True)
                if len(path) or item.getPosition() == character.getPosition():
                    quest = src.quests.questMap["CleanSpace"](targetPosition=item.getSmallPosition(),targetPositionBig=self.targetPosition,reason="pick up the items")
                    return ([quest],None)
        return (None,None)
    
    def getLeftoverItems(self,character):
        terrain = character.getTerrain()
        leftOverItems = []
        items = terrain.itemsByBigCoordinate.get(self.targetPosition,[])
        items = items[:]
        random.shuffle(items)
        for item in items:
            #if item.type == "Scrap":
            #    continue
            if self.toCollect and item.type != self.toCollect:
                continue
            if item.bolted:
                continue

            leftOverItems.append(item)
        return leftOverItems

    def pickedUpItem(self,extraInfo):
        self.triggerCompletionCheck(extraInfo[0])

    def assignToCharacter(self, character):
        if self.character:
            return None

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

        if renderForTile and character.getBigPosition() == self.targetPosition:
            for item in character.getTerrain().itemsByBigCoordinate.get(self.targetPosition,[]):
                if item.bolted:
                    continue
                if self.toCollect and item.type != self.toCollect:
                    continue
                result.append((item.getPosition(),"target"))

        return result

src.quests.addType(ScavengeTile)

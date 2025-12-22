import random

import src


class ScavengeTile(src.quests.MetaQuestSequence):
    type = "ScavengeTile"

    def __init__(self, description="scavenge tile", creator=None, targetPositionBig=None,toCollect=None, reason=None, endOnFullInventory=False,tryHard=False,lifetime=None,ignoreAlarm=False):
        questList = []
        super().__init__(questList, creator=creator,lifetime=None)
        self.metaDescription = description
        if targetPositionBig:
            self.metaDescription += " "+str(targetPositionBig)
        self.baseDescription = description
        self.toCollect = toCollect
        self.reason = reason
        self.endOnFullInventory = endOnFullInventory

        self.targetPositionBig = targetPositionBig
        self.tryHard = tryHard
        self.ignoreAlarm = ignoreAlarm

    def generateTextDescription(self):
        out = []

        reason = ""
        if self.reason:
            reason = f", to {self.reason}"
        text = f"""
Scavenge the tile {self.targetPositionBig}"""
        if self.toCollect:
            text += f" for {self.toCollect}"
        text += f"""{reason}."""
        text += """

This quest will end when the target tile has no items left."""

        out.append(text)
        return out

    def triggerCompletionCheck(self,character=None,dryRun=True):

        if not character:
            return False

        if self.endOnFullInventory and not character.getFreeInventorySpace() > 0:
            if not dryRun:
                self.postHandler()
            return True

        if not self.getLeftoverItems(character):
            if not dryRun:
                self.postHandler()
            return True

        return False

    def getNextStep(self,character,ignoreCommands=False, dryRun = True):

        # end when done
        self.triggerCompletionCheck(character=character,dryRun=dryRun)

        # use current position as default
        if not self.targetPositionBig:
            if not dryRun:
                self.targetPositionBig = character.getBigPosition()
            return (None,("+","set current position as target"))

        # handle weird edge cases
        if self.subQuests:
            return (None, None)

        # handle enemies
        if character.getNearbyEnemies():
            if character.health > character.maxHealth//3:
                quest = src.quests.questMap["Fight"]()
                return ([quest],None)
            else:
                quest = src.quests.questMap["Heal"]()
                return ([quest],None)
            
        # fail on alarm
        if character.getTerrain().alarm and not self.tryHard and not self.ignoreAlarm:
            return self._solver_trigger_fail(dryRun,"alarm")

        # ensure free inventory space
        if not character.getFreeInventorySpace() > 0:
            if self.endOnFullInventory:
                if not dryRun:
                    self.postHandler()
                return (None,("+","end quest"))
            quest = src.quests.questMap["ClearInventory"](reason="be able to pick up more items")
            return ([quest],None)

        # go to loot spot
        if character.getBigPosition() != (self.targetPositionBig[0], self.targetPositionBig[1], 0):
            quest = src.quests.questMap["GoToTile"](targetPosition=self.targetPositionBig,reason="go to target tile")
            return ([quest],None)

        # pick up items
        items = self.getLeftoverItems(character)
        for item in items:
            path = character.getTerrain().getPathTile(character.getTilePosition(),character.getSpacePosition() ,item.getSmallPosition(),character=character,ignoreEndBlocked =True)
            if len(path) or item.getPosition() == character.getPosition():
                quest = src.quests.questMap["CleanSpace"](targetPosition=item.getSmallPosition(),targetPositionBig=self.targetPositionBig,reason="pick up the items",pickUpBolted=True)
                return ([quest],None)
    
    def getLeftoverItems(self,character):
        terrain = character.getTerrain()
        if not terrain:
            return []
        leftOverItems = []
        targetPositionBig = self.targetPositionBig
        if not targetPositionBig:
            targetPositionBig = character.getBigPosition()
        items = terrain.itemsByBigCoordinate.get(targetPositionBig,[])
        items = items[:]
        random.shuffle(items)
        for item in items:
            if self.toCollect and item.type != self.toCollect:
                continue
            if item.bolted:
                continue

            leftOverItems.append(item)
        return leftOverItems

    def pickedUpItem(self,extraInfo):
        self.triggerCompletionCheck(extraInfo[0],dryRun=False)

    def assignToCharacter(self, character):
        if self.character:
            return None

        self.startWatching(character,self.pickedUpItem, "itemPickedUp")
        return super().assignToCharacter(character)

    def getQuestMarkersTile(self,character):
        result = super().getQuestMarkersTile(character)
        targetPositionBig = self.targetPositionBig
        if not targetPositionBig:
            targetPositionBig = character.getBigPosition()
        result.append(((targetPositionBig[0],targetPositionBig[1]),"target"))
        return result

    def getQuestMarkersSmall(self,character,renderForTile=False):
        if isinstance(character.container,src.rooms.Room):
            if renderForTile:
                return []
        else:
            if not renderForTile:
                return []

        targetPositionBig = self.targetPositionBig
        if not targetPositionBig:
            targetPositionBig = character.getBigPosition()

        result = super().getQuestMarkersSmall(character,renderForTile=renderForTile)

        if renderForTile and character.getBigPosition() == self.targetPositionBig:
            for item in character.getTerrain().itemsByBigCoordinate.get(targetPositionBig,[]):
                if item.bolted:
                    continue
                if self.toCollect and item.type != self.toCollect:
                    continue
                result.append((item.getPosition(),"target"))

        return result

src.quests.addType(ScavengeTile)

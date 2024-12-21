import random

import src

class FarmMoldTile(src.quests.MetaQuestSequence):
    type = "FarmMoldTile"

    def __init__(self, description="farm mold tile", creator=None, targetPosition=None, reason=None, endOnFullInventory=False):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description+" "+str(targetPosition)
        self.baseDescription = description
        self.reason = reason
        self.endOnFullInventory = endOnFullInventory

        self.targetPosition = targetPosition

    def generateTextDescription(self):
        out = []

        reason = ""
        if self.reason:
            reason = f", to {self.reason}"
        text = f"""
farm mold on the tile {self.targetPosition}"""

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
        if not character:
            return (None,None)
        if self.subQuests:
            return (None,None)

        if character.getTerrain().alarm:
            if not dryRun:
                self.fail("alarm")
            return (None,None)

        if character.getBigPosition() != (self.targetPosition[0], self.targetPosition[1], 0):
            quest = src.quests.questMap["GoToTile"](targetPosition=self.targetPosition,reason="go to target tile")
            return ([quest],None)

        items = self.getLeftoverItems(character)
        for item in items:
            if item.bolted:
                continue
            else:
                path = character.getTerrain().getPathTile(character.getTilePosition(),character.getSpacePosition() ,item.getSmallPosition(),character=character,ignoreEndBlocked =True)
                if len(path):
                    quest = src.quests.questMap["CleanSpace"](targetPosition=item.getSmallPosition(),targetPositionBig=self.targetPosition,reason="pick up the items")
                    return ([quest],None)

        offsets = [(0,0,0),(1,0,0),(0,1,0),(-1,0,0),(0,-1,0)]
        foundOffset = None
        charPos = character.getPosition()
        for offset in offsets:
            checkPos = (charPos[0]+offset[0],charPos[1]+offset[1],charPos[2]+offset[2])
            items = character.container.getItemByPosition(checkPos)
            if not items:
                continue

            if not items[0].type == "Sprout":
                continue

            foundOffset = offset
            break

        if foundOffset:
            if foundOffset == (0,0,0):
                command = "j"
            elif foundOffset == (1,0,0):
                command = "Jd"
            elif foundOffset == (-1,0,0):
                command = "Ja"
            elif foundOffset == (0,1,0):
                command = "Js"
            elif foundOffset == (0,-1,0):
                command = "Jw"

            return (None,(command,"stimulate mold growth"))

        items = self.getLeftoverItems(character)
        if not items:
            return (None,None)
        item = random.choice(items)
        quest = src.quests.questMap["GoToPosition"](targetPosition=item.getSmallPosition(),ignoreEndBlocked=True)
        return ([quest],None)

    def getLeftoverItems(self,character):
        terrain = character.getTerrain()
        leftOverItems = []
        numSprouts = 0
        items = terrain.itemsByBigCoordinate.get(self.targetPosition,[])
        for item in items:
            if item.type == "Bloom":
                leftOverItems.append(item)
            if item.type == "Sprout":
                numSprouts += 1
                if numSprouts > 4:
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

src.quests.addType(FarmMoldTile)

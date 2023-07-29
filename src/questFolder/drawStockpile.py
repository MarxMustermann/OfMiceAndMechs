import src

class DrawStockpile(src.quests.MetaQuestSequence):
    type = "DrawStockpile"

    def __init__(self, description="draw stockpile", creator=None, targetPosition=None, targetPositionBig=None,itemType=None,stockpileType=None,tryHard=False,reason=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        self.targetPosition = targetPosition
        self.targetPositionBig = targetPositionBig
        self.itemType = itemType
        self.stockpileType = stockpileType
        self.tryHard = tryHard
        self.painterPos = None
        self.reason = reason

    def triggerCompletionCheck(self,character=None):
        if not character:
            return

    def generateTextDescription(self):
        reason = ""
        if self.reason:
            reason = ", to %s"%(self.reason,)
        mappedNames = {"i":"input stockpile","o":"output stockpile","s":"storage stockpile"}
        text = """
draw a %s stockpile for %s on position %s on tile %s%s.

"""%(mappedNames[self.stockpileType],self.itemType,self.targetPosition,self.targetPositionBig,reason)

        if self.stockpileType == "i":
            text += """
Input stockpiles should be filled by clones. Not every clone will fill stockpiles.
The items to fill up the stockpiles can comes from any source.
Usually items are taken from a corresponding output or storage slot or gathered outside.

Other processes can be set up to take from an input stockpile.
For example a machine can take from an input stockpile.
That way clones should fill up the stockpile and supply the machine with resources.
"""
        elif self.stockpileType == "o":
            text += """
Clones can take items from output stockpiles.
Often the item taken from output stockpiles are carried to input or storage stockpiles.
Sometimes the clones use the items directly.

Output stockpiles need to be filled up by some other process.
For example a machine can produce onto a output stockpile.
That way clones can access the output of a machine.
"""
        else:
            text += """
Stockpiles indicate to clones where items should be stored.
Storage stockpiles are used to store items.

"""

        text += """
Stockpiles are drawn using a Painter (xi).
Examine the Painter for more details.
"""

        if self.tryHard:
            text += """
Try as hard as you can to achieve this.
"""

        return text

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

    def getNextStep(self,character=None,ignoreCommands=False):
        if not self.subQuests:
            rooms = character.getTerrain().getRoomByPosition(self.targetPositionBig)
            if not rooms:
                self.fail("target room missing")
                return (None,None)
            room = rooms[0]

            if self.stockpileType == "i":
                for inputSlot in room.inputSlots:
                    if inputSlot[0] == self.targetPosition:
                        self.postHandler()
                        return (None,None)
            if self.stockpileType == "o":
                for outputSlot in room.outputSlots:
                    if outputSlot[0] == self.targetPosition:
                        self.postHandler()
                        return (None,None)
            if self.stockpileType == "s":
                for storageSlot in room.storageSlots:
                    if storageSlot[0] == self.targetPosition:
                        self.postHandler()
                        return (None,None)

            offsets = ((0,0,0),(0,1,0),(1,0,0),(0,-1,0),(-1,0,0))
            foundOffset = None
            for offset in offsets:
                items = room.getItemByPosition((self.targetPosition[0]+offset[0],self.targetPosition[1]+offset[1],self.targetPosition[2]+offset[2]))
                if not items or not items[-1].type == "Painter":
                    continue

                foundOffset = (offset,items[-1])
            if foundOffset:
                item = foundOffset[1]
                if character.getDistance(item.getPosition()) > 0:
                    quest = src.quests.questMap["GoToPosition"](targetPosition=item.getPosition(),reason="get to the painter")
                    return ([quest],None)

                if self.stockpileType == "i" and not item.paintMode == "inputSlot":
                    return (None,(["c","m","i","enter"],"to configure the painter to input stockpile"))
                if self.stockpileType == "o" and not item.paintMode == "outputSlot":
                    return (None,(["c","m","o","enter"],"to configure the painter to output stockpile"))
                if self.stockpileType == "s" and not item.paintMode == "storageSlot":
                    return (None,(["c","m","s","enter"],"to configure the painter to output stockpile"))
                if not (self.itemType == item.paintType):
                    if self.itemType:
                        return (None,(["c","t"] + list(self.itemType) + ["enter"],"to configure the item type for the stockpile"))
                    else:
                        return (None,(["c","t"] + ["enter"],"to remove the item type for the stockpile"))
                    
                return (None,("jk","draw to stockpile"))

            if not self.painterPos:
                if not character.inventory or not character.inventory[-1].type == "Painter":
                    quest = src.quests.questMap["FetchItems"](toCollect="Painter",amount=1,reason="be able to draw a stockpile")
                    return ([quest],None)
                painter = character.inventory[-1]

            if not character.getBigPosition() == self.targetPositionBig:
                quest = src.quests.questMap["GoToTile"](targetPosition=self.targetPositionBig,reason="get nearby to the drawing spot")
                return ([quest],None)

            if character.getDistance(self.targetPosition) > 0:
                quest = src.quests.questMap["GoToPosition"](targetPosition=self.targetPosition,reason="get to the drawing spot")
                return ([quest],None)

            return (None,("l","drop the Painter"))

        return (None,None)

    def getQuestMarkersTile(self,character):
        result = super().getQuestMarkersTile(character)
        result.append(((self.targetPositionBig[0],self.targetPositionBig[1]),"target"))
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
            result.append(((self.targetPosition[0]+self.targetPositionBig[0]*15,self.targetPosition[1]+self.targetPositionBig[1]*15),"target"))
        else:
            if character.getBigPosition() == self.targetPositionBig:
                result.append(((self.targetPosition[0],self.targetPosition[1]),"target"))
        return result

src.quests.addType(DrawStockpile)

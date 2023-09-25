import src

class DrawStockpile(src.quests.MetaQuestSequence):
    type = "DrawStockpile"

    def __init__(self, description=None, creator=None, targetPosition=None, targetPositionBig=None,itemType=None,stockpileType=None,tryHard=False,reason=None,extraInfo=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.targetPosition = targetPosition
        self.targetPositionBig = targetPositionBig
        self.itemType = itemType
        self.stockpileType = stockpileType
        self.tryHard = tryHard
        self.reason = reason

        if description:
            self.metaDescription = "draw stockpile"
        else:
            stockpileTypeName = ""
            if stockpileType == "i":
                stockpileTypeName = "input"
            if stockpileType == "o":
                stockpileTypeName = "output"
            if stockpileType == "s":
                stockpileTypeName = "storage"
            itemTypeName = ""
            if itemType:
                itemTypeName = f" for {itemType}"
            self.metaDescription = f"draw {stockpileTypeName}stockpile{itemTypeName}"

        if not extraInfo:
            self.extraInfo = {}
        else:
            self.extraInfo = extraInfo

    def triggerCompletionCheck(self,character=None):
        if not character:
            return

        room = character.getTerrain().getRoomByPosition(self.targetPositionBig)[0]
        if self.stockpileType == "i":
            for inputSlot in room.inputSlots:
                if inputSlot[0] == self.targetPosition and inputSlot[1] == self.itemType:
                    self.postHandler()
                    return True
        if self.stockpileType == "o":
            for outputSlot in room.outputSlots:
                if outputSlot[0] == self.targetPosition and outputSlot[1] == self.itemType:
                    self.postHandler()
                    return True
        if self.stockpileType == "s":
            for storageSlot in room.storageSlots:
                if storageSlot[0] == self.targetPosition and storageSlot[1] == self.itemType:
                    self.postHandler()
                    return True

    def generateTextDescription(self):
        reason = ""
        if self.reason:
            reason = f",\nto {self.reason}"
        mappedNames = {"i":"input stockpile","o":"output stockpile","s":"storage stockpile"}
        itemTypePart = ""
        if self.itemType:
            itemTypePart = f"for {self.itemType} "
        text = """
Draw a {} {}on position {} on tile {}{}.

""".format(mappedNames[self.stockpileType],itemTypePart,self.targetPosition,self.targetPositionBig,reason)

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
        elif self.stockpileType == "s":
            text += """
Clones can store items in storage stockpiles.
This means are taken out or added to storage stockpiles.
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

    def unhandledSubQuestFail(self,extraParam):
        self.fail(extraParam["reason"])

    def solver(self, character):
        if self.triggerCompletionCheck(character):
            return

        (nextQuests,nextCommand) = self.getNextStep(character,dryRun=False)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
                self.startWatching(quest,self.unhandledSubQuestFail,"failed")
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

    def handleQuestFailure(self,extraParam):
        self.fail(extraParam["reason"])

    def getNextStep(self,character=None,ignoreCommands=False,dryRun=True):
        if not self.subQuests:
            submenue = character.macroState.get("submenue")
            if submenue:
                if submenue.tag == "paintModeSelection":
                    if submenue.text == "":
                        if self.stockpileType == "i":
                            return (None,(["i"],"to configure the painter to input stockpile"))
                        if self.stockpileType == "o":
                            return (None,(["o"],"to configure the painter to output stockpile"))
                        if self.stockpileType == "s":
                            return (None,(["s"],"to configure the painter to storage stockpile"))
                    elif self.stockpileType == submenue.text:
                        if self.stockpileType == "i":
                            return (None,(["enter"],"to configure the painter to input stockpile"))
                        if self.stockpileType == "o":
                            return (None,(["enter"],"to configure the painter to output stockpile"))
                        if self.stockpileType == "s":
                            return (None,(["enter"],"to configure the painter to storage stockpile"))
                    else:
                        return (None,(["backspace"],"to delete input"))

                if submenue.tag == "paintTypeSelection":
                    itemType = self.itemType
                    if not itemType:
                        itemType = ""

                    if itemType == submenue.text:
                        if self.stockpileType == "i":
                            return (None,(["enter"],"to configure the painter to input stockpile"))
                        if self.stockpileType == "o":
                            return (None,(["enter"],"to configure the painter to output stockpile"))
                        if self.stockpileType == "s":
                            return (None,(["enter"],"to configure the painter to storage stockpile"))

                    correctIndex = 0
                    while correctIndex < len(itemType) and correctIndex < len(submenue.text):
                        if not itemType[correctIndex] == submenue.text[correctIndex]:
                            break
                        correctIndex += 1

                    if correctIndex < len(submenue.text):
                        return (None,(["backspace"],"to delete input"))

                    return (None,(itemType[correctIndex:],"to enter type"))

                if submenue.tag == "paintExtraParamName":
                    nameToSet = ""
                    for (key,value) in self.extraInfo.items():
                        if (not key in submenue.extraInfo["item"].paintExtraInfo) or (not value == submenue.extraInfo["item"].paintExtraInfo[key]):
                            nameToSet = key

                    if nameToSet == submenue.text:
                        return (None,(["enter"],"to set the name of the extra parameter"))

                    correctIndex = 0
                    while correctIndex < len(nameToSet) and correctIndex < len(submenue.text):
                        if not nameToSet[correctIndex] == submenue.text[correctIndex]:
                            break
                        correctIndex += 1

                    if correctIndex < len(submenue.text):
                        return (None,(["backspace"],"to delete input"))

                    return (None,(nameToSet[correctIndex:],"to enter name of the extra parameter"))

                if submenue.tag == "paintExtraParamValue":
                    #BUG: ordering is not actually checked
                    valueToSet = ""
                    for (key,value) in self.extraInfo.items():
                        if (not key in submenue.extraInfo["item"].paintExtraInfo) or (not value == submenue.extraInfo["item"].paintExtraInfo[key]):
                            valueToSet = value

                    if valueToSet == submenue.text:
                        return (None,(["enter"],"to set the value of the extra parameter"))

                    correctIndex = 0
                    while correctIndex < len(valueToSet) and correctIndex < len(submenue.text):
                        if not valueToSet[correctIndex] == submenue.text[correctIndex]:
                            break
                        correctIndex += 1

                    if correctIndex < len(submenue.text):
                        return (None,(["backspace"],"to delete input"))

                    return (None,(valueToSet[correctIndex:],"to enter value of the extra parameter"))

            rooms = character.getTerrain().getRoomByPosition(self.targetPositionBig)
            if not rooms:
                if not dryRun:
                    self.fail("target room missing")
                return (None,None)
            room = rooms[0]

            if self.stockpileType == "i":
                for inputSlot in room.inputSlots:
                    if inputSlot[0] == self.targetPosition and inputSlot[1] == self.itemType:
                        if not dryRun:
                            self.postHandler()
                        return (None,None)
            if self.stockpileType == "o":
                for outputSlot in room.outputSlots:
                    if outputSlot[0] == self.targetPosition and outputSlot[1] == self.itemType:
                        if not dryRun:
                            self.postHandler()
                        return (None,None)
            if self.stockpileType == "s":
                for storageSlot in room.storageSlots:
                    if storageSlot[0] == self.targetPosition and storageSlot[1] == self.itemType:
                        if not dryRun:
                            self.postHandler()
                        return (None,None)

            if not character.inventory or not character.inventory[-1].type == "Painter":
                quest = src.quests.questMap["FetchItems"](toCollect="Painter",amount=1)
                return ([quest],None)

            item = character.inventory[-1]

            if not self.targetPositionBig == character.getBigPosition():
                quest = src.quests.questMap["GoToTile"](targetPosition=self.targetPositionBig,reason="go to the tile the stockpile should be drawn on")
                return ([quest],None)
            if character.getDistance(self.targetPosition) > 0:
                quest = src.quests.questMap["GoToPosition"](targetPosition=self.targetPosition,reason="get to the drawing spot")
                return ([quest],None)

            offsets = ((0,0,0),(0,1,0),(1,0,0),(0,-1,0),(-1,0,0))
            foundOffset = None
            for offset in offsets:
                if character.getPosition(offset=offset) == self.targetPosition:
                    foundOffset = offset

            if self.stockpileType == "i" and not item.paintMode == "inputSlot":
                return (None,(["C","i","m","i","enter"],"to configure the painter to input stockpile"))
            if self.stockpileType == "o" and not item.paintMode == "outputSlot":
                return (None,(["C","i","m","o","enter"],"to configure the painter to output stockpile"))
            if self.stockpileType == "s" and not item.paintMode == "storageSlot":
                return (None,(["C","i","m","s","enter"],"to configure the painter to storage stockpile"))
            if not (self.itemType == item.paintType):
                if self.itemType:
                    return (None,(["C","i","t"] + list(self.itemType) + ["enter"],"to configure the item type for the stockpile"))
                else:
                    return (None,(["C","i","t"] + ["enter"],"to remove the item type for the stockpile"))

            for (key,value) in item.paintExtraInfo.items():
                if not key in self.extraInfo:
                    return (None,(["C","i","c"],"to clear the painters extra info"))

            for (key,value) in self.extraInfo.items():
                if (not key in item.paintExtraInfo) or (not value == item.paintExtraInfo[key]):
                    return (None,(["C","i","e",key,"enter",value,"enter"],"to clear the painters extra info"))

            if not (item.offset == (0,0,0)):
                return (None,(["C","i","d","."] + ["enter"],"to remove the offset from the painter"))

            return (None,("Ji","draw to stockpile"))

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

    def handleDrewMarking(self,extraInfo):
        if not self.active:
            return
        if self.completed:
            1/0

        self.triggerCompletionCheck(self.character)

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.handleDrewMarking, "drew marking")

        return super().assignToCharacter(character)


src.quests.addType(DrawStockpile)

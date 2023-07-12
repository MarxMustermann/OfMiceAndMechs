import src
import random

class FetchItems(src.quests.MetaQuestSequence):
    type = "FetchItems"

    def __init__(self, description="fetch items", creator=None, targetPosition=None, toCollect=None, amount=None, returnToTile=True,lifetime=None,takeAnyUnbolted=False,tryHard=False,reason=None):
        questList = []
        super().__init__(questList, creator=creator,lifetime=lifetime)
        self.metaDescription = description
        self.amount = amount
        self.toCollect = None
        self.returnToTile = True
        self.tileToReturnTo = None
        self.collectedItems = False
        self.takeAnyUnbolted = takeAnyUnbolted
        self.tryHard = tryHard
        self.reason = reason

        if toCollect:
            self.setParameters({"toCollect":toCollect})
        if amount:
            self.setParameters({"amount":amount})
        if returnToTile:
            self.setParameters({"returnToTile":returnToTile})

        self.attributesToStore.append("toCollect")
        self.attributesToStore.append("amount")
        self.attributesToStore.append("returnToTile")
        self.tuplesToStore.append("tileToReturnTo")

        self.shortCode = "f"

    def generateTextDescription(self):
        reason = ""
        if self.reason:
            reason = ", to %s"%(self.reason,)

        if not self.amount:
            text = """
Fetch an inventory full of %ss%s.
"""%(self.toCollect,reason,)
        else:
            extraS = "s"
            if self.amount == 1:
                extraS = ""
            text = """
Fetch %s %s%s%s.
"""%(self.amount,self.toCollect,extraS,reason,)

        if self.takeAnyUnbolted:
            text += """
Take any fitting unbolted item.
"""
        else:
            text += """
Only take items from stockpiles.
"""

        if self.returnToTile:
            tile = self.tileToReturnTo
            if not tile:
                tile = "this tile"
            text += """
Return to %s after to complete this quest.
"""%(tile,)

        if self.tryHard:
            text += """
Try as hard as you can to achieve this.
If you don't find a source, produce new items.
"""

        return text

    def pickedUpItem(self,extraInfo):
        self.triggerCompletionCheck(extraInfo[0])

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.pickedUpItem, "itemPickedUp")
        return super().assignToCharacter(character)

    def setParameters(self,parameters):
        if "toCollect" in parameters and "toCollect" in parameters:
            self.toCollect = parameters["toCollect"]
            self.metaDescription += " "+self.toCollect
        if "amount" in parameters and "amount" in parameters:
            self.amount = parameters["amount"]
        if "returnToTile" in parameters and "returnToTile" in parameters:
            self.returnToTile = parameters["returnToTile"]
        return super().setParameters(parameters)

    def getRequiredParameters(self):
        parameters = super().getRequiredParameters()
        parameters.append({"name":"toCollect","type":"itemType"})
        return parameters

    def triggerCompletionCheck(self,character=None):

        if not character:
            return

        if self.amount:
            numItems = 0
            for item in reversed(character.inventory):
                if not item.type == self.toCollect:
                    break
                numItems += 1

            if numItems >= self.amount:
                self.collectedItems = True

        if character.getFreeInventorySpace() <= 0 and character.inventory[-1].type == self.toCollect:
            self.collectedItems = True

        if self.collectedItems:
            self.postHandler()
            return

        if isinstance(character.container,src.rooms.Room):
            outputSlots = character.container.getNonEmptyOutputslots(itemType=self.toCollect)
            random.shuffle(outputSlots)
            if outputSlots:
                return

            if self.getSource():
                return
        return

    def unhandledSubQuestFail(self,extraParam):
        self.fail(extraParam["reason"])

    def getSource(self):
        if not isinstance(self.character.container,src.rooms.Room):
            return None

        source = None
        for room in self.character.getTerrain().rooms:
            if room.getNonEmptyOutputslots(itemType=self.toCollect):
                return (room.getPosition(),)

        if self.takeAnyUnbolted:
            for room in self.character.getTerrain().rooms:
                for item in room.itemsOnFloor:
                    if item.bolted == False and item.type == self.toCollect:
                        return (room.getPosition(),)

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

    def getNextStep(self, character):
        if self.subQuests:
            return (None,None)

        if character.getFreeInventorySpace() <= 0:
            quest = src.quests.questMap["ClearInventory"](reason="be able to store items")
            return ([quest],None)

        if self.amount:
            numItemsCollected = 0
            for item in reversed(character.inventory):
                if not item.type == self.toCollect:
                    break
                numItemsCollected += 1

            if character.getFreeInventorySpace() < self.amount-numItemsCollected:
                quest = src.quests.questMap["ClearInventory"](reason="be able to store the needed amount of items")
                return ([quest],None)

        if self.collectedItems and self.tileToReturnTo:
            charPos = None
            if isinstance(character.container,src.rooms.Room):
                charPos = (character.container.xPosition,character.container.yPosition,0)
            else:
                charPos = (character.xPosition//15,character.yPosition//15,0)
            if not charPos == self.tileToReturnTo:
                quest = src.quests.questMap["GoToTile"](targetPosition=self.tileToReturnTo,reason="return where you came from")
                self.tileToReturnTo = None
                return ([quest],None)

        if not self.collectedItems:
            if not isinstance(character.container,src.rooms.Room):
                quest = src.quests.questMap["GoHome"](reason="orient yourself")
                return ([quest],None)
            room = character.container
            outputSlots = room.getNonEmptyOutputslots(itemType=self.toCollect)
            foundItem = False
            if outputSlots:
                foundItem = True
                offsets = [(0,0,0),(1,0,0),(0,1,0),(-1,0,0),(0,-1,0)]
                foundDirection = None
                for outputSlot in outputSlots:
                    if character.getDistance(outputSlot[0]) < 2:
                        for offset in offsets:
                            if character.getPosition(offset=offset) == outputSlot[0]:
                                foundDirection = offset

                if foundDirection:
                    if foundDirection == (0,0,0):
                        return (None,("K.","pick up item"))
                    if foundDirection == (1,0,0):
                        return (None,("Kd","pick up item"))
                    if foundDirection == (-1,0,0):
                        return (None,("Ka","pick up item"))
                    if foundDirection == (0,1,0):
                        return (None,("Ks","pick up item"))
                    if foundDirection == (0,-1,0):
                        return (None,("Kw","pick up item"))

                outputSlot = random.choice(outputSlots)
                quest = src.quests.questMap["GoToPosition"](targetPosition=outputSlot[0],ignoreEndBlocked=True,description="go to "+self.toCollect,reason="be able to pick up the %s"%(self.toCollect,))
                return ([quest],None)

            elif self.takeAnyUnbolted:
                candidates = []

                if character.container.isRoom:
                    for item in character.container.itemsOnFloor:
                        if item.bolted == False and item.type == self.toCollect:
                            candidates.append(item)

                if not candidates:
                    for room in character.getTerrain().rooms:
                        for item in room.itemsOnFloor:
                            if item.bolted == False and item.type == self.toCollect:
                                candidates.append(item)

                if candidates:
                    foundItem = True
                    offsets = [(0,0,0),(1,0,0),(0,1,0),(-1,0,0),(0,-1,0)]
                    foundDirection = None
                    for item in candidates:
                        if character.getDistance(item.getPosition()) < 2:
                            for offset in offsets:
                                if character.getPosition(offset=offset) == item.getPosition():
                                    if item.container == character.container:
                                        foundDirection = offset

                    if foundDirection:
                        if foundDirection == (0,0,0):
                            return (None,("K.","pick up item"))
                        if foundDirection == (1,0,0):
                            return (None,("Kd","pick up item"))
                        if foundDirection == (-1,0,0):
                            return (None,("Ka","pick up item"))
                        if foundDirection == (0,1,0):
                            return (None,("Ks","pick up item"))
                        if foundDirection == (0,-1,0):
                            return (None,("Kw","pick up item"))

                    item = random.choice(candidates)
                    quests = []
                    quests.append(src.quests.questMap["GoToPosition"](targetPosition=item.getPosition(),ignoreEndBlocked=True,description="go to "+self.toCollect,reason="be able to pick up the %s"%(self.toCollect,)))
                    if not character.container == item.container:
                        quests.append(src.quests.questMap["GoToTile"](targetPosition=item.container.getPosition(),description="go to "+self.toCollect+" source",reason="reach a source for %s"%(self.toCollect,)))
                    return (quests,None)
            else:
                source = self.getSource()
                if source:
                    quest = src.quests.questMap["GoToTile"](targetPosition=source[0],reason="reach a source for %s"%(self.toCollect,))
                    if self.returnToTile:
                        self.tileToReturnTo = (room.xPosition,room.yPosition,0)
                    return ([quest],None)

            if not foundItem:
                if self.tryHard:
                    if self.toCollect == "Scrap":
                        quest = src.quests.questMap["GatherScrap"](reason="have items to fetch")
                        return ([quest],None)
                    else:
                        quest = src.quests.questMap["ProduceItem"](itemType=self.toCollect,tryHard=self.tryHard,reason="have items to fetch")
                        self.startWatching(quest,self.unhandledSubQuestFail,"failed")
                        return ([quest],None)

                self.fail(reason="no source for item %s"%(self.toCollect,))
                return (None,None)
        return (None,None)

    def getSolvingCommandString(self, character, dryRun=True):
        nextStep = self.getNextStep(character)
        if nextStep == (None,None):
            return super().getSolvingCommandString(character)
        return self.getNextStep(character)[1]

src.quests.addType(FetchItems)

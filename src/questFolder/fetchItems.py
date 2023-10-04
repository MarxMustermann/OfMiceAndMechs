import random

import src


class FetchItems(src.quests.MetaQuestSequence):
    type = "FetchItems"

    def __init__(self, description="fetch items", creator=None, toCollect=None, amount=None, returnToTile=True,lifetime=None,takeAnyUnbolted=False,tryHard=False,reason=None):
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

        self.shortCode = "f"

    def generateTextDescription(self):
        reason = ""
        if self.reason:
            reason = f", to {self.reason}"

        if not self.amount:
            text = f"""
Fetch an inventory full of {self.toCollect}s{reason}.
"""
        else:
            extraS = "s"
            if self.amount == 1:
                extraS = ""
            text = f"""
Fetch {self.amount} {self.toCollect}{extraS}{reason}.
"""

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
            text += f"""
Return to {tile} after to complete this quest.
"""

        if self.tryHard:
            text += """
Try as hard as you can to achieve this.
If you don't find a source, produce new items.
"""

        out = [text]
        if not self.subQuests:
            out.append((src.interaction.urwid.AttrSpec("#f00", "black"),"""
This quest has no subquests. Press r to generate subquests for this quest."""))
        else:
            out.append((src.interaction.urwid.AttrSpec("#080", "black"),"""
This quests has subquests.
Press d to move the cursor and show the subquests description.
"""))

        return out

    def pickedUpItem(self,extraInfo):
        self.triggerCompletionCheck(extraInfo[0])

    def assignToCharacter(self, character):
        if self.character:
            return None

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
                if item.type != self.toCollect:
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
        if self.triggerCompletionCheck(character):
            return

        (nextQuests,nextCommand) = self.getNextStep(character,dryRun=False)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
            return

        if nextCommand:
            character.runCommandString(nextCommand[0])
            return
        super().solver(character)

    def getNextStep(self, character,dryRun=True,ignoreCommands=False):
        if self.subQuests:
            return (None,None)

        if not self.amount:
            numItemsCollected = 0
            for item in reversed(character.inventory):
                if item.type != self.toCollect:
                    break
                numItemsCollected += 1
            if (numItemsCollected+character.getFreeInventorySpace()) < 5:
                quest = src.quests.questMap["ClearInventory"](reason="be able to store the needed amount of items")
                if not dryRun:
                    self.startWatching(quest,self.unhandledSubQuestFail,"failed")
                return ([quest],None)

        if self.amount:
            numItemsCollected = 0
            for item in reversed(character.inventory):
                if item.type != self.toCollect:
                    break
                numItemsCollected += 1

            if character.getFreeInventorySpace() < self.amount-numItemsCollected:
                quest = src.quests.questMap["ClearInventory"](reason="be able to store the needed amount of items")
                if not dryRun:
                    self.startWatching(quest,self.unhandledSubQuestFail,"failed")
                return ([quest],None)

        if self.collectedItems and self.tileToReturnTo:
            charPos = None
            if isinstance(character.container,src.rooms.Room):
                charPos = (character.container.xPosition,character.container.yPosition,0)
            else:
                charPos = (character.xPosition//15,character.yPosition//15,0)
            if charPos != self.tileToReturnTo:
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
                quest = src.quests.questMap["GoToPosition"](targetPosition=outputSlot[0],ignoreEndBlocked=True,description="go to "+self.toCollect,reason=f"be able to pick up the {self.toCollect}")
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
                    quests.append(src.quests.questMap["GoToPosition"](targetPosition=item.getPosition(),ignoreEndBlocked=True,description="go to "+self.toCollect,reason=f"be able to pick up the {self.toCollect}"))
                    if character.container != item.container:
                        quests.append(src.quests.questMap["GoToTile"](targetPosition=item.container.getPosition(),description="go to "+self.toCollect+" source",reason=f"reach a source for {self.toCollect}"))
                    return (quests,None)
            else:
                source = self.getSource()
                if source:
                    quest = src.quests.questMap["GoToTile"](targetPosition=source[0],reason=f"reach a source for {self.toCollect}")
                    if self.returnToTile:
                        self.tileToReturnTo = (room.xPosition,room.yPosition,0)
                    return ([quest],None)

            if not foundItem:
                if self.toCollect == "Scrap":
                    if self.tryHard:
                        quest = src.quests.questMap["GatherScrap"](reason="have items to fetch")
                        return ([quest],None)
                else:
                    if "metal working" in self.character.duties:
                        if self.toCollect not in ("MetalBars","Scrap",):
                            newQuest = src.quests.questMap["MetalWorking"](toProduce=self.toCollect,amount=1,reason="produce a item you do not have",produceToInventory=True)
                            return ([newQuest],None)
                    if self.tryHard:
                        quest = src.quests.questMap["ProduceItem"](itemType=self.toCollect,tryHard=self.tryHard,reason="have items to fetch")
                        return ([quest],None)

                if not dryRun:
                    self.fail(reason=f"no source for item {self.toCollect}")
                return (None,None)
        return (None,None)

    def generateSubquests(self, character=None):
        (nextQuests,nextCommand) = self.getNextStep(character,ignoreCommands=True)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
            return

    def getSolvingCommandString(self, character, dryRun=True):
        nextStep = self.getNextStep(character)
        if nextStep == (None,None):
            return super().getSolvingCommandString(character)
        return self.getNextStep(character)[1]

src.quests.addType(FetchItems)

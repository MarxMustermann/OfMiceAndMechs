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
                    if item.bolted is False and item.type == self.toCollect:
                        return (room.getPosition(),)
            return None
        return None

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
                quest = src.quests.questMap["ClearInventory"](reason="be able to store the needed amount of items",returnToTile=False)
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
                quest = src.quests.questMap["ClearInventory"](reason="be able to store the needed amount of items",returnToTile=False)
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

            if self.takeAnyUnbolted:
                candidates = []

                if character.container.isRoom:
                    for item in character.container.itemsOnFloor:
                        if item.bolted is False and item.type == self.toCollect:
                            candidates.append(item)

                if not candidates:
                    for room in character.getTerrain().rooms:
                        for item in room.itemsOnFloor:
                            if item.bolted is False and item.type == self.toCollect:
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
                    #if "metal working" in self.character.duties:
                    #    if self.toCollect not in ("MetalBars","Scrap",):
                    #        newQuest = src.quests.questMap["MetalWorking"](toProduce=self.toCollect,amount=1,reason="produce a item you do not have",produceToInventory=True)
                    #        return ([newQuest],None)
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
    @staticmethod
    def generateDutyQuest(beUsefull,character,currentRoom):

        for trueInput in (True,False):
            for room in beUsefull.getRandomPriotisedRooms(character,currentRoom):
                checkedTypes = set()
                emptyInputSlots = room.getEmptyInputslots(allowStorage=(not trueInput),allowAny=True)

                if emptyInputSlots:

                    for inputSlot in random.sample(list(emptyInputSlots),len(emptyInputSlots)):
                        if inputSlot[1] is None:
                            items = room.getItemByPosition(inputSlot[0])
                            if items:
                                inputSlot = (inputSlot[0],items[0].type,inputSlot[2])
                        if inputSlot[1] in checkedTypes:
                            continue
                        checkedTypes.add(inputSlot[1])

                        hasItem = False
                        if character.inventory and (character.inventory[-1].type == inputSlot[1] or not inputSlot[1]):
                            hasItem = True

                        if not hasItem:
                            allowStorage = trueInput
                            if inputSlot[2].get("desiredState") == "filled":
                                allowStorage = True

                            source = None
                            for candidateSource in room.sources:
                                if candidateSource[1] != inputSlot[1]:
                                    continue

                                sourceRoom = room.container.getRoomByPosition(candidateSource[0])
                                if not sourceRoom:
                                    continue

                                sourceRoom = sourceRoom[0]
                                if sourceRoom == character.container:
                                    continue
                                if not sourceRoom.getNonEmptyOutputslots(itemType=inputSlot[1],allowStorage=allowStorage):
                                    continue

                                source = candidateSource
                                break

                            if not source:
                                for otherRoom in random.sample(character.getTerrain().rooms,len(character.getTerrain().rooms)):
                                    if otherRoom == room:
                                        continue

                                    outputSlots = otherRoom.getNonEmptyOutputslots(itemType=inputSlot[1],allowStorage=allowStorage,)
                                    if not outputSlots:
                                        continue

                                    source = (otherRoom.getPosition(),inputSlot[1],outputSlots)
                                    break

                            if not source:
                                continue

                        if not hasItem and src.quests.questMap["ClearInventory"].generateDutyQuest(beUsefull,character,room):
                            beUsefull.idleCounter = 0
                            return True

                        if trueInput:
                            beUsefull.addQuest(src.quests.questMap["RestockRoom"](toRestock=inputSlot[1],reason="restock the room with the items fetched1",allowAny=True,targetPositionBig=room.getPosition()))
                        else:
                            if hasItem:
                                beUsefull.addQuest(src.quests.questMap["RestockRoom"](toRestock=character.inventory[-1].type,reason="restock the room with the items fetched2",allowAny=True,targetPositionBig=room.getPosition()))
                                beUsefull.idleCounter = 0
                                return True

                        if not hasItem:
                            if trueInput:
                                amountToFetch = None
                                if src.gamestate.gamestate.mainChar == character:
                                    walkable = False
                                    if inputSlot[1] in src.items.itemMap:
                                        walkable = src.items.itemMap[inputSlot[1]]().walkable
                                    amountNeeded = 0
                                    for checkInputSlot in emptyInputSlots:
                                        if checkInputSlot[1] == inputSlot[1]:
                                            if walkable:
                                                amountNeeded += 20-len(room.getItemByPosition(inputSlot[0]))
                                            else:
                                                amountNeeded += 1

                                    if amountNeeded < character.maxInventorySpace:
                                        amountToFetch = amountNeeded

                                roomPos = (room.xPosition,room.yPosition,0)
                                if source[0] != roomPos:
                                    beUsefull.addQuest(src.quests.questMap["GoToTile"](targetPosition=roomPos))

                                beUsefull.addQuest(src.quests.questMap["FetchItems"](toCollect=inputSlot[1], amount=amountToFetch))
                                if source[0] != roomPos:
                                    beUsefull.addQuest(src.quests.questMap["GoToTile"](targetPosition=(source[0])))

                                if character.inventory and (not amountToFetch or amountToFetch > character.getFreeInventorySpace()):
                                    beUsefull.addQuest(src.quests.questMap["ClearInventory"](returnToTile=False))
                            else:
                                roomPos = (room.xPosition,room.yPosition,0)
                                if source[0] != roomPos:
                                    beUsefull.addQuest(src.quests.questMap["GoToTile"](targetPosition=roomPos))

                                beUsefull.addQuest(src.quests.questMap["CleanSpace"](targetPositionBig=source[0],targetPosition=source[2][0][0]))
                                beUsefull.idleCounter = 0
                                return True



                        beUsefull.idleCounter = 0
                        return True

        for room in beUsefull.getRandomPriotisedRooms(character,currentRoom):
            checkedTypes = set()
            for storageSlot in room.storageSlots:
                if storageSlot[2].get("desiredState") != "filled":
                    continue

                items = room.getItemByPosition(storageSlot[0])
                if items and (not items[0].walkable or len(items) >= 20):
                    continue

                for otherRoom in beUsefull.getRandomPriotisedRooms(character,currentRoom):
                    if otherRoom == room:
                        continue
                    for checkStorageSlot in otherRoom.storageSlots:
                        if checkStorageSlot[1] == storageSlot[1] or not checkStorageSlot[1]:
                            items = otherRoom.getItemByPosition(checkStorageSlot[0])
                            if checkStorageSlot[2].get("desiredState") == "filled":
                                continue
                            if not items or items[0].type != storageSlot[1]:
                                continue

                            beUsefull.addQuest(src.quests.questMap["RestockRoom"](targetPositionBig=room.getPosition(),targetPosition=storageSlot[0],allowAny=True,toRestock=items[0].type,reason="fill a storage stockpile designated to be filled"))
                            beUsefull.addQuest(src.quests.questMap["CleanSpace"](targetPositionBig=otherRoom.getPosition(),targetPosition=checkStorageSlot[0],reason="fill a storage stockpile designated to be filled",abortOnfullInventory=True))
                            if character.inventory:
                                beUsefull.addQuest(src.quests.questMap["ClearInventory"]())
                            beUsefull.idleCounter = 0
                            return True
        return None
src.quests.addType(FetchItems)

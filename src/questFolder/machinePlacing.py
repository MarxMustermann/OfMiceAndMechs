import src
import random

class MachinePlacing(src.quests.MetaQuestSequence):
    type = "MachinePlacing"

    def __init__(self, description="place machines", creator=None, targetPosition=None,toRestock=None,allowAny=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        self.shortCode = "d"
        self.targetPosition = targetPosition

    def triggerCompletionCheck(self,character=None):
        if not character:
            return

    def getNextStep(self,character=None,ignoreCommands=False):
        if not self.subQuests:

            if not isinstance(character.container,src.rooms.Room):
                command = None
                if character.xPosition%15 == 0:
                    command = "d"
                if character.xPosition%15 == 14:
                    command = "a"
                if character.yPosition%15 == 0:
                    command = "s"
                if character.yPosition%15 == 14:
                    command = "w"
                if command:
                    return (None,(command,"enter tile"))

            1/0
            if not character.container.floorPlan:
                self.fail()
                return None

            if character.getBigPosition() != self.targetPosition:
                quest = src.quests.questMap["GoToTile"](targetPosition=self.targetPosition)
                return ([quest],None)

            if "walkingSpace" in character.container.floorPlan:
                walkingSpaces = character.container.floorPlan.get("walkingSpace")
                if walkingSpaces and walkingSpaces[-1] in character.container.walkingSpace:
                    walkingSpaces.pop()

                if walkingSpaces:
                    quest = src.quests.questMap["DrawWalkingSpace"](tryHard=True,targetPositionBig=self.targetPosition,targetPosition=walkingSpaces[-1])
                    return ([quest],None)

                if walkingSpaces is not None:
                    del character.container.floorPlan["walkingSpace"]

            if "inputSlots" in character.container.floorPlan:
                inputSlots = character.container.floorPlan.get("inputSlots")
                if inputSlots:
                    for existingInputslot in character.container.inputSlots:
                        if existingInputslot[0] == inputSlots[-1][0]:
                            inputSlots.pop()
                            break

                    if inputSlots:
                        inputSlot = inputSlots[-1]
                        quest = src.quests.questMap["DrawStockpile"](itemType=inputSlot[1],stockpileType="i",targetPositionBig=self.targetPosition,targetPosition=inputSlot[0])
                        return ([quest],None)

                if inputSlots is not None:
                    del character.container.floorPlan["inputSlots"]

            if "outputSlots" in character.container.floorPlan:
                outputSlots = character.container.floorPlan.get("outputSlots")
                if outputSlots:
                    for existingOutputSlot in character.container.outputSlots:
                        if existingOutputSlot[0] == outputSlots[-1][0]:
                            outputSlots.pop()
                            break

                    if outputSlots:
                        outputSlot = outputSlots[-1]
                        quest = src.quests.questMap["DrawStockpile"](itemType=outputSlot[1],stockpileType="o",targetPositionBig=self.targetPosition,targetPosition=outputSlot[0])
                        return ([quest],None)

                if outputSlots is not None:
                    del character.container.floorPlan["outputSlots"]

            if "buildSites" in character.container.floorPlan:
                buildSites = character.container.floorPlan.get("buildSites")

                if buildSites:
                    for existingBuildSite in character.container.buildSites:
                        if existingBuildSite[0] == buildSites[-1][0]:
                            buildSites.pop()
                            break

                    if buildSites:
                        buildSite = buildSites[-1]
                        quest = src.quests.questMap["DrawBuildSite"](itemType=buildSite[1],targetPositionBig=self.targetPosition,targetPosition=buildSite[0],extraInfo=buildSite[2])
                        return ([quest],None)

                if buildSites is not None:
                    del character.container.floorPlan["buildSites"]

            self.postHandler()
            return (None,None)
        return (None,None)

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

    def solver(self, character):
        if self.triggerCompletionCheck(character):
            return
        (nextQuests,nextCommand) = self.getNextStep(character)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
            return

        if nextCommand:
            character.runCommandString(nextCommand[0])
            return
        super().solver(character)

    @staticmethod
    def generateDutyQuest(beUsefull,character,currentRoom):
        terrain = character.getTerrain()
        produceQuest = None
        for room in beUsefull.getRandomPriotisedRooms(character,currentRoom):
            if (not room.floorPlan) and room.buildSites:
                checkedMaterial = set()
                for buildSite in random.sample(room.buildSites,len(room.buildSites)):
                    if buildSite[1] in checkedMaterial:
                        continue
                    checkedMaterial.add(buildSite[1])

                    if buildSite[1] == "Machine":
                        lastCheck = character.grievances.get(("SetUpMachine",buildSite[2]["toProduce"],"no machine"),0)
                        if lastCheck+10 > src.gamestate.gamestate.tick:
                            continue

                    neededItem = buildSite[1]
                    if buildSite[1] == "Command":
                        neededItem = "Sheet"
                    hasItem = False
                    source = None
                    if character.inventory and character.inventory[-1].type == neededItem:
                        hasItem = True

                    if buildSite[1] == "Machine":
                        quest = src.quests.questMap["SetUpMachine"](itemType=buildSite[2]["toProduce"],targetPositionBig=room.getPosition(),targetPosition=buildSite[0])
                        beUsefull.addQuest(quest)
                        beUsefull.startWatching(quest,beUsefull.registerDutyFail,"failed")
                        beUsefull.idleCounter = 0
                        return True


                    if not hasItem:
                        for candidateSource in room.sources:
                            if candidateSource[1] != neededItem:
                                continue

                            sourceRoom = room.container.getRoomByPosition(candidateSource[0])
                            if not sourceRoom:
                                continue

                            sourceRoom = sourceRoom[0]
                            if not sourceRoom.getNonEmptyOutputslots(itemType=neededItem):
                                continue

                            source = candidateSource
                            break

                        if not source:
                            for checkRoom in random.sample(character.getTerrain().rooms,len(character.getTerrain().rooms)):
                                if not checkRoom.getNonEmptyOutputslots(itemType=neededItem):
                                    continue

                                source = (checkRoom.getPosition(),neededItem)
                                break

                        if not source:
                            continue
                        """
                        if not source:
                            if buildSite[1] not in ("Machine","Command") and "metal working" in character.duties:
                                self.addQuest(src.quests.questMap["PlaceItem"](itemType=buildSite[1],targetPositionBig=room.getPosition(),targetPosition=buildSite[0],boltDown=True))
                                self.idleCounter = 0
                                return True

                            if buildSite[1] == "Machine":
                                self.addQuest(src.quests.questMap["SetUpMachine"](itemType=buildSite[2]["toProduce"],targetPositionBig=room.getPosition(),targetPosition=buildSite[0]))
                                self.idleCounter = 0
                                return True

                            continue
                        """

                    if buildSite[1] != "Command":
                        beUsefull.addQuest(src.quests.questMap["PlaceItem"](itemType=buildSite[1],targetPositionBig=room.getPosition(),targetPosition=buildSite[0],boltDown=True))
                        beUsefull.idleCounter = 0
                        return True

                    if hasItem:
                        if buildSite[1] == "Command":
                            if "command" in buildSite[2]:
                                beUsefull.addQuest(src.quests.questMap["RunCommand"](command="jjssj%s\n"%(buildSite[2]["command"])))
                            else:
                                beUsefull.addQuest(src.quests.questMap["RunCommand"](command="jjssj.\n"))
                        beUsefull.addQuest(src.quests.questMap["RunCommand"](command="lcb"))
                        beUsefull.addQuest(src.quests.questMap["GoToPosition"](targetPosition=buildSite[0]))
                        buildSite[2]["reservedTill"] = room.timeIndex+100
                        beUsefull.addQuest(src.quests.questMap["GoToTile"](targetPosition=room.getPosition()))
                        #self.addQuest(produceQuest)
                        beUsefull.idleCounter = 0
                        return True
                    elif source:
                        if not character.getFreeInventorySpace() > 0:
                            quest = src.quests.questMap["ClearInventory"]()
                            beUsefull.addQuest(quest)
                            quest.assignToCharacter(character)
                            quest.activate()
                            beUsefull.idleCounter = 0
                            return True

                        roomPos = (room.xPosition,room.yPosition)

                        if source[0] != roomPos:
                            beUsefull.addQuest(src.quests.questMap["GoToTile"](targetPosition=(roomPos[0],roomPos[1],0)))
                        beUsefull.addQuest(src.quests.questMap["FetchItems"](toCollect=neededItem,amount=1))
                        beUsefull.idleCounter = 0
                        return True

        # spawn city planer if there is none
        terrain = character.getTerrain()
        cityCore = terrain.getRoomByPosition((7,7,0))[0]
        cityPlaner = cityCore.getItemByType("CityPlaner",needsBolted=True)

        """
        if not cityPlaner:
            itemsInStorage = {}
            freeStorage = 0
            for room in character.getTerrain().rooms:
                for storageSlot in room.storageSlots:
                    items = room.getItemByPosition(storageSlot[0])
                    if not items:
                        freeStorage += 1
                    for item in items:
                        itemsInStorage[item.type] = itemsInStorage.get(item.type,0)+1

            if itemsInStorage.get("CityPlaner") or "metal working" in character.duties:
                quest = src.quests.questMap["PlaceItem"](targetPositionBig=(7,7,0),targetPosition=(4,1,0),itemType="CityPlaner",tryHard=True,boltDown=True,reason="have it to plan the city with")
                self.addQuest(quest)
                return True
        """

        # spawn basic items, if not there
        foundPlacedItems = {}
        foundPlacedMachines = {}
        terrain = character.getTerrain()
        for room in terrain.rooms:
            for item in room.itemsOnFloor:
                if not item.bolted:
                    continue

                if item.type not in foundPlacedItems:
                    foundPlacedItems[item.type] = []
                foundPlacedItems[item.type].append(item)

        if cityPlaner:
            checkItems = ["ScrapCompactor","MaggotFermenter","BioPress","GooProducer"]
            checkItems = ["ScrapCompactor"]
            for checkItem in checkItems:
                if checkItem in foundPlacedItems:
                    continue

                for generalPurposeRoom in cityPlaner.generalPurposeRooms:

                    terrain = beUsefull.character.getTerrain()
                    room = terrain.getRoomByPosition(generalPurposeRoom)[0]

                    validTargetPosition = False
                    terrain = character.getTerrain()
                    counter = 0
                    while not validTargetPosition and counter < 10:
                        counter += 1
                        targetPosition = (random.randint(3,9),random.randint(3,9),0)

                        offsetBlocked = False
                        for offset in [(-1,0,0),(1,0,0),(0,-1,0),(0,1,0),(0,0,0)]:
                            checkPos = (targetPosition[0]+offset[0],targetPosition[1]+offset[1],0)
                            if room.getItemByPosition(checkPos) or room.getPaintedByPosition(checkPos):
                                offsetBlocked = True
                                break

                        if offsetBlocked:
                            continue

                        validTargetPosition = True
                        break

                    if validTargetPosition:
                        quest = src.quests.questMap["PlaceItem"](targetPositionBig=room.getPosition(),targetPosition=targetPosition,itemType=checkItem,boltDown=True,reason="have at least one scrpa compactor")
                        beUsefull.addQuest(quest)
                        return True
            return None
        return None

src.quests.addType(MachinePlacing)

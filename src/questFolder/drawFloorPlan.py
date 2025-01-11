import random

import src


class DrawFloorPlan(src.quests.MetaQuestSequence):
    type = "DrawFloorPlan"

    def __init__(self, description="draw floor plan", creator=None, targetPosition=None,reason=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        self.shortCode = "d"
        self.targetPosition = targetPosition
        self.reason = reason

    def generateTextDescription(self):
        out = []
        reason = ""
        if self.reason:
            reason = f",\nto {self.reason}"
        text = f"""
Draw a floor plan assigned to a room{reason}.

"""
        return out

    def triggerCompletionCheck(self,character=None):
        if not character:
            return

    def getNextStep(self,character=None,ignoreCommands=False,dryRun=True):
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
                    return (None,(command,"enter room"))

            if character.getBigPosition() != self.targetPosition:
                quest = src.quests.questMap["GoToTile"](targetPosition=self.targetPosition)
                return ([quest],None)

            if not character.container.floorPlan:
                if not dryRun:
                    self.fail()
                return (None,None)

            if "walkingSpace" in character.container.floorPlan:
                walkingSpaces = character.container.floorPlan.get("walkingSpace")
                if walkingSpaces and walkingSpaces[-1] in character.container.walkingSpace:
                    walkingSpaces.pop()

                quests = []
                counter = 0
                walkingSpaces = list(walkingSpaces)
                if len(walkingSpaces) > 1:
                    index = random.randint(0,len(walkingSpaces)-1)
                    walkingSpaces = walkingSpaces[index:]+walkingSpaces[:index]
                for walkingSpace in reversed(walkingSpaces):
                    if counter > 9:
                        break
                    counter += 1
                    quest = src.quests.questMap["DrawWalkingSpace"](tryHard=True,targetPositionBig=self.targetPosition,targetPosition=walkingSpace)
                    quests.append(quest)

                if quests:
                    return (list(reversed(quests)),None)

                if walkingSpaces is not None:
                    del character.container.floorPlan["walkingSpace"]

            if "outputSlots" in character.container.floorPlan:
                outputSlots = character.container.floorPlan.get("outputSlots")
                if outputSlots:
                    for existingOutputSlot in character.container.outputSlots:
                        if existingOutputSlot[0] == outputSlots[-1][0]:
                            outputSlots.pop()
                            break

                outputSlots = character.container.floorPlan.get("outputSlots")[:]
                if len(outputSlots) > 1:
                    index = random.randint(0,len(outputSlots)-1)
                    walkingSpaces = outputSlots[index:]+outputSlots[:index]
                if outputSlots:
                    quests = []
                    counter = 0
                    counter2 = 0
                    while counter < len(outputSlots):
                        if counter2 > 4:
                            break
                        outputSlot = outputSlots[counter]

                        counter += 1
                        counter2 += 1

                        quest = src.quests.questMap["DrawStockpile"](itemType=outputSlot[1],stockpileType="o",targetPositionBig=self.targetPosition,targetPosition=outputSlot[0])
                        quests.append(quest)

                        for outputSlot2 in outputSlots[counter:]:
                            if outputSlot[1] == outputSlot2[1]:
                                quest = src.quests.questMap["DrawStockpile"](itemType=outputSlot2[1],stockpileType="o",targetPositionBig=self.targetPosition,targetPosition=outputSlot2[0])
                                quests.append(quest)
                                outputSlots.remove(outputSlot2)
                                counter2 += 1

                    if quests:
                        return (list(reversed(quests)),None)

                if outputSlots is not None:
                    del character.container.floorPlan["outputSlots"]

            if "buildSites" in character.container.floorPlan:
                buildSites = character.container.floorPlan.get("buildSites")
                if buildSites:
                    for existingBuildSite in character.container.buildSites:
                        if existingBuildSite[0] == buildSites[-1][0]:
                            buildSites.pop()
                            break

                buildSites = character.container.floorPlan.get("buildSites")[:]
                if len(buildSites) > 1:
                    index = random.randint(0,len(buildSites)-1)
                    buildSites = buildSites[index:]+buildSites[:index]
                if buildSites:
                    quests = []
                    counter = 0
                    counter2 = 0
                    while counter < len(buildSites):
                        if counter2 > 4:
                            break
                        buildSite = buildSites[counter]

                        counter += 1
                        counter2 += 1

                        quest = src.quests.questMap["DrawBuildSite"](itemType=buildSite[1],targetPositionBig=self.targetPosition,targetPosition=buildSite[0],extraInfo=buildSite[2])
                        quests.append(quest)

                        for buildSite2 in buildSites[counter:]:
                            if buildSite[1] == buildSite2[1] and buildSite[2] == buildSite2[2]:
                                quest = src.quests.questMap["DrawBuildSite"](itemType=buildSite2[1],targetPositionBig=self.targetPosition,targetPosition=buildSite2[0],extraInfo=buildSite2[2])
                                quests.append(quest)
                                buildSites.remove(buildSite2)
                                counter2 += 1
                                if counter2 > 9:
                                    break

                    if quests:
                        return (list(reversed(quests)),None)

                    if buildSites:
                        buildSite = buildSites[-1]
                        quest = src.quests.questMap["DrawBuildSite"](itemType=buildSite[1],targetPositionBig=self.targetPosition,targetPosition=buildSite[0],extraInfo=buildSite[2])
                        return ([quest],None)

                if buildSites is not None:
                    del character.container.floorPlan["buildSites"]

            if "storageSlots" in character.container.floorPlan:
                storageSlots = character.container.floorPlan.get("storageSlots")
                if storageSlots:
                    for existingStorageSlot in character.container.storageSlots:
                        if existingStorageSlot[0] == storageSlots[-1][0]:
                            storageSlots.pop()
                            break

                storageSlots = character.container.floorPlan.get("storageSlots")[:]
                if len(storageSlots) > 1:
                    index = random.randint(0,len(storageSlots)-1)
                    storageSlots = storageSlots[index:]+storageSlots[:index]

                if storageSlots:
                    quests = []
                    counter = 0
                    counter2 = 0
                    while counter < len(storageSlots):
                        if counter2 > 4:
                            break
                        storageSlot = storageSlots[counter]

                        counter += 1
                        counter2 += 1

                        quest = src.quests.questMap["DrawStockpile"](itemType=storageSlot[1],stockpileType="s",targetPositionBig=self.targetPosition,targetPosition=storageSlot[0],extraInfo=storageSlot[2])
                        quests.append(quest)

                        for storageSlot2 in storageSlots[counter:]:
                            if storageSlot[1] == storageSlot2[1] and storageSlot[2] == storageSlot2[2]:
                                quest = src.quests.questMap["DrawStockpile"](itemType=storageSlot2[1],stockpileType="s",targetPositionBig=self.targetPosition,targetPosition=storageSlot2[0],extraInfo=storageSlot[2])
                                quests.append(quest)
                                storageSlots.remove(storageSlot2)
                                counter2 += 1

                                if counter2 > 9:
                                    break
                    if quests:
                        return (list(reversed(quests)),None)

                if storageSlots is not None:
                    del character.container.floorPlan["storageSlots"]

            if "inputSlots" in character.container.floorPlan:
                inputSlots = character.container.floorPlan.get("inputSlots")
                if inputSlots:
                    for existingInputslot in character.container.inputSlots:
                        if existingInputslot[0] == inputSlots[-1][0]:
                            inputSlots.pop()
                            break

                inputSlots = character.container.floorPlan.get("inputSlots")[:]
                random.shuffle(inputSlots)
                if inputSlots:
                    quests = []
                    counter = 0
                    counter2 = 0
                    while counter < len(inputSlots):
                        if counter2 > 4:
                            break
                        inputSlot = inputSlots[counter]

                        counter += 1
                        counter2 += 1

                        quest = src.quests.questMap["DrawStockpile"](itemType=inputSlot[1],stockpileType="i",targetPositionBig=self.targetPosition,targetPosition=inputSlot[0])
                        quests.append(quest)

                        for inputSlot2 in inputSlots[counter:]:
                            if inputSlot[1] == inputSlot2[1]:
                                quest = src.quests.questMap["DrawStockpile"](itemType=inputSlot2[1],stockpileType="i",targetPositionBig=self.targetPosition,targetPosition=inputSlot2[0])
                                quests.append(quest)
                                inputSlots.remove(inputSlot2)
                                counter2 += 1

                    if quests:
                        return (list(reversed(quests)),None)

                if inputSlots is not None:
                    del character.container.floorPlan["inputSlots"]

            if character.container.floorPlan:
                character.container.floorPlan = None

            if not dryRun:
                self.postHandler()
            return (None,None)
        return (None,None)

    @staticmethod
    def generateDutyQuest(beUsefull,character,currentRoom, dryRun):
        for room in beUsefull.getRandomPriotisedRooms(character,currentRoom):
            if room.floorPlan:
                quest = src.quests.questMap["DrawFloorPlan"](targetPosition=room.getPosition())
                if not dryRun:
                    beUsefull.idleCounter = 0
                return ([quest],None)

        terrain = character.getTerrain()
        numFreeStorage = 0
        for room in terrain.rooms:
            for storageSlot in room.storageSlots:
                items = room.getItemByPosition(storageSlot[0])
                if items:
                    continue
                if storageSlot[1] is not None:
                    continue
                if storageSlot[2] != {}:
                    continue
                numFreeStorage += 1

        if numFreeStorage < 10:
            cityPlaner = None
            rooms = terrain.getRoomByPosition((7,7,0))
            if rooms:
                room = rooms[0]
                cityPlaner = room.getItemByType("CityPlaner")

            if cityPlaner:
                for generalPurposeRoom in cityPlaner.generalPurposeRooms:

                    terrain = beUsefull.character.getTerrain()
                    room = terrain.getRoomByPosition(generalPurposeRoom)[0]
                    counter = 1
                    quests = []
                    for y in (1,3,5,7,9,11):
                        for x in range(1,12):
                            if x == 6:
                                continue
                            if counter > 15:
                                continue

                            if room.getItemByPosition((x,y,0)):
                                continue

                            if (x,y,0) in room.walkingSpace:
                                continue

                            blockedSpot = False
                            for storageSlot in room.storageSlots:
                                if storageSlot[0] == (x,y,0):
                                    blockedSpot = True
                                    break
                            for outputSlot in room.outputSlots:
                                if outputSlot[0] == (x,y,0):
                                    blockedSpot = True
                                    break
                            for inputSlot in room.inputSlots:
                                if inputSlot[0] == (x,y,0):
                                    blockedSpot = True
                                    break
                            for buildSite in room.buildSites:
                                if buildSite[0] == (x,y,0):
                                    blockedSpot = True
                                    break
                            if blockedSpot:
                                continue

                            counter += 1
                            quest = src.quests.questMap["DrawStockpile"](tryHard=True,itemType=None,stockpileType="s",targetPositionBig=generalPurposeRoom,targetPosition=(x,y,0),reason="extend the storage capacity temporarily")
                            quests.append(quest)
                    quests.reverse()
                    if quests:
                        return (quests,None)

        # get storage stockpiles that have the filled tag
        desireFilledStorageSlots = {}
        for room in character.getTerrain().rooms:
            if room.tag != "storage":
                continue
            for storageSlot in room.storageSlots:
                if storageSlot[2].get("desiredState") == "filled":
                    if storageSlot[1] not in desireFilledStorageSlots:
                        desireFilledStorageSlots[storageSlot[1]] = 0
                    desireFilledStorageSlots[storageSlot[1]] += 1


        # check rules to add more to be filled storage slots
        checkDesireFilledStorageSlots = [("Wall",10),("Door",5),("MetalBars",3)]
        for checkDesireFilledStorageSlot in checkDesireFilledStorageSlots:
            if desireFilledStorageSlots.get(checkDesireFilledStorageSlot[0],0) >= checkDesireFilledStorageSlot[1]:
                continue

            for room in beUsefull.getRandomPriotisedRooms(character,currentRoom):
                if room.tag != "storage":
                    continue
                storageSlots = room.storageSlots[:]
                random.shuffle(storageSlots)
                for storageSlot in storageSlots:
                    if storageSlot[1] or storageSlot[2]:
                        continue
                    if room.getItemByPosition(storageSlot[0]):
                        continue
                    quest = src.quests.questMap["DrawStockpile"](stockpileType="s",targetPositionBig=room.getPosition(),targetPosition=storageSlot[0],reason="designate special storage for basic items",itemType=checkDesireFilledStorageSlot[0],extraInfo={"desiredState":"filled"})
                    return ([quest],None)

        return (None,None)

src.quests.addType(DrawFloorPlan)

import src
import random


class ExtendBase(src.quests.MetaQuestSequence): 
    type = "ExtendBase"

    def __init__(self, description="set up base", creator=None, command=None, lifetime=None):
        questList = []
        super().__init__(questList, creator=creator, lifetime=lifetime)
        self.metaDescription = description

    def generateTextDescription(self):
        out = []
        if len(self.character.getTerrain().rooms) == 1:
            roomBuilder = src.items.itemMap["RoomBuilder"]()
            wall = src.items.itemMap["Wall"]()
            door = src.items.itemMap["Door"]()
            out.extend(["""
You remember that your task is to set up a base.
You know you are equiped for it, but you remember nothing more.
Follow that order and set up a base.

Your base is currently only the city core.
This is the room you started in.
To set up the base you need to build more rooms.

Use a RoomBuilder (""",roomBuilder.render(),""") to build a room.
The needed walls (""",wall.render(),""") and Doors (""",door.render(),""") should be in the city core.
Start setting up the base using these materials.

Add the first room, to have space for some industry.
This has the nice side effect of freeing up space in the city core.
"""])
        elif len(self.character.getTerrain().rooms) == 2:
            out.append("""
Your base has one additional room now.
This should give you some room to work with.
Set up a production line for walls and some basic infrastructure.

Use this to build another room.
""")
        elif len(self.character.getTerrain().rooms) == 3:
            out.append("""
Your base has 2 additional rooms now.
That is actually quite a lot of space.
Try to fill that space.

""")
        elif len(self.character.getTerrain().rooms) == 4:
            out.append("""
Your base has 3 additional rooms now. great.
Did you set food production already?

""")
        elif len(self.character.getTerrain().rooms) == 5:
            out.append("""
Almost done! Keep going

""")
        else:
            out.append("""
Extend the base further.

""")

        out.append("""
Build 6 rooms to complete this quest.
Build %s more rooms to achive that.
"""%(6-len(self.character.getTerrain().rooms),))

        if not self.subQuests:
            out.append((src.interaction.urwid.AttrSpec("#f00", "black"),"""
This quest has no subquests. Press r to generate subquests for this quest."""))
        else:
            out.append("""
This quests has subquests.
Follow this quests sub quests. They will guide you and try to explain how to build a base.
You do not have to follow the subquests as long as the base is getting set up.
Press d to move the cursor and show the subquests description.
""")
        return out

    def roomBuildingFailed(self,extraParam):
        3/0

    def solver(self, character):
        (nextQuests,nextCommand) = self.getNextStep(character,dryRun=False)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
            if not self.subQuests[0].active:
                self.subQuests[0].activate()
            return

        if nextCommand:
            character.runCommandString(nextCommand[0])
            return
        super().solver(character)

    def getSolvingCommandString(self, character, dryRun=True):
        nextStep = self.getNextStep(character)
        if nextStep == (None,None):
            return super().getSolvingCommandString(character)
        return nextStep[1]

    def generateSubquests(self, character=None):
        (nextQuests,nextCommand) = self.getNextStep(character,ignoreCommands=True)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
            return

    def handQuestFailure(self,extraParam):
        self.subQuests.remove(extraParam["quest"])
        if extraParam["reason"] == "no storage available":
            terrain = self.character.getTerrain()
            cityPlanner = terrain.getRoomByPosition((7,7,0))[0].getItemByPosition((5,2,0))
            if not cityPlanner:
                quest = src.quests.questMap["DiscardInventory"]()
                self.addQuest(quest)
                return
            cityPlanner = cityPlanner[0]
            if not cityPlanner.type == "CityPlaner":
                quest = src.quests.questMap["DiscardInventory"]()
                self.addQuest(quest)
                return

            for generalPurposeRoom in cityPlanner.generalPurposeRooms:
                for y in (1,3,5):
                    for x in range(1,6):
                        quest = src.quests.questMap["DrawStockpile"](tryHard=True,itemType=None,stockpileType="s",targetPositionBig=generalPurposeRoom,targetPosition=(x,y,0))
                        self.addQuest(quest)
                quest = src.quests.questMap["DiscardInventory"]()
                self.addQuest(quest)
                return

            quest = src.quests.questMap["DiscardInventory"]()
            self.addQuest(quest)
            return

    def getNextStep(self,character=None,ignoreCommands=False,dryRun=True):
        if not self.subQuests:
            if not ignoreCommands:
                submenue = character.macroState.get("submenue")
                if submenue:
                    return (None,(["esc"],"exit the menu"))

            """
            if not character.weapon:
                quest = src.quests.questMap["Equip"](weaponOnly=True)
                self.startWatching(quest,self.roomBuildingFailed,"failed")
                return ([quest],None)
            """

            if len(character.getTerrain().rooms) < 2:
                candidates = [(6,7,0),(7,6,0),(8,7,0),(7,8,0)]
                random.shuffle(candidates)
                for candidate in candidates:
                    terrain = character.getTerrain()
                    if (not terrain.getRoomByPosition(candidate)) and (not candidate in terrain.scrapFields) and (not candidate in terrain.forests):
                        if len(terrain.itemsByBigCoordinate.get(candidate,[])) < 5:
                            quest = src.quests.questMap["BuildRoom"](targetPosition=candidate,tryHard=True,reason="make some room to work with",takeAnyUnbolted=True)
                            if not dryRun:
                                self.startWatching(quest,self.roomBuildingFailed,"failed")
                            return ([quest],None)
                for candidate in candidates:
                    terrain = character.getTerrain()
                    if (not terrain.getRoomByPosition(candidate)) and (not candidate in terrain.scrapFields) and (not candidate in terrain.forests):
                        quest = src.quests.questMap["BuildRoom"](targetPosition=candidate,tryHard=True,reason="make some room to work with",takeAnyUnbolted=True)
                        if not dryRun:
                            self.startWatching(quest,self.roomBuildingFailed,"failed")
                        return ([quest],None)
                self.fail()
                return (None,None)

            if len(character.getTerrain().rooms) < 3:

                terrain = character.getTerrain()
                room = terrain.getRoomByPosition((7,7,0))[0]
                items = room.getItemByPosition((5,2,0))
                if ( not room.getItemByPosition((5,2,0)) or 
                     not room.getItemByPosition((5,2,0))[0].type == "CityPlaner" ):
                    quest = src.quests.questMap["PlaceItem"](targetPositionBig=(7,7,0),targetPosition=(5,2,0),itemType="CityPlaner",boltDown=True)
                    if not dryRun:
                        self.startWatching(quest,self.handQuestFailure,"failed")
                    return ([quest],None)

                cityPlaner = room.getItemByPosition((5,2,0))[0]
                if not cityPlaner.generalPurposeRooms:
                    for room in terrain.rooms:
                        if room.getPosition() == (7,0,0):
                            continue
                        if room.getPosition() in cityPlaner.specialPurposeRooms:
                            continue
                        if room.getPosition() in cityPlaner.generalPurposeRooms:
                            continue
                        if (len(room.itemsOnFloor) > 13+13+12+12 or room.floorPlan or room.storageSlots or len(room.walkingSpace) > 4 or room.inputSlots):
                            continue
                        cityPlaner.generalPurposeRooms.append(room.getPosition())

                doorFound = False
                for checkRoom in character.getTerrain().rooms:
                    for item in checkRoom.itemsOnFloor+character.inventory:
                        if item.bolted:
                            continue
                        if item.type == "Door":
                            doorFound = True

                terrain = character.getTerrain()
                candidates = []
                for room in terrain.rooms:
                    roomPos = room.getPosition()
                    candidates.append((roomPos[0]-1,roomPos[1],0))
                    candidates.append((roomPos[0]+1,roomPos[1],0))
                    candidates.append((roomPos[0],roomPos[1]-1,0))
                    candidates.append((roomPos[0],roomPos[1]+1,0))

                foundRoomBuilder = False
                for candidate in candidates[:]:
                    if terrain.getRoomByPosition(candidate):
                        candidates.remove(candidate)
                        continue
                    if candidate in terrain.scrapFields:
                        candidates.remove(candidate)
                        continue
                    print(terrain.forests)
                    if candidate in terrain.forests:
                        candidates.remove(candidate)
                        continue

                    items = terrain.getItemByPosition((candidate[0]*15+7,candidate[1]*15+7,0))
                    if items and items[0].type == "RoomBuilder":
                        foundRoomBuilder = True

                random.shuffle(candidates)

                if not foundRoomBuilder:
                    for candidate in candidates:
                        if len(terrain.itemsByBigCoordinate.get(candidate,[])) < 5:
                            quest = src.quests.questMap["PlaceItem"](targetPositionBig=candidate,targetPosition=(7,7,0),itemType="RoomBuilder",tryHard=True)
                            return ([quest],None)
                    candidate = candidates[0]
                    quest = src.quests.questMap["PlaceItem"](targetPositionBig=candidate,targetPosition=(7,7,0),itemType="RoomBuilder",tryHard=True)
                    return ([quest],None)

                room = character.getTerrain().getRoomByPosition((7,7,0))[0]
                itemsOnFloor = room.itemsOnFloor
                random.shuffle(itemsOnFloor)
                quests = []
                for item in room.itemsOnFloor:
                    if item.bolted:
                        continue

                    if not item.type in ("Wall","Door","RoomBuilder",):
                        continue

                    inStorage = False
                    pos = item.getPosition()
                    for storageSlot in room.storageSlots:
                        if storageSlot[0] == pos:
                            inStorage = True

                    if inStorage:
                        continue

                    quest = src.quests.questMap["CleanSpace"](targetPositionBig=(7,7,0),targetPosition=item.getPosition())
                    if not dryRun:
                        self.startWatching(quest,self.handQuestFailure,"failed")
                    quests.append(quest)

                if quests:
                    return (quests,None)

                if not character.getFreeInventorySpace():
                    quest = src.quests.questMap["ClearInventory"]()
                    if not dryRun:
                        self.startWatching(quest,self.handQuestFailure,"failed")
                    return ([quest],None)

                room = character.getTerrain().getRoomByPosition((7,7,0))[0]
                epochArtwork = room.getItemsByType("EpochArtwork")[0]
                if epochArtwork.recalculateGlasstears(character,dryRun=True):
                    quest = src.quests.questMap["GetEpochEvaluation"]()
                    return ([quest],None)

                hasRoombuildingNPC = False
                for otherChar in character.getTerrain().characters:
                    if otherChar == character:
                        continue
                    if "room building" in otherChar.duties:
                        hasRoombuildingNPC = True
                for room in character.getTerrain().rooms:
                    for otherChar in room.characters:
                        if otherChar == character:
                            continue
                        if "room building" in otherChar.duties:
                            hasRoombuildingNPC = True

                if not hasRoombuildingNPC and epochArtwork.charges >= 10:
                    quest = src.quests.questMap["GetEpochReward"](rewardType="room building")
                    return ([quest],None)

                if not doorFound:
                    quest = src.quests.questMap["Scavenge"](toCollect="Door")
                    return ([quest],None)

                quest = src.quests.questMap["Scavenge"](toCollect="Wall")
                return ([quest],None)

            if len(character.getTerrain().rooms) < 4:

                if not character.getFreeInventorySpace():
                    quest = src.quests.questMap["ClearInventory"](returnToTile=False)
                    if not dryRun:
                        self.startWatching(quest,self.handQuestFailure,"failed")
                    return ([quest],None)

                terrain = character.getTerrain()
                room = terrain.getRoomByPosition((7,7,0))[0]
                epochArtwork = room.getItemsByType("EpochArtwork")[0]
                if epochArtwork.recalculateGlasstears(character,dryRun=True):
                    quest = src.quests.questMap["GetEpochEvaluation"]()
                    return ([quest],None)

                hasScavengingNPC = False
                for otherChar in character.getTerrain().characters:
                    if otherChar == character:
                        continue
                    if "scavenging" in otherChar.duties:
                        hasScavengingNPC = True
                for checkRoom in character.getTerrain().rooms:
                    for otherChar in checkRoom.characters:
                        if otherChar == character:
                            continue
                        if "scavenging" in otherChar.duties:
                            hasScavengingNPC = True

                if not hasScavengingNPC and epochArtwork.charges >= 10:
                    quest = src.quests.questMap["GetEpochReward"](rewardType="scavenging")
                    return ([quest],None)

                #schedule rooms to be build
                #TODO: do this properly
                cityPlaner = room.getItemByPosition((5,2,0))[0]
                if not cityPlaner.plannedRooms:
                    for checkRoom in terrain.rooms:
                        roomPos = checkRoom.getPosition()
                        for offset in ((1,0,0),(-1,0,0),(0,1,0),(0,-1,0)):
                            newPos = (roomPos[0]+offset[0],roomPos[1]+offset[1],0)
                            if newPos in terrain.forests:
                                continue
                            if (newPos[0],newPos[1]) in terrain.scrapFields:
                                continue
                            if terrain.getRoomByPosition(newPos):
                                continue
                            if newPos in cityPlaner.plannedRooms:
                                continue
                            if len(terrain.itemsByBigCoordinate.get(newPos,[])) > 5:
                                continue
                            cityPlaner.plannedRooms.append(newPos)

                cityPlaner = room.getItemByPosition((5,2,0))[0]
                if not cityPlaner.plannedRooms:
                    for checkRoom in terrain.rooms:
                        roomPos = checkRoom.getPosition()
                        for offset in ((1,0,0),(-1,0,0),(0,1,0),(0,-1,0)):
                            newPos = (roomPos[0]+offset[0],roomPos[1]+offset[1],0)
                            if newPos in terrain.forests:
                                continue
                            if (newPos[0],newPos[1]) in terrain.scrapFields:
                                continue
                            if terrain.getRoomByPosition(newPos):
                                continue
                            if newPos in cityPlaner.plannedRooms:
                                continue
                            cityPlaner.plannedRooms.append(newPos)

                #set special purpose room
                #TODO: do this properly
                if not cityPlaner.specialPurposeRooms:
                    for room in terrain.rooms:
                        if room.getPosition() == (7,7,0):
                            continue
                        if room.getPosition() in cityPlaner.specialPurposeRooms:
                            continue
                        if room.getPosition() in cityPlaner.generalPurposeRooms:
                            continue
                        if (len(room.itemsOnFloor) > 13+13+12+12 or room.floorPlan or room.storageSlots or len(room.walkingSpace) > 4 or room.inputSlots):
                            continue
                        cityPlaner.specialPurposeRooms.append(room.getPosition())
                        break

                if not room.getItemByPosition((8,2,0)):
                    quest = src.quests.questMap["SetUpMachine"](targetPositionBig=(7,7,0),targetPosition=(8,2,0),itemType="Wall",tryHard=True)
                    return ([quest],None)

                machine = room.getItemByPosition((8,2,0))[0]
                if machine.readyToUse():
                    if not character.getBigPosition() == (7,7,0):
                        quest = src.quests.questMap["GoHome"]()
                        return ([quest],None)
                    quest = src.quests.questMap["OperateMachine"](targetPosition=(8,2,0))
                    return ([quest],None)
                machine = room.getItemByPosition((8,4,0))[0]
                if machine.readyToUse():
                    if not character.getBigPosition() == (7,7,0):
                        quest = src.quests.questMap["GoHome"]()
                        return ([quest],None)
                    quest = src.quests.questMap["OperateMachine"](targetPosition=(8,4,0))
                    return ([quest],None)
                machine = room.getItemByPosition((8,5,0))[0]
                if machine.readyToUse():
                    if not character.getBigPosition() == (7,7,0):
                        quest = src.quests.questMap["GoHome"]()
                        return ([quest],None)
                    quest = src.quests.questMap["OperateMachine"](targetPosition=(8,5,0))
                    return ([quest],None)

                storageRoomPosition = cityPlaner.specialPurposeRooms[0]
                storageRoom = terrain.getRoomByPosition(storageRoomPosition)[0]
                positions = []
                for y in (1,):
                    quests = []
                    for x in range(1,12):
                        if x == 6:
                            continue
                        isPainted = False
                        position = (x,y,0)
                        for storageSlot in storageRoom.storageSlots:
                            if position == storageSlot[0]:
                                isPainted = True
                                break
                        if isPainted:
                            continue
                        quest = src.quests.questMap["DrawStockpile"](tryHard=True,itemType=None,stockpileType="s",targetPositionBig=storageRoomPosition,targetPosition=position)
                        quests.append(quest)
                    if quests:
                        return (quests,None)

                caseFound = False
                doorFound = False
                metalBarsFound = False
                for checkRoom in character.getTerrain().rooms:
                    for item in checkRoom.itemsOnFloor+character.inventory:
                        if item.bolted:
                            continue
                        if item.type == "Case":
                            caseFound = True
                        if item.type == "Door":
                            doorFound = True
                        if item.type == "MetalBars":
                            metalBarsFound = True

                if metalBarsFound and not room.getItemByPosition((7,2,0)):
                    quest = src.quests.questMap["PlaceItem"](targetPositionBig=(7,7,0),targetPosition=(7,2,0),itemType="MetalBars")
                    return ([quest],None)

                if caseFound and not room.getItemByPosition((8,1,0)):
                    quest = src.quests.questMap["PlaceItem"](targetPositionBig=(7,7,0),targetPosition=(8,1,0),itemType="Case")
                    return ([quest],None)

                if not caseFound:
                    quest = src.quests.questMap["Scavenge"](toCollect="Case")
                    return ([quest],None)
                if not metalBarsFound:
                    quest = src.quests.questMap["Scavenge"](toCollect="MetalBars")
                    return ([quest],None)
                if not doorFound:
                    quest = src.quests.questMap["Scavenge"](toCollect="Door")
                    return ([quest],None)

            terrain = character.getTerrain()
            room = terrain.getRoomByPosition((7,7,0))[0]
            cityPlaner = room.getItemByPosition((5,2,0))[0]
            storageRoomPosition = cityPlaner.specialPurposeRooms[0]
            storageRoom = terrain.getRoomByPosition(storageRoomPosition)[0]
            positions = []
            for y in (1,3,5,7,9,11):
                quests = []
                for x in range(1,12):
                    if x == 6:
                        continue
                    isPainted = False
                    position = (x,y,0)
                    for storageSlot in storageRoom.storageSlots:
                        if position == storageSlot[0]:
                            isPainted = True
                            break
                    if isPainted:
                        continue
                    quest = src.quests.questMap["DrawStockpile"](tryHard=True,itemType=None,stockpileType="s",targetPositionBig=storageRoomPosition,targetPosition=position)
                    quests.append(quest)
                if quests:
                    return (quests,None)

            if len(character.getTerrain().rooms) < 4:
                quest = src.quests.questMap["Scavenge"](toCollect="Wall")
                quest.assignToCharacter(character)
                return ([quest],None)

            if len(character.getTerrain().rooms) < 5:
                if character.inventory:
                    quest = src.quests.questMap["ClearInventory"](returnToTile=False)
                    if not dryRun:
                        self.startWatching(quest,self.handQuestFailure,"failed")
                    return ([quest],None)

                room = character.getTerrain().getRoomByPosition((7,7,0))[0]
                epochArtwork = room.getItemsByType("EpochArtwork")[0]
                if epochArtwork.recalculateGlasstears(character,dryRun=True):
                    quest = src.quests.questMap["GetEpochEvaluation"]()
                    return ([quest],None)

                hasNPC = False
                for otherChar in character.getTerrain().characters:
                    if otherChar == character:
                        continue
                    if "machine operating" in otherChar.duties:
                        hasNPC = True
                for checkRoom in character.getTerrain().rooms:
                    for otherChar in checkRoom.characters:
                        if otherChar == character:
                            continue
                        if "machine operating" in otherChar.duties:
                            hasNPC = True

                if not hasNPC and epochArtwork.charges >= 10:
                    quest = src.quests.questMap["GetEpochReward"](rewardType="machine operating")
                    return ([quest],None)

                terrain = character.getTerrain()
                for checkRoom in terrain.rooms:
                    for inputSlot in checkRoom.getEmptyInputslots():
                        if not inputSlot[1]:
                            continue

                        for sourceRoom in terrain.rooms:
                            for outputSlot in sourceRoom.getNonEmptyOutputslots(inputSlot[1]):
                                amount = None
                                if inputSlot[1] == "Case":
                                    amount = 1
                                quest2 = src.quests.questMap["FetchItems"](toCollect=inputSlot[1],amount=amount)
                                quest4 = src.quests.questMap["RestockRoom"](toRestock=inputSlot[1],targetPosition=checkRoom.getPosition())
                                return ([quest4,quest2],None)


            #set special purpose room
            #TODO: do this properly
            if len(cityPlaner.specialPurposeRooms) < 2:
                for room in terrain.rooms:
                    if room.getPosition() == (7,7,0):
                        continue
                    if room.getPosition() in cityPlaner.specialPurposeRooms:
                        continue
                    if room.getPosition() in cityPlaner.generalPurposeRooms:
                        continue
                    if (len(room.itemsOnFloor) > 13+13+12+12 or room.floorPlan or room.storageSlots or len(room.walkingSpace) > 4 or room.inputSlots):
                        continue
                    cityPlaner.specialPurposeRooms.append(room.getPosition())
                    break

            terrain = character.getTerrain()
            positions = [(3,3,0),(6,3,0),(3,6,0),(6,6,0),(9,9,0),(7,9,0),(5,9,0)]
            machineRoomPosition = cityPlaner.specialPurposeRooms[1]
            checkRoom = terrain.getRoomByPosition(machineRoomPosition)[0]
            for pos in positions:
                if not checkRoom.getItemByPosition(pos):
                    itemType = "Wall"
                    if pos == (6,6,0):
                        itemType = "Door"
                    if pos == (9,6,0):
                        itemType = "ScrapCompactor"
                    if pos == (5,9,0):
                        itemType = "Rod"
                    if pos == (7,9,0):
                        itemType = "Frame"
                    if pos == (9,9,0):
                        itemType = "Case"
                    if itemType == "ScrapCompactor":
                        quest1 = src.quests.questMap["SetUpMachine"](targetPositionBig=machineRoomPosition,targetPosition=pos,itemType=itemType)
                        quest2 = src.quests.questMap["DrawStockpile"](tryHard=True,itemType="MetalBars",stockpileType="i",targetPositionBig=machineRoomPosition,targetPosition=(pos[0]-1,pos[1],0))
                        quest4 = src.quests.questMap["DrawStockpile"](tryHard=True,itemType=itemType,stockpileType="o",targetPositionBig=machineRoomPosition,targetPosition=(pos[0]+1,pos[1],0))

                        return ([quest4,quest2,quest1],None)
                    elif itemType == "Rod":
                        quest1 = src.quests.questMap["SetUpMachine"](targetPositionBig=machineRoomPosition,targetPosition=pos,itemType=itemType)
                        quest2 = src.quests.questMap["DrawStockpile"](tryHard=True,itemType="MetalBars",stockpileType="i",targetPositionBig=machineRoomPosition,targetPosition=(pos[0]-1,pos[1],0))

                        return ([quest2,quest1],None)
                    elif itemType == "Frame":
                        quest1 = src.quests.questMap["SetUpMachine"](targetPositionBig=machineRoomPosition,targetPosition=pos,itemType=itemType)
                        quest2 = src.quests.questMap["DrawStockpile"](tryHard=True,itemType="Rod",stockpileType="i",targetPositionBig=machineRoomPosition,targetPosition=(pos[0]-1,pos[1],0))

                        return ([quest2,quest1],None)
                    elif itemType == "Case":
                        quest1 = src.quests.questMap["SetUpMachine"](targetPositionBig=machineRoomPosition,targetPosition=pos,itemType=itemType)
                        quest2 = src.quests.questMap["DrawStockpile"](tryHard=True,itemType="Frame",stockpileType="i",targetPositionBig=machineRoomPosition,targetPosition=(pos[0]-1,pos[1],0))
                        quest4 = src.quests.questMap["DrawStockpile"](tryHard=True,itemType=itemType,stockpileType="o",targetPositionBig=machineRoomPosition,targetPosition=(pos[0]+1,pos[1],0))

                        return ([quest4,quest2,quest1],None)
                    else:
                        quest1 = src.quests.questMap["SetUpMachine"](targetPositionBig=machineRoomPosition,targetPosition=pos,itemType=itemType)
                        quest2 = src.quests.questMap["DrawStockpile"](tryHard=True,itemType="MetalBars",stockpileType="i",targetPositionBig=machineRoomPosition,targetPosition=(pos[0]-1,pos[1],0))
                        quest3 = src.quests.questMap["DrawStockpile"](tryHard=True,itemType="Case",stockpileType="i",targetPositionBig=machineRoomPosition,targetPosition=(pos[0],pos[1]-1,0))
                        quest4 = src.quests.questMap["DrawStockpile"](tryHard=True,itemType=itemType,stockpileType="o",targetPositionBig=machineRoomPosition,targetPosition=(pos[0]+1,pos[1],0))

                        return ([quest4,quest2,quest3,quest1],None)

            if len(character.getTerrain().rooms) < 5:
                quest = src.quests.questMap["Scavenge"]()
                return ([quest],None)

            if len(character.getTerrain().rooms) < 6:

                room = character.getTerrain().getRoomByPosition((7,7,0))[0]
                epochArtwork = room.getItemsByType("EpochArtwork")[0]
                if epochArtwork.recalculateGlasstears(character,dryRun=True):
                    quest = src.quests.questMap["GetEpochEvaluation"]()
                    return ([quest],None)

                hasNPC = False
                for otherChar in character.getTerrain().characters:
                    if otherChar == character:
                        continue
                    if "resource fetching" in otherChar.duties:
                        hasNPC = True
                for checkRoom in character.getTerrain().rooms:
                    for otherChar in checkRoom.characters:
                        if otherChar == character:
                            continue
                        if "resource fetching" in otherChar.duties:
                            hasNPC = True

                if not hasNPC and epochArtwork.charges >= 10:
                    quest = src.quests.questMap["GetEpochReward"](rewardType="resource fetching")
                    return ([quest],None)

                for room in terrain.rooms:
                    for inputSlot in room.getEmptyInputslots():
                        if not inputSlot[1]:
                            continue
                        if inputSlot[1] == "MetalBars":
                            continue
                        if inputSlot[1] == "Scrap":
                            continue
                        if not room.getNonEmptyOutputslots(inputSlot[1]):
                            continue

                        quest1 = src.quests.questMap["GoToTile"](targetPosition=room.getPosition())
                        quest2 = src.quests.questMap["FetchItems"](toCollect=inputSlot[1],amount=1)
                        quest3 = src.quests.questMap["RestockRoom"](toRestock=inputSlot[1])
                        return ([quest3,quest2,quest1],None)

            if len(character.getTerrain().rooms) < 6:
                for room in terrain.rooms:
                    inputSlots = room.getEmptyInputslots(itemType="Scrap")
                    for inputSlot in inputSlots:
                        if room.getItemByPosition(inputSlot[0]):
                            continue
                        quest1 = src.quests.questMap["GatherScrap"](reason="have Scrap to supply the city with")
                        quest2 = src.quests.questMap["GoToTile"](targetPosition=room.getPosition(),reason="go to tile in need of Scrap")
                        quest3 = src.quests.questMap["RestockRoom"](toRestock="Scrap",reason="ensure scrap supply")
                        return ([quest3,quest2,quest1],None)

            machineRoomPosition = cityPlaner.specialPurposeRooms[1]
            pos = (9,3,0)
            room = character.getTerrain().getRoomByPosition(machineRoomPosition)[0]
            if not room.getItemByPosition(pos):
                quest1 = src.quests.questMap["SetUpMachine"](targetPositionBig=machineRoomPosition,targetPosition=pos,itemType="ScrapCompactor")
                quest2 = src.quests.questMap["DrawStockpile"](tryHard=True,itemType="MetalBars",stockpileType="i",targetPositionBig=machineRoomPosition,targetPosition=(pos[0]-1,pos[1],0))
                quest4 = src.quests.questMap["DrawStockpile"](tryHard=True,itemType="ScrapCompactor",stockpileType="o",targetPositionBig=machineRoomPosition,targetPosition=(pos[0]+1,pos[1],0))

                return ([quest4,quest2,quest1],None)

            pos = (3,9,0)
            room = character.getTerrain().getRoomByPosition(machineRoomPosition)[0]
            if not room.getItemByPosition(pos):
                quest1 = src.quests.questMap["DrawStockpile"](tryHard=True,itemType="Scrap",stockpileType="i",targetPositionBig=machineRoomPosition,targetPosition=(pos[0]-1,pos[1],0))
                quest2 = src.quests.questMap["PlaceItem"](targetPositionBig=machineRoomPosition,targetPosition=pos,itemType="ScrapCompactor",tryHard=True,boltDown=True)
                return ([quest1,quest2],None)

            #set special purpose room
            #TODO: do this properly
            if len(cityPlaner.specialPurposeRooms) < 3:
                for room in terrain.rooms:
                    if room.getPosition() == (7,7,0):
                        continue
                    if room.getPosition() in cityPlaner.specialPurposeRooms:
                        continue
                    if room.getPosition() in cityPlaner.generalPurposeRooms:
                        continue
                    if (len(room.itemsOnFloor) > 13+13+12+12 or room.floorPlan or room.storageSlots or len(room.walkingSpace) > 4 or room.inputSlots):
                        continue
                    cityPlaner.specialPurposeRooms.append(room.getPosition())
                    break

            if len(character.getTerrain().rooms) == 6:
                room = character.getTerrain().getRoomByPosition((7,7,0))[0]
                epochArtwork = room.getItemsByType("EpochArtwork")[0]
                if epochArtwork.recalculateGlasstears(character,dryRun=True):
                    quest = src.quests.questMap["GetEpochEvaluation"]()
                    return ([quest],None)

                hasNPC = False
                for otherChar in character.getTerrain().characters:
                    if otherChar == character:
                        continue
                    if "resource gathering" in otherChar.duties:
                        hasNPC = True
                for checkRoom in character.getTerrain().rooms:
                    for otherChar in checkRoom.characters:
                        if otherChar == character:
                            continue
                        if "resource gathering" in otherChar.duties:
                            hasNPC = True

                if not hasNPC and epochArtwork.charges >= 10:
                    quest = src.quests.questMap["GetEpochReward"](rewardType="resource gathering")
                    return ([quest],None)

            positions = [(3,2,0),(3,3,0),(3,5,0),(3,6,0),(3,8,0),(3,9,0),]
            machineRoomPosition2 = cityPlaner.specialPurposeRooms[2]
            checkRoom = terrain.getRoomByPosition(machineRoomPosition2)[0]
            for pos in positions:
                if not checkRoom.getItemByPosition(pos):
                    quest1 = src.quests.questMap["DrawStockpile"](tryHard=True,itemType="Scrap",stockpileType="i",targetPositionBig=machineRoomPosition2,targetPosition=(pos[0]-1,pos[1],0))
                    quest2 = src.quests.questMap["PlaceItem"](targetPositionBig=machineRoomPosition2,targetPosition=pos,itemType="ScrapCompactor",tryHard=True,boltDown=True)
                    quest3 = src.quests.questMap["DrawStockpile"](tryHard=True,itemType="MetalBars",stockpileType="o",targetPositionBig=machineRoomPosition2,targetPosition=(pos[0]+1,pos[1],0))
                    return ([quest1,quest3,quest2],None)

            positions = [(3,2,0),(3,3,0),(3,5,0),(3,6,0),]
            checkRoom = terrain.getRoomByPosition(machineRoomPosition2)[0]
            for pos in positions:
                pos = (pos[0]+2,pos[1],0)
                if not checkRoom.getItemByPosition(pos):
                    quest = src.quests.questMap["SetUpMachine"](targetPositionBig=machineRoomPosition2,targetPosition=pos,itemType="Rod")
                    return ([quest],None)
                pos = (pos[0]+2,pos[1],0)
                if not checkRoom.getItemByPosition(pos):
                    quest = src.quests.questMap["SetUpMachine"](targetPositionBig=machineRoomPosition2,targetPosition=pos,itemType="Frame")
                    return ([quest],None)
                pos = (pos[0]+2,pos[1],0)
                if not checkRoom.getItemByPosition(pos):
                    quest1 = src.quests.questMap["DrawStockpile"](tryHard=True,itemType="Case",stockpileType="o",targetPositionBig=machineRoomPosition2,targetPosition=(pos[0]+1,pos[1],0))
                    quest2 = src.quests.questMap["SetUpMachine"](targetPositionBig=machineRoomPosition2,targetPosition=pos,itemType="Case")
                    return ([quest2,quest1],None)

            machineRoomPosition = cityPlaner.specialPurposeRooms[1]
            checkRoom = terrain.getRoomByPosition(machineRoomPosition)[0]
            pos = (9,6,0)
            if not checkRoom.getItemByPosition(pos):
                quest1 = src.quests.questMap["DrawStockpile"](tryHard=True,itemType="RoomBuilder",stockpileType="o",targetPositionBig=machineRoomPosition,targetPosition=(pos[0]+1,pos[1],0))
                quest2 = src.quests.questMap["DrawStockpile"](tryHard=True,itemType="Case",stockpileType="i",targetPositionBig=machineRoomPosition,targetPosition=(pos[0]-1,pos[1],0))
                quest3 = src.quests.questMap["DrawStockpile"](tryHard=True,itemType="pusher",stockpileType="i",targetPositionBig=machineRoomPosition,targetPosition=(pos[0],pos[1]-1,0))
                quest4 = src.quests.questMap["DrawStockpile"](tryHard=True,itemType="puller",stockpileType="i",targetPositionBig=machineRoomPosition,targetPosition=(pos[0],pos[1]+1,0))
                quest5 = src.quests.questMap["SetUpMachine"](targetPositionBig=machineRoomPosition,targetPosition=pos,itemType="RoomBuilder")

                return ([quest5,quest4,quest3,quest2,quest1],None)

            checkRoom = terrain.getRoomByPosition(machineRoomPosition2)[0]
            pos = (7,8,0)
            if not checkRoom.getItemByPosition(pos):
                quest1 = src.quests.questMap["DrawStockpile"](tryHard=True,itemType="pusher",stockpileType="o",targetPositionBig=machineRoomPosition2,targetPosition=(pos[0]+1,pos[1],0))
                quest2 = src.quests.questMap["SetUpMachine"](targetPositionBig=machineRoomPosition2,targetPosition=pos,itemType="pusher")
                return ([quest2,quest1],None)
            pos = (5,8,0)
            if not checkRoom.getItemByPosition(pos):
                quest2 = src.quests.questMap["SetUpMachine"](targetPositionBig=machineRoomPosition2,targetPosition=pos,itemType="Stripe")
                return ([quest2],None)
            pos = (7,9,0)
            if not checkRoom.getItemByPosition(pos):
                quest1 = src.quests.questMap["DrawStockpile"](tryHard=True,itemType="puller",stockpileType="o",targetPositionBig=machineRoomPosition2,targetPosition=(pos[0]+1,pos[1],0))
                quest2 = src.quests.questMap["SetUpMachine"](targetPositionBig=machineRoomPosition2,targetPosition=pos,itemType="puller")
                return ([quest2,quest1],None)
            pos = (5,9,0)
            if not checkRoom.getItemByPosition(pos):
                quest2 = src.quests.questMap["SetUpMachine"](targetPositionBig=machineRoomPosition2,targetPosition=pos,itemType="Bolt")
                return ([quest2],None)

            for room in terrain.rooms:
                if not room.floorPlan:
                    continue

                quest1 = src.quests.questMap["GoToTile"](targetPosition=room.getPosition())
                quest2 = src.quests.questMap["DrawFloorPlan"](targetPosition=room.getPosition())
                return ([quest2,quest1],None)

            return (None,("...","wait"))
            1/0

            character.timeTaken +=1
            return (None,None)


            rooms = character.getTerrain().getRoomByPosition((7,7,0))
            if not rooms:
                self.fail("command centre missing")
                return (None,None)
            room = rooms[0]

            npcs = []
            npcs.extend(character.getTerrain().characters)
            for checkRoom in character.getTerrain().rooms:
                npcs.extend(checkRoom.characters)
            for npc in npcs:
                if npc == character:
                    continue
                if not npc.faction == character.faction:
                    continue
                quest = src.quests.questMap["ReduceFoodConsumption"](reason="prevent starvation")
                return ([quest],None)

            for checkRoom in character.getTerrain().rooms:
                for item in checkRoom.itemsOnFloor:
                    if not item.type in ("Corpse","GooFlask"):
                        continue

                    inStorage = False
                    for storageSlot in checkRoom.storageSlots:
                        if not storageSlot[0] == item.getPosition():
                            continue
                        inStorage = True

                    if inStorage:
                        continue
                            
                    quest1 = src.quests.questMap["CleanSpace"](targetPosition=item.getPosition(),targetPositionBig=checkRoom.getPosition(),reason="pick up valuables")
                    quest2 = src.quests.questMap["ClearInventory"](reason="store the valuables")
                    return ([quest2,quest1], None)

            if character.flask and character.flask.uses < 8:
                quest = src.quests.questMap["FillFlask"]()
                return ([quest],None)

            foundInput1 = False
            for inputSlot in room.inputSlots:
                if inputSlot[0] == (7,4,0):
                    foundInput1 = True

            if not foundInput1:
                if room.getItemByPosition((7,4,0)):
                    quest = src.quests.questMap["CleanSpace"](targetPosition=(7,4,0),targetPositionBig=(7,7,0),reason="remove blocking item")
                    return ([quest],None)
                quest = src.quests.questMap["DrawStockpile"](tryHard=True,itemType="Scrap",stockpileType="i",targetPositionBig=(7,7,0),targetPosition=(7,4,0),reason="set up scrap supply infrastructure for the machine production")
                return ([quest],None)

            items = room.getItemByPosition((8,4,0))
            if not items or not items[-1].type == "ScrapCompactor":
                quest = src.quests.questMap["PlaceItem"](targetPositionBig=(7,7,0),targetPosition=(8,4,0),itemType="ScrapCompactor",tryHard=True,boltDown=True,reason="set up metal bar production for the machine production")
                return ([quest],None)

            for room in character.getTerrain().rooms:
                for inputSlot in room.inputSlots:
                    if inputSlot[1] == "Scrap":
                        items = room.getItemByPosition(inputSlot[0])
                        if not items or not items[-1].type == "Scrap":
                            quest1 = src.quests.questMap["GatherScrap"](reason="have Scrap to supply the city with")
                            quest2 = src.quests.questMap["GoToTile"](targetPosition=room.getPosition(),reason="get back to tile in need of Scrap")
                            quest3 = src.quests.questMap["RestockRoom"](toRestock="Scrap",reason="ensure scrap supply")
                            return ([quest3,quest2,quest1],None)
            
            foundCaseOutput = False
            for room in character.getTerrain().rooms:
                for outputSlot in room.outputSlots:
                    if outputSlot[1] == "Case":
                        foundCaseOutput = True

            if not foundCaseOutput:
                quest = src.quests.questMap["SetUpProductionLine"](tryHard=True,itemType="Case",targetPositionBig=(6,7,0))
                return ([quest],None)

            foundWallOutput = False
            for room in character.getTerrain().rooms:
                for outputSlot in room.outputSlots:
                    if outputSlot[1] == "Wall":
                        foundWallOutput = True

            if not foundWallOutput:
                quest = src.quests.questMap["SetUpProductionLine"](tryHard=True,itemType="Wall",targetPositionBig=(6,7,0))
                return ([quest],None)

            foundDoorOutput = False
            for room in character.getTerrain().rooms:
                for outputSlot in room.outputSlots:
                    if outputSlot[1] == "Door":
                        foundDoorOutput = True

            if not foundDoorOutput:
                quest = src.quests.questMap["SetUpProductionLine"](tryHard=True,itemType="Door",targetPositionBig=(6,7,0))
                return ([quest],None)

            if not character.getTerrain().getRoomByPosition((7,8,0)):
                quest = src.quests.questMap["BuildRoom"](targetPosition=(7,8,0),tryHard=True)
                if not dryRun:
                    self.startWatching(quest,self.roomBuildingFailed,"failed")
                return ([quest],None)
            if not character.getTerrain().getRoomByPosition((8,7,0)):
                quest = src.quests.questMap["BuildRoom"](targetPosition=(8,7,0),tryHard=True)
                if not dryRun:
                    self.startWatching(quest,self.roomBuildingFailed,"failed")
                return ([quest],None)
            if not character.getTerrain().getRoomByPosition((7,6,0)):
                quest = src.quests.questMap["BuildRoom"](targetPosition=(7,6,0),tryHard=True)
                if not dryRun:
                    self.startWatching(quest,self.roomBuildingFailed,"failed")
                return ([quest],None)
            if not character.getTerrain().getRoomByPosition((8,8,0)):
                quest = src.quests.questMap["BuildRoom"](targetPosition=(8,8,0),tryHard=True)
                if not dryRun:
                    self.startWatching(quest,self.roomBuildingFailed,"failed")
                return ([quest],None)
            90023/0
            90023/0
        
        return (None,None)

    def gotThirsty(self,extraParam=None):
        quest = src.quests.questMap["Eat"]()
        self.addQuest(quest)
        return
    
    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character, self.gotThirsty, "thirst")
        super().assignToCharacter(character)

    def triggerCompletionCheck(self,character=None):
        return False
    
src.quests.addType(ExtendBase)

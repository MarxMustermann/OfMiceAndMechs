import src
import random


class ExtendBase(src.quests.MetaQuestSequence): 
    type = "ExtendBase"

    def __init__(self, description="set up base", creator=None, command=None, lifetime=None):
        questList = []
        super().__init__(questList, creator=creator, lifetime=lifetime)
        self.metaDescription = description
        self.shownTutorialEnd = False

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

The city core should hold enough building material to build the first room.

This quest system will help you by breaking up that task.
You will get very detailed instructions, but you do not have to follow them closely.
The EpochArtwork will reward you for progress.

"""])
        elif len(self.character.getTerrain().rooms) == 2:
            out.append("""
Your base has one additional room now.
This should give you some room to work with.
To really make use of the rooms you need to expand the base further.

If you followed the instructions you should have a room builder.
That clone will build rooms and frees you up for other tasks.
Place the building materials into storage and the clone will place them.

There are not enough walls in the city core to build the second room.
Scavenge the environment for more building material.
""")
        elif len(self.character.getTerrain().rooms) == 3:
            out.append("""
Your base has 2 additional rooms now.
That is actually quite a lot of space.
Use that space to set up a temporary storage room.

If you followed the instructions you should have a scavenger.
That clone will fetch items from outside and frees you up for other tasks.
The clone will place the item into storage.

There are not enough building materials on the terrain to build all the rooms you need.
Start building Walls instead of just scavenging them.
""")
        elif len(self.character.getTerrain().rooms) == 4:
            out.append("""
Your base has 3 additional rooms now. 
This is enough space to set up production lines.

If you followed the instructions you should have a operator.
That clone will use machines, if the machine is ready to be used.
Input and output stockpiles connect those machines to the storage.

Set up machines to produce your own building items.
Supply these machines to ensure production.
""")
        elif len(self.character.getTerrain().rooms) == 5:
            out.append("""
Almost done! Keep going

""")
        else:
            out.append("""
Extend the base further.

""")

        if not self.subQuests:
            out.append((src.interaction.urwid.AttrSpec("#f00", "black"),"""
This quest has no subquests. Press r to generate subquests for this quest."""))
        else:
            out.append((src.interaction.urwid.AttrSpec("#080", "black"),"""
This quests has subquests.
Press d to move the cursor and show the subquests description.
"""))
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
                quest = src.quests.questMap["DiscardInventory"](reason="be able to act again")
                self.addQuest(quest)
                return
            cityPlanner = cityPlanner[0]
            if not cityPlanner.type == "CityPlaner":
                quest = src.quests.questMap["DiscardInventory"](reason="be able to act again")
                self.addQuest(quest)
                return

            for generalPurposeRoom in cityPlanner.generalPurposeRooms:
                for y in (1,3,5):
                    for x in range(1,6):
                        quest = src.quests.questMap["DrawStockpile"](tryHard=True,itemType=None,stockpileType="s",targetPositionBig=generalPurposeRoom,targetPosition=(x,y,0),reason="extend the storage capacity temporarily")
                        self.addQuest(quest)
                quest = src.quests.questMap["DiscardInventory"](reason="be able to pick up a painter")
                self.addQuest(quest)
                return

            quest = src.quests.questMap["DiscardInventory"](reason="be able to act again")
            self.addQuest(quest)
            return

    def getNextStep(self,character=None,ignoreCommands=False,dryRun=True):

        try:
            self.shownTutorialEnd
        except:
            self.shownTutorialEnd = False

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
                            quest = src.quests.questMap["BuildRoom"](targetPosition=candidate,tryHard=True,reason="start extending the base",takeAnyUnbolted=True)
                            if not dryRun:
                                self.startWatching(quest,self.roomBuildingFailed,"failed")
                            return ([quest],None)
                for candidate in candidates:
                    terrain = character.getTerrain()
                    if (not terrain.getRoomByPosition(candidate)) and (not candidate in terrain.scrapFields) and (not candidate in terrain.forests):
                        quest = src.quests.questMap["BuildRoom"](targetPosition=candidate,tryHard=True,reason="start extending the base",takeAnyUnbolted=True)
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
                    quest = src.quests.questMap["PlaceItem"](targetPositionBig=(7,7,0),targetPosition=(5,2,0),itemType="CityPlaner",reason="be able to use it to manage room purposes")
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
                        if (len(room.itemsOnFloor) > 13+13+11+11 or room.floorPlan or room.storageSlots or len(room.walkingSpace) > 4 or room.inputSlots):
                            continue

                        quest = src.quests.questMap["DesignateRoom"](roomPosition=room.getPosition(),roomType="generalPurposeRoom",reason="reserve some room for unforseen needs")
                        return ([quest],None)

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
                    reason = "start the process of building the second room"
                    for candidate in candidates:
                        if len(terrain.itemsByBigCoordinate.get(candidate,[])) < 5:
                            quest = src.quests.questMap["PlaceItem"](targetPositionBig=candidate,targetPosition=(7,7,0),itemType="RoomBuilder",tryHard=True,reason=reason)
                            return ([quest],None)
                    candidate = candidates[0]
                    quest = src.quests.questMap["PlaceItem"](targetPositionBig=candidate,targetPosition=(7,7,0),itemType="RoomBuilder",tryHard=True,reason=reason)
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

                    quest = src.quests.questMap["CleanSpace"](targetPositionBig=(7,7,0),targetPosition=item.getPosition(),reason="unclutter the city core and put the items into storage")
                    if not dryRun:
                        self.startWatching(quest,self.handQuestFailure,"failed")
                    quests.append(quest)

                if quests:
                    return (quests,None)

                if not character.getFreeInventorySpace():
                    quest = src.quests.questMap["ClearInventory"](reason="fill the stockpiles and free your inventory")
                    if not dryRun:
                        self.startWatching(quest,self.handQuestFailure,"failed")
                    return ([quest],None)

                room = character.getTerrain().getRoomByPosition((7,7,0))[0]
                epochArtwork = room.getItemsByType("EpochArtwork")[0]
                if epochArtwork.recalculateGlasstears(character,dryRun=True):
                    quest = src.quests.questMap["GetEpochEvaluation"](reason="start getting the reward for building the first room")
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
                    quest = src.quests.questMap["GetEpochReward"](rewardType="room building",reason="spawn the first clone to help you")
                    return ([quest],None)

                if not doorFound:
                    quest = src.quests.questMap["Scavenge"](toCollect="Door",reason="get more building materials")
                    return ([quest],None)

                quest = src.quests.questMap["Scavenge"](toCollect="Wall",reason="get more building materials")
                return ([quest],None)

            terrain = character.getTerrain()
            room = terrain.getRoomByPosition((7,7,0))[0]
            cityPlaner = room.getItemByPosition((5,2,0))[0]
            if not cityPlaner.plannedRooms:
                quests = []
                targets = []
                counter = 0
                for checkRoom in terrain.rooms:
                    roomPos = checkRoom.getPosition()
                    for offset in ((1,0,0),(-1,0,0),(0,1,0),(0,-1,0)):
                        newPos = (roomPos[0]+offset[0],roomPos[1]+offset[1],0)
                        if newPos in terrain.forests:
                            continue
                        if (newPos[0],newPos[1]) in terrain.scrapFields:
                            continue
                        if newPos in terrain.scrapFields:
                            continue
                        if terrain.getRoomByPosition(newPos):
                            continue
                        if newPos in cityPlaner.plannedRooms:
                            continue
                        if newPos in targets:
                            continue
                        counter += 1
                        if counter > 3:
                            continue
                        targets.append(newPos)
                        quest = src.quests.questMap["ScheduleRoomBuilding"](roomPosition=newPos,reason="extend the base and keep the room building clone occupied")
                        quests.append(quest)
                return (quests,None)

            if len(character.getTerrain().rooms) < 4:

                if not character.getFreeInventorySpace():
                    quest = src.quests.questMap["ClearInventory"](returnToTile=False,reason="restock the base and have space in your inventory")
                    if not dryRun:
                        self.startWatching(quest,self.handQuestFailure,"failed")
                    return ([quest],None)

                terrain = character.getTerrain()
                room = terrain.getRoomByPosition((7,7,0))[0]
                epochArtwork = room.getItemsByType("EpochArtwork")[0]
                if epochArtwork.recalculateGlasstears(character,dryRun=True):
                    quest = src.quests.questMap["GetEpochEvaluation"](reason="start recieving the reward for building the second room")
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
                    quest = src.quests.questMap["GetEpochReward"](rewardType="scavenging",reason="get a clone to scavenge for you")
                    return ([quest],None)

                #set special purpose room
                if not cityPlaner.specialPurposeRooms:
                    for room in terrain.rooms:
                        if room.getPosition() == (7,7,0):
                            continue
                        if room.getPosition() in cityPlaner.specialPurposeRooms:
                            continue
                        if room.getPosition() in cityPlaner.generalPurposeRooms:
                            continue
                        if (len(room.itemsOnFloor) > 13+13+11+11 or room.floorPlan or room.storageSlots or len(room.walkingSpace) > 4 or room.inputSlots):
                            continue

                        quest = src.quests.questMap["DesignateRoom"](roomPosition=room.getPosition(),roomType="specialPurposeRoom",roomTag="temporaryStorage",reason="have a room to store items in")
                        return ([quest],None)

                machine = room.getItemByPosition((8,2,0))[0]
                if machine.readyToUse():
                    if not character.getBigPosition() == (7,7,0):
                        quest = src.quests.questMap["GoHome"](reason="get back to the city core")
                        return ([quest],None)
                    quest = src.quests.questMap["OperateMachine"](targetPosition=(8,2,0),reason="produce a Wall")
                    return ([quest],None)
                machine = room.getItemByPosition((8,4,0))[0]
                if machine.readyToUse():
                    if not character.getBigPosition() == (7,7,0):
                        quest = src.quests.questMap["GoHome"](reason="get back to the city core")
                        return ([quest],None)
                    quest = src.quests.questMap["OperateMachine"](targetPosition=(8,4,0),reason="produce a MetalBars")
                    return ([quest],None)
                machine = room.getItemByPosition((8,5,0))[0]
                if machine.readyToUse():
                    if not character.getBigPosition() == (7,7,0):
                        quest = src.quests.questMap["GoHome"](reason="get back to the city core")
                        return ([quest],None)
                    quest = src.quests.questMap["OperateMachine"](targetPosition=(8,5,0),reason="produce a MetalBars")
                    return ([quest],None)

                storageRoom = None
                for room in terrain.rooms:
                    if not room.tag == "temporaryStorage":
                        continue
                    storageRoom = room
                if storageRoom:
                    storageRoomPosition = storageRoom.getPosition()
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
                            quest = src.quests.questMap["DrawStockpile"](tryHard=True,itemType=None,stockpileType="s",targetPositionBig=storageRoomPosition,targetPosition=position,reason="add a storage spot to the storage room")
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

                room = terrain.getRoomByPosition((7,7,0))[0]
                if metalBarsFound and not room.getItemByPosition((7,2,0)):
                    quest = src.quests.questMap["PlaceItem"](targetPositionBig=(7,7,0),targetPosition=(7,2,0),itemType="MetalBars",reason="prepare producing a wall")
                    return ([quest],None)

                if caseFound and not room.getItemByPosition((8,1,0)):
                    quest = src.quests.questMap["PlaceItem"](targetPositionBig=(7,7,0),targetPosition=(8,1,0),itemType="Case",reason="prepare producing a wall")
                    return ([quest],None)

                if not caseFound:
                    quest = src.quests.questMap["Scavenge"](toCollect="Case",reason="get more materials to produce walls with")
                    return ([quest],None)
                if not metalBarsFound:
                    quest = src.quests.questMap["Scavenge"](toCollect="MetalBars",reason="get more materials to build walls with")
                    return ([quest],None)
                if not doorFound:
                    quest = src.quests.questMap["Scavenge"](toCollect="Door",reason="get more building materials")
                    return ([quest],None)

            if len(terrain.rooms) < 7:
                terrain = character.getTerrain()
                room = terrain.getRoomByPosition((7,7,0))[0]
                cityPlaner = room.getItemByPosition((5,2,0))[0]
                storageRoom = None
                for room in terrain.rooms:
                    if not room.tag == "temporaryStorage":
                        continue
                    storageRoom = room
                if storageRoom:
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
                            quest = src.quests.questMap["DrawStockpile"](tryHard=True,itemType=None,stockpileType="s",targetPositionBig=storageRoomPosition,targetPosition=position,reason="add a storage spot to the storage room")
                            quests.append(quest)
                        if quests:
                            return (quests,None)

            if len(character.getTerrain().rooms) < 4:
                quest = src.quests.questMap["Scavenge"](toCollect="Wall",reason="get more building materials and pass some time")
                quest.assignToCharacter(character)
                return ([quest],None)

            if len(character.getTerrain().rooms) < 5:
                if not character.getFreeInventorySpace():
                    quest = src.quests.questMap["ClearInventory"](returnToTile=False,reason="restock the base and have space in your inventory")
                    if not dryRun:
                        self.startWatching(quest,self.handQuestFailure,"failed")
                    return ([quest],None)

                room = character.getTerrain().getRoomByPosition((7,7,0))[0]
                epochArtwork = room.getItemsByType("EpochArtwork")[0]
                if epochArtwork.recalculateGlasstears(character,dryRun=True):
                    quest = src.quests.questMap["GetEpochEvaluation"](reason="start recieving the reward for building the third room")
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
                    quest = src.quests.questMap["GetEpochReward"](rewardType="machine operating",reason="get a clone to use machines for you")
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
                                quest2 = src.quests.questMap["FetchItems"](toCollect=inputSlot[1],amount=amount,reason="fetch materials from storage")
                                quest4 = src.quests.questMap["RestockRoom"](toRestock=inputSlot[1],targetPosition=checkRoom.getPosition(),reason="fill input stockpiles for machines")
                                return ([quest4,quest2],None)


            #set special purpose room
            if len(terrain.rooms) < 7:
                if len(cityPlaner.specialPurposeRooms) < 2:
                    for room in terrain.rooms:
                        if room.getPosition() == (7,7,0):
                            continue
                        if room.getPosition() in cityPlaner.specialPurposeRooms:
                            continue
                        if room.getPosition() in cityPlaner.generalPurposeRooms:
                            continue
                        if (len(room.itemsOnFloor) > 13+13+11+11 or room.floorPlan or room.storageSlots or len(room.walkingSpace) > 4 or room.inputSlots):
                            continue
                        
                        quest = src.quests.questMap["DesignateRoom"](roomPosition=room.getPosition(),roomType="specialPurposeRoom",roomTag="temporaryProduction1",reason="reserve a room to set up temporary production line")
                        return ([quest],None)

            if len(terrain.rooms) < 6:
                terrain = character.getTerrain()
                checkRoom = None
                for room in terrain.rooms:
                    if not room.tag == "temporaryProduction1":
                        continue
                    checkRoom = room
                if checkRoom:
                    positions = [(3,3,0),(6,3,0),(3,6,0),(6,6,0),(9,9,0),(7,9,0),(5,9,0)]
                    machineRoomPosition = checkRoom.getPosition()
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
                                quest1 = src.quests.questMap["SetUpMachine"](targetPositionBig=machineRoomPosition,targetPosition=pos,itemType=itemType,reason="set up temporary scrap compactor production")
                                quest2 = src.quests.questMap["DrawStockpile"](tryHard=True,itemType="MetalBars",stockpileType="i",targetPositionBig=machineRoomPosition,targetPosition=(pos[0]-1,pos[1],0),reason="set up temporary scrap compactor production")
                                quest4 = src.quests.questMap["DrawStockpile"](tryHard=True,itemType=itemType,stockpileType="o",targetPositionBig=machineRoomPosition,targetPosition=(pos[0]+1,pos[1],0),reason="set up temporary scrap compactor production")

                                return ([quest4,quest2,quest1],None)
                            elif itemType == "Rod":
                                quest1 = src.quests.questMap["SetUpMachine"](targetPositionBig=machineRoomPosition,targetPosition=pos,itemType=itemType,reason="set up temporary rod production")
                                quest2 = src.quests.questMap["DrawStockpile"](tryHard=True,itemType="MetalBars",stockpileType="i",targetPositionBig=machineRoomPosition,targetPosition=(pos[0]-1,pos[1],0),reason="set up temporary rod production")

                                return ([quest2,quest1],None)
                            elif itemType == "Frame":
                                quest1 = src.quests.questMap["SetUpMachine"](targetPositionBig=machineRoomPosition,targetPosition=pos,itemType=itemType,reason="set up temporary frame production")
                                quest2 = src.quests.questMap["DrawStockpile"](tryHard=True,itemType="Rod",stockpileType="i",targetPositionBig=machineRoomPosition,targetPosition=(pos[0]-1,pos[1],0),reason="set up temporary frame production")

                                return ([quest2,quest1],None)
                            elif itemType == "Case":
                                quest1 = src.quests.questMap["SetUpMachine"](targetPositionBig=machineRoomPosition,targetPosition=pos,itemType=itemType,reason="set up temporary case production")
                                quest2 = src.quests.questMap["DrawStockpile"](tryHard=True,itemType="Frame",stockpileType="i",targetPositionBig=machineRoomPosition,targetPosition=(pos[0]-1,pos[1],0),reason="set up temporary case production")
                                quest4 = src.quests.questMap["DrawStockpile"](tryHard=True,itemType=itemType,stockpileType="o",targetPositionBig=machineRoomPosition,targetPosition=(pos[0]+1,pos[1],0),reason="set up temporary case production")

                                return ([quest4,quest2,quest1],None)
                            else:
                                quest1 = src.quests.questMap["SetUpMachine"](targetPositionBig=machineRoomPosition,targetPosition=pos,itemType=itemType,reason="set up temporary "+itemType+" production")
                                quest2 = src.quests.questMap["DrawStockpile"](tryHard=True,itemType="MetalBars",stockpileType="i",targetPositionBig=machineRoomPosition,targetPosition=(pos[0]-1,pos[1],0),reason="set up temporary "+itemType+" production")
                                quest3 = src.quests.questMap["DrawStockpile"](tryHard=True,itemType="Case",stockpileType="i",targetPositionBig=machineRoomPosition,targetPosition=(pos[0],pos[1]-1,0),reason="set up temporary "+itemType+" production")
                                quest4 = src.quests.questMap["DrawStockpile"](tryHard=True,itemType=itemType,stockpileType="o",targetPositionBig=machineRoomPosition,targetPosition=(pos[0]+1,pos[1],0),reason="set up temporary "+itemType+" production")

                                return ([quest4,quest2,quest3,quest1],None)

            if len(character.getTerrain().rooms) < 5:
                quest = src.quests.questMap["Scavenge"](reason="get more materials and pass some time")
                return ([quest],None)

            if len(character.getTerrain().rooms) < 6:

                room = character.getTerrain().getRoomByPosition((7,7,0))[0]
                epochArtwork = room.getItemsByType("EpochArtwork")[0]
                if epochArtwork.recalculateGlasstears(character,dryRun=True):
                    quest = src.quests.questMap["GetEpochEvaluation"](reason="start getting the reward for building another room")
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
                    quest = src.quests.questMap["GetEpochReward"](rewardType="resource fetching",reason="get another clone to help you out")
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

                        quest2 = src.quests.questMap["FetchItems"](toCollect=inputSlot[1],amount=1,reason="fetch materials from storage")
                        quest3 = src.quests.questMap["RestockRoom"](toRestock=inputSlot[1],targetPosition=room.getPosition(),reason="fill input stockpiles")
                        return ([quest3,quest2],None)

            if len(character.getTerrain().rooms) < 6:
                for room in terrain.rooms:
                    inputSlots = room.getEmptyInputslots(itemType="Scrap")
                    for inputSlot in inputSlots:
                        if room.getItemByPosition(inputSlot[0]):
                            continue
                        quest1 = src.quests.questMap["GatherScrap"](reason="have Scrap to supply the city with")
                        quest3 = src.quests.questMap["RestockRoom"](toRestock="Scrap",reason="ensure scrap supply",targetPosition=room.getPosition())
                        return ([quest3,quest1],None)

            if len(terrain.rooms) < 7:
                checkRoom = None
                for room in terrain.rooms:
                    if not room.tag == "temporaryProduction1":
                        continue
                    checkRoom = room
                if checkRoom:
                    machineRoomPosition = checkRoom.getPosition()
                    pos = (9,3,0)
                    if not checkRoom.getItemByPosition(pos):
                        quest1 = src.quests.questMap["SetUpMachine"](targetPositionBig=machineRoomPosition,targetPosition=pos,itemType="ScrapCompactor",reason="set up temporary scrap compactor production")
                        quest2 = src.quests.questMap["DrawStockpile"](tryHard=True,itemType="MetalBars",stockpileType="i",targetPositionBig=machineRoomPosition,targetPosition=(pos[0]-1,pos[1],0),reason="set up temporary scrap compactor production")
                        quest4 = src.quests.questMap["DrawStockpile"](tryHard=True,itemType="ScrapCompactor",stockpileType="o",targetPositionBig=machineRoomPosition,targetPosition=(pos[0]+1,pos[1],0),reason="set up temporary scrap compactor production")

                        return ([quest4,quest2,quest1],None)

            if len(terrain.rooms) < 7:
                checkRoom = None
                for room in terrain.rooms:
                    if not room.tag == "temporaryProduction1":
                        continue
                    checkRoom = room
                if checkRoom:
                    machineRoomPosition = checkRoom.getPosition()
                    pos = (3,9,0)
                    if not checkRoom.getItemByPosition(pos):
                        quest1 = src.quests.questMap["DrawStockpile"](tryHard=True,itemType="Scrap",stockpileType="i",targetPositionBig=machineRoomPosition,targetPosition=(pos[0]-1,pos[1],0),reason="set up temporary MetalBars production")
                        quest2 = src.quests.questMap["PlaceItem"](targetPositionBig=machineRoomPosition,targetPosition=pos,itemType="ScrapCompactor",tryHard=True,boltDown=True,reason="set up temporary MetalBars production")
                        return ([quest1,quest2],None)

            #set special purpose room
            if len(terrain.rooms) < 7:
                if len(cityPlaner.specialPurposeRooms) < 3:
                    for room in terrain.rooms:
                        if room.getPosition() == (7,7,0):
                            continue
                        if room.getPosition() in cityPlaner.specialPurposeRooms:
                            continue
                        if room.getPosition() in cityPlaner.generalPurposeRooms:
                            continue
                        if (len(room.itemsOnFloor) > 13+13+11+11 or room.floorPlan or room.storageSlots or len(room.walkingSpace) > 4 or room.inputSlots):
                            continue
                    
                        quest = src.quests.questMap["DesignateRoom"](roomPosition=room.getPosition(),roomType="specialPurposeRoom",roomTag="temporaryProduction2",reason="set up second temporary production room")
                        return ([quest],None)

            if len(character.getTerrain().rooms) == 6:
                room = character.getTerrain().getRoomByPosition((7,7,0))[0]
                epochArtwork = room.getItemsByType("EpochArtwork")[0]
                if epochArtwork.recalculateGlasstears(character,dryRun=True):
                    quest = src.quests.questMap["GetEpochEvaluation"](reason="start getting the reward for building another room")
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
                    quest = src.quests.questMap["GetEpochReward"](rewardType="resource gathering",reason="spawn another clone to help you out")
                    return ([quest],None)

            if len(terrain.rooms) < 7:
                checkRoom = None
                for room in terrain.rooms:
                    if not room.tag == "temporaryProduction2":
                        continue
                    checkRoom = room
                if checkRoom:
                    positions = [(3,2,0),(3,3,0),(3,5,0),(3,6,0),(3,8,0),(3,9,0),]
                    machineRoomPosition2 = checkRoom.getPosition()
                    for pos in positions:
                        if not checkRoom.getItemByPosition(pos):
                            quest1 = src.quests.questMap["DrawStockpile"](tryHard=True,itemType="Scrap",stockpileType="i",targetPositionBig=machineRoomPosition2,targetPosition=(pos[0]-1,pos[1],0),reason="increase temporary scrap compacting capacity")
                            quest2 = src.quests.questMap["PlaceItem"](targetPositionBig=machineRoomPosition2,targetPosition=pos,itemType="ScrapCompactor",tryHard=True,boltDown=True,reason="increase temporary scrap compacting capacity")
                            quest3 = src.quests.questMap["DrawStockpile"](tryHard=True,itemType="MetalBars",stockpileType="o",targetPositionBig=machineRoomPosition2,targetPosition=(pos[0]+1,pos[1],0),reason="increase temporary scrap compacting capacity")
                            return ([quest1,quest3,quest2],None)

            if len(terrain.rooms) < 7:
                checkRoom = None
                for room in terrain.rooms:
                    if not room.tag == "temporaryProduction2":
                        continue
                    checkRoom = room
                if checkRoom:
                    positions = [(3,2,0),(3,3,0),(3,5,0),(3,6,0),]
                    machineRoomPosition2 = checkRoom.getPosition()
                    for pos in positions:
                        pos = (pos[0]+2,pos[1],0)
                        quests = []
                        if not checkRoom.getItemByPosition(pos):
                            quest = src.quests.questMap["SetUpMachine"](targetPositionBig=machineRoomPosition2,targetPosition=pos,itemType="Rod",reason="set up case production line")
                            quests.append(quest)
                        pos = (pos[0]+2,pos[1],0)
                        if not checkRoom.getItemByPosition(pos):
                            quest = src.quests.questMap["SetUpMachine"](targetPositionBig=machineRoomPosition2,targetPosition=pos,itemType="Frame",reason="set up case production line")
                            quests.append(quest)
                        pos = (pos[0]+2,pos[1],0)
                        if not checkRoom.getItemByPosition(pos):
                            quest1 = src.quests.questMap["SetUpMachine"](targetPositionBig=machineRoomPosition2,targetPosition=pos,itemType="Case",reason="set up case production line")
                            quest2 = src.quests.questMap["DrawStockpile"](tryHard=True,itemType="Case",stockpileType="o",targetPositionBig=machineRoomPosition2,targetPosition=(pos[0]+1,pos[1],0),reason="set up case production line")
                            quests.append(quest1)
                            quests.append(quest2)

                        if quests:
                            return (quests,None)

            if len(terrain.rooms) < 7:
                checkRoom = None
                for room in terrain.rooms:
                    if not room.tag == "temporaryProduction1":
                        continue
                    checkRoom = room
                if checkRoom:
                    machineRoomPosition = checkRoom.getPosition()
                    pos = (9,6,0)
                    if not checkRoom.getItemByPosition(pos):
                        quest1 = src.quests.questMap["DrawStockpile"](tryHard=True,itemType="RoomBuilder",stockpileType="o",targetPositionBig=machineRoomPosition,targetPosition=(pos[0]+1,pos[1],0),reason="set up room builder machine")
                        quest2 = src.quests.questMap["DrawStockpile"](tryHard=True,itemType="Case",stockpileType="i",targetPositionBig=machineRoomPosition,targetPosition=(pos[0]-1,pos[1],0),reason="set up room builder machine")
                        quest3 = src.quests.questMap["DrawStockpile"](tryHard=True,itemType="pusher",stockpileType="i",targetPositionBig=machineRoomPosition,targetPosition=(pos[0],pos[1]-1,0),reason="set up room builder machine")
                        quest4 = src.quests.questMap["DrawStockpile"](tryHard=True,itemType="puller",stockpileType="i",targetPositionBig=machineRoomPosition,targetPosition=(pos[0],pos[1]+1,0),reason="set up room builder machine")
                        quest5 = src.quests.questMap["SetUpMachine"](targetPositionBig=machineRoomPosition,targetPosition=pos,itemType="RoomBuilder",reason="set up room builder machine")

                        return ([quest5,quest4,quest3,quest2,quest1],None)

            if len(terrain.rooms) < 7:
                checkRoom = None
                for room in terrain.rooms:
                    if not room.tag == "temporaryProduction2":
                        continue
                    checkRoom = room
                if checkRoom:
                    quests = []
                    pos = (5,8,0)
                    if not checkRoom.getItemByPosition(pos):
                        quest2 = src.quests.questMap["SetUpMachine"](targetPositionBig=machineRoomPosition2,targetPosition=pos,itemType="Stripe",reason="set up production room builder base materials")
                        quests.append(quest2)
                    pos = (7,8,0)
                    if not checkRoom.getItemByPosition(pos):
                        quest1 = src.quests.questMap["SetUpMachine"](targetPositionBig=machineRoomPosition2,targetPosition=pos,itemType="pusher",reason="set up production room builder base materials")
                        quest2 = src.quests.questMap["DrawStockpile"](tryHard=True,itemType="pusher",stockpileType="o",targetPositionBig=machineRoomPosition2,targetPosition=(pos[0]+1,pos[1],0),reason="set up production room builder base materials")
                        quests.append(quest1)
                        quests.append(quest2)
                    if quests:
                        return (quests,None)

                    quests = []
                    pos = (5,9,0)
                    if not checkRoom.getItemByPosition(pos):
                        quest2 = src.quests.questMap["SetUpMachine"](targetPositionBig=machineRoomPosition2,targetPosition=pos,itemType="Bolt",reason="set up production room builder base materials")
                        quests.append(quest2)
                    pos = (7,9,0)
                    if not checkRoom.getItemByPosition(pos):
                        quest1 = src.quests.questMap["SetUpMachine"](targetPositionBig=machineRoomPosition2,targetPosition=pos,itemType="puller",reason="set up production room builder base materials")
                        quest2 = src.quests.questMap["DrawStockpile"](tryHard=True,itemType="puller",stockpileType="o",targetPositionBig=machineRoomPosition2,targetPosition=(pos[0]+1,pos[1],0),reason="set up production room builder base materials")
                        quests.append(quest1)
                        quests.append(quest2)
                    if quests:
                        return (quests,None)

            if len(terrain.rooms) < 7:
                for room in terrain.rooms:
                    if not room.floorPlan:
                        continue

                    if "storageSlots" in room.floorPlan:
                        if not room.floorPlan.get("storageSlots"):
                            del room.floorPlan["storageSlots"]

                    if not room.floorPlan:
                        continue

                    quest1 = src.quests.questMap["GoToTile"](targetPosition=room.getPosition(),reason="go to unpainted room")
                    quest2 = src.quests.questMap["DrawFloorPlan"](targetPosition=room.getPosition(),reason="paint the markings for the new room")
                    return ([quest2,quest1],None)


            #################
            ###
            ##  generic end phase
            #
            #################

            # set floor plans
            floorPlansToSet = ["wallProduction","basicMaterialsProduction","caseProduction","storage","scrapCompactor","scrapCompactorProduction","basicRoombuildingItemsProduction","storage",]
            hasAllFloorPlans = False
            for room in terrain.rooms:
                if room.tag in floorPlansToSet:
                    floorPlansToSet.remove(room.tag)
            if floorPlansToSet:
                for room in cityPlaner.getAvailableRooms():
                    quest = src.quests.questMap["AssignFloorPlan"](roomPosition=room.getPosition(),floorPlanType=floorPlansToSet[0],reason="start the process of making the room useful")
                    return ([quest],None)
            else:
                hasAllFloorPlans = True

            room = character.getTerrain().getRoomByPosition((7,7,0))[0]
            epochArtwork = room.getItemsByType("EpochArtwork")[0]
            if epochArtwork.recalculateGlasstears(character,dryRun=True):
                quest = src.quests.questMap["GetEpochEvaluation"](reason="start getting the reward for building another room")
                return ([quest],None)

            
            #spwan NPCs
            foundMachinePlacer = False
            hasAllNPCs = True
            for duty in ["painting","machine placing","hauling"]:
                hasNPC = False
                for otherChar in character.getTerrain().characters:
                    if otherChar == character:
                        continue
                    if duty in otherChar.duties:
                        hasNPC = True
                for checkRoom in character.getTerrain().rooms:
                    for otherChar in checkRoom.characters:
                        if otherChar == character:
                            continue
                        if duty in otherChar.duties:
                            hasNPC = True

                if not hasNPC:
                    hasAllNPCs = False

                if hasNPC and duty == "machine placing":
                    foundMachinePlacer = True

                if not hasNPC and epochArtwork.charges >= 10:
                    quest = src.quests.questMap["GetEpochReward"](rewardType="spawn "+duty+" NPC",reason="spawn another clone to help you out")
                    return ([quest],None)

            if hasAllFloorPlans:
                floorPlansToSet = ["wallProduction","basicMaterialsProduction","caseProduction","storage","scrapCompactor","scrapCompactorProduction","basicRoombuildingItemsProduction","storage",]

                for room in cityPlaner.getAvailableRooms():
                    quest = src.quests.questMap["AssignFloorPlan"](roomPosition=room.getPosition(),floorPlanType=random.choice(floorPlansToSet),reason="increase the bases production")
                    return ([quest],None)
            if hasAllNPCs:
                numItems = 0
                for scrapField in terrain.scrapFields:
                    numItems += len(terrain.itemsByBigCoordinate.get(scrapField,[]))
                if numItems < 100 and epochArtwork.charges >= 20:
                    quest = src.quests.questMap["GetEpochReward"](rewardType="spawn scrap",reason="ensure enough scrap is available")
                    return ([quest],None)

                if numItems >= 100:
                    102/0

            if hasAllFloorPlans and hasAllNPCs:
                if not dryRun and not self.shownTutorialEnd:
                    text = """

You build a base! Great!
This means you reached the end of the tutorial.
And to be frank you reached the end of the availabe basebuilder content.

There is more stuff prepared that can be added.
But i need to get feedback and polish the basic basebuilding first.
Otherwise the whole thing might end up unfun.

So do your part and reach me.
Even if it is just to tell me you reached this screen.
It would make my day to see that.

You can press enter to continue running the game.
On that note, did you know that the tutorial base does not include food?

For your convinience full auto mode is now enabled.
Press * to start it, press ctrl-d to stop it.
"""
                    src.interaction.showInterruptText(text)
                    self.shownTutorialEnd = True
                    character.disableCommandsOnPlus = False

            # remove special room designations
            for room in terrain.rooms:
                if not room.tag in ("temporaryProduction2","temporaryProduction1","temporaryStorage"):
                    continue
                if room.floorPlan:
                    continue
                if room.buildSites:
                    continue
                if len(room.walkingSpace) > 4:
                    continue
                if room.inputSlots:
                    continue
                if room.outputSlots:
                    continue
                if room.storageSlots:
                    continue
                if len(room.itemsOnFloor) > 13+13+11+11:
                    continue
                quest = src.quests.questMap["DesignateRoom"]("undesignate room",roomPosition=room.getPosition(),roomType="undesignate",reason="free up the room for different usage")
                return ([quest],None)

            # check for wall production
            completedWallProductionRoom = False
            for room in terrain.rooms:
                if not room.tag == "wallProduction":
                    continue
                if room.floorPlan:
                    continue
                if room.buildSites:
                    continue
                completedWallProductionRoom = True
                break

            # clear tmp wall production
            if completedWallProductionRoom:
                checkRoom = None
                for room in terrain.rooms:
                    if not room.tag == "temporaryProduction1":
                        continue
                    checkRoom = room
                if checkRoom:
                    checkRoomPos = checkRoom.getPosition()
                    positions = [(2,3,0),(3,2,0),(3,3,0),(4,3,0),
                                 (5,3,0),(6,2,0),(6,3,0),(7,3,0),
                                 (2,6,0),(3,5,0),(3,6,0),(4,6,0)]

                    quests = []
                    for position in positions:
                        if not checkRoom.getPaintedByPosition(position):
                            continue
                        quest = src.quests.questMap["DeleteMarking"](targetPosition=position,targetPositionBig=checkRoom.getPosition(),reason="remove old markings")
                        quests.append(quest)
                    if quests:
                        return (quests,None)

                    quests = []
                    for position in positions:
                        if not checkRoom.getItemByPosition(position):
                            continue
                        quest = src.quests.questMap["CleanSpace"](targetPosition=position,targetPositionBig=checkRoom.getPosition(),reason="remove old machinery")
                        quests.append(quest)
                    if quests:
                        return (quests,None)

            # clear command centre wall production
            if completedWallProductionRoom:
                positions = [(7,1,0),(8,1,0),(8,1,0),(9,1,0),
                             (7,2,0),(8,2,0),(8,2,0),(9,2,0),]
                checkRoom = terrain.getRoomByPosition((7,7,0))[0]
                checkRoomPos = checkRoom.getPosition()

                quests = []
                for position in positions:
                    if not checkRoom.getPaintedByPosition(position):
                        continue
                    quest = src.quests.questMap["DeleteMarking"](targetPosition=position,targetPositionBig=checkRoom.getPosition(),reason="remove old markings")
                    quests.append(quest)
                if quests:
                    return (quests,None)

                quests = []
                for position in positions:
                    if not checkRoom.getItemByPosition(position):
                        continue
                    quest = src.quests.questMap["CleanSpace"](targetPosition=position,targetPositionBig=checkRoom.getPosition(),reason="remove old machinery")
                    quests.append(quest)
                if quests:
                    return (quests,None)

            # check for basic material production
            completedBasicMaterialsProductionRoom = False
            for room in terrain.rooms:
                print(room.tag)
                if not room.tag == "basicMaterialsProduction":
                    continue
                if room.floorPlan:
                    continue
                if room.buildSites:
                    continue
                completedBasicMaterialsProductionRoom = True
                break

            # clear tmp material production
            if completedBasicMaterialsProductionRoom:
                checkRoom = None
                for room in terrain.rooms:
                    if not room.tag == "temporaryProduction2":
                        continue
                    checkRoom = room
                if checkRoom:
                    checkRoomPos = checkRoom.getPosition()
                    positions = []

                    for y in range(7,12):
                        for x in range(1,12):
                            positions.append((x,y,0))

                    quests = []
                    for position in positions:
                        if not checkRoom.getPaintedByPosition(position):
                            continue
                        quest = src.quests.questMap["DeleteMarking"](targetPosition=position,targetPositionBig=checkRoom.getPosition(),reason="remove old markings")
                        quests.append(quest)
                    if quests:
                        return (quests,None)

                    quests = []
                    for position in positions:
                        if not checkRoom.getItemByPosition(position):
                            continue
                        quest = src.quests.questMap["CleanSpace"](targetPosition=position,targetPositionBig=checkRoom.getPosition(),reason="remove old machinery")
                        quests.append(quest)
                    if quests:
                        return (quests,None)

            # check for case room
            completedCaseProductionRoom = False
            for room in terrain.rooms:
                if not room.tag == "caseProduction":
                    continue
                if room.floorPlan:
                    continue
                if room.buildSites:
                    continue
                completedCaseProductionRoom = True
                break

            # remove temp case production
            checkRoom = None
            for room in terrain.rooms:
                if not room.tag == "temporaryProduction2":
                    continue
                checkRoom = room
            if completedCaseProductionRoom and checkRoom:
                # remove temp case production
                checkRoomPos = checkRoom.getPosition()
                positions = []

                for y in range(1,12):
                    for x in range(1,12):
                        positions.append((x,y,0))

                quests = []
                counter = 0
                for position in positions:
                    if not checkRoom.getPaintedByPosition(position):
                        continue
                    counter += 1
                    if counter > 5:
                        break
                    quest = src.quests.questMap["DeleteMarking"](targetPosition=position,targetPositionBig=checkRoom.getPosition(),reason="remove old markings")
                    quests.append(quest)
                if quests:
                    return (quests,None)

                quests = []
                counter = 0
                for position in positions:
                    if not checkRoom.getItemByPosition(position):
                        continue
                    counter += 1
                    if counter > 5:
                        break
                    quest = src.quests.questMap["CleanSpace"](targetPosition=position,targetPositionBig=checkRoom.getPosition(),reason="remove old machinery")
                    quests.append(quest)
                if quests:
                    return (quests,None)

            # remove temp case production
            checkRoom = None
            for room in terrain.rooms:
                if not room.tag == "temporaryProduction1":
                    continue
                checkRoom = room
            if completedCaseProductionRoom and checkRoom:
                checkRoomPos = checkRoom.getPosition()
                positions = []

                for y in range(8,12):
                    for x in range(1,12):
                        positions.append((x,y,0))

                quests = []
                counter = 0
                for position in positions:
                    if not checkRoom.getPaintedByPosition(position):
                        continue
                    counter += 1
                    if counter > 5:
                        break
                    quest = src.quests.questMap["DeleteMarking"](targetPosition=position,targetPositionBig=checkRoom.getPosition(),reason="remove old markings")
                    quests.append(quest)
                if quests:
                    return (quests,None)

                quests = []
                counter = 0
                for position in positions:
                    if not checkRoom.getItemByPosition(position):
                        continue
                    counter += 1
                    if counter > 5:
                        break
                    quest = src.quests.questMap["CleanSpace"](targetPosition=position,targetPositionBig=checkRoom.getPosition(),reason="remove old machinery")
                    quests.append(quest)
                if quests:
                    return (quests,None)

            # check for storage room
            completedStorageRoom = False
            for room in terrain.rooms:
                if not room.tag == "storage":
                    continue
                if room.floorPlan:
                    continue
                if room.buildSites:
                    continue
                completedStorageRoom = True
                break

            # remove temp storage
            checkRoom = None
            for room in terrain.rooms:
                if not room.tag == "temporaryStorage":
                    continue
                checkRoom = room
            if completedStorageRoom and checkRoom:
                checkRoomPos = checkRoom.getPosition()
                positions = []

                for y in range(1,12):
                    for x in range(1,12):
                        positions.append((x,y,0))

                quests = []
                counter = 0
                for position in positions:
                    if not checkRoom.getPaintedByPosition(position):
                        continue
                    counter += 1
                    if counter > 5:
                        break
                    quest = src.quests.questMap["DeleteMarking"](targetPosition=position,targetPositionBig=checkRoom.getPosition(),reason="remove old markings")
                    quests.append(quest)
                if quests:
                    return (quests,None)

                quests = []
                counter = 0
                for position in positions:
                    if not checkRoom.getItemByPosition(position):
                        continue
                    counter += 1
                    if counter > 5:
                        break
                    quest = src.quests.questMap["CleanSpace"](targetPosition=position,targetPositionBig=checkRoom.getPosition(),reason="remove old machinery")
                    quests.append(quest)
                if quests:
                    return (quests,None)

            # check for scrap compactor production
            completedScrapCompactorProductionRoom = False
            for room in terrain.rooms:
                if not room.tag == "scrapCompactorProduction":
                    continue
                if room.floorPlan:
                    continue
                if room.buildSites:
                    continue
                completedScrapCompactorProductionRoom = True
                break

            # remove temp scrap compactor production
            checkRoom = None
            for room in terrain.rooms:
                if not room.tag == "temporaryProduction1":
                    continue
                checkRoom = room
            if completedScrapCompactorProductionRoom and checkRoom:
                checkRoomPos = checkRoom.getPosition()
                positions = []

                for y in (3,):
                    for x in range(6,12):
                        positions.append((x,y,0))

                quests = []
                counter = 0
                for position in positions:
                    if not checkRoom.getPaintedByPosition(position):
                        continue
                    counter += 1
                    if counter > 5:
                        break
                    quest = src.quests.questMap["DeleteMarking"](targetPosition=position,targetPositionBig=checkRoom.getPosition(),reason="remove old markings")
                    quests.append(quest)
                if quests:
                    return (quests,None)

                quests = []
                counter = 0
                for position in positions:
                    if not checkRoom.getItemByPosition(position):
                        continue
                    counter += 1
                    if counter > 5:
                        break
                    quest = src.quests.questMap["CleanSpace"](targetPosition=position,targetPositionBig=checkRoom.getPosition(),reason="remove old machinery")
                    quests.append(quest)
                if quests:
                    return (quests,None)

            # check for scrap compacting
            completedScrapCompactorRoom = False
            for room in terrain.rooms:
                if not room.tag == "scrapCompactor":
                    continue
                if room.floorPlan:
                    continue
                if room.buildSites:
                    continue
                completedScrapCompactorRoom = True
                break

            # clear command centre scrap compacting
            if completedScrapCompactorRoom:
                positions = [(9,5,0),(8,5,0),(7,5,0),]
                checkRoom = terrain.getRoomByPosition((7,7,0))[0]
                checkRoomPos = checkRoom.getPosition()

                quests = []
                for position in positions:
                    if not checkRoom.getPaintedByPosition(position):
                        continue
                    quest = src.quests.questMap["DeleteMarking"](targetPosition=position,targetPositionBig=checkRoom.getPosition(),reason="remove old markings")
                    quests.append(quest)
                if quests:
                    return (quests,None)

                quests = []
                for position in positions:
                    if not checkRoom.getItemByPosition(position):
                        continue
                    quest = src.quests.questMap["CleanSpace"](targetPosition=position,targetPositionBig=checkRoom.getPosition(),reason="remove old machinery")
                    quests.append(quest)
                if quests:
                    return (quests,None)

            # check for room building basics
            completedBasicRoombuildingItemsProductionRoom = False
            for room in terrain.rooms:
                if not room.tag == "basicRoombuildingItemsProduction":
                    continue
                if room.floorPlan:
                    continue
                if room.buildSites:
                    continue
                completedBasicRoombuildingItemsProductionRoom = True
                break

            # remove temp scrap compactor production
            checkRoom = None
            for room in terrain.rooms:
                if not room.tag == "temporaryProduction1":
                    continue
                checkRoom = room
            if completedBasicRoombuildingItemsProductionRoom and checkRoom:
                checkRoomPos = checkRoom.getPosition()
                positions = []

                for y in (5,6,7):
                    for x in range(5,12):
                        positions.append((x,y,0))

                quests = []
                counter = 0
                for position in positions:
                    if not checkRoom.getPaintedByPosition(position):
                        continue
                    counter += 1
                    if counter > 5:
                        break
                    quest = src.quests.questMap["DeleteMarking"](targetPosition=position,targetPositionBig=checkRoom.getPosition(),reason="remove old markings")
                    quests.append(quest)
                if quests:
                    return (quests,None)

                quests = []
                counter = 0
                for position in positions:
                    if not checkRoom.getItemByPosition(position):
                        continue
                    counter += 1
                    if counter > 5:
                        break
                    quest = src.quests.questMap["CleanSpace"](targetPosition=position,targetPositionBig=checkRoom.getPosition(),reason="remove old machinery")
                    quests.append(quest)
                if quests:
                    return (quests,None)

            # set up machines
            for room in terrain.rooms:
                if not room.buildSites:
                    continue

                quests = []
                counter = 0
                for buildSite in room.buildSites:
                    if not buildSite[1] == "Machine":
                        continue
                    counter += 1
                    if counter > 5:
                        break
                    quest = src.quests.questMap["SetUpMachine"](itemType=buildSite[2]["toProduce"],targetPositionBig=room.getPosition(),targetPosition=buildSite[0],tryHard=True,reason="to help with setting up the rooms")
                    quests.append(quest)
                if quests:
                    return (quests,None)

            # set up items
            for room in terrain.rooms:
                if not room.buildSites:
                    continue

                quests = []
                counter = 0
                for buildSite in room.buildSites:
                    counter += 1
                    if counter > 5:
                        break
                    quest = src.quests.questMap["PlaceItem"](targetPositionBig=room.getPosition(),targetPosition=buildSite[0],itemType=buildSite[1],tryHard=True,boltDown=True,reason="to help with setting up the rooms")
                    quests.append(quest)
                if quests:
                    return (quests,None)

            # draw some outputslots
            for room in terrain.rooms:
                if not room.floorPlan:
                    continue

                if "outputSlots" in room.floorPlan:
                    if not room.floorPlan.get("outputSlots"):
                        del room.floorPlan["outputSlots"]

                if not room.floorPlan:
                    continue

                if not "outputSlots" in room.floorPlan:
                    continue

                quests = []
                outputSlots = room.floorPlan["outputSlots"][:]
                random.shuffle(outputSlots)
                counter = 0
                for outputSlot in outputSlots:
                    counter += 1
                    if counter > 5:
                        break
                    quest = src.quests.questMap["DrawStockpile"](tryHard=True,itemType=outputSlot[1],stockpileType="o",targetPositionBig=room.getPosition(),targetPosition=outputSlot[0],reason="to help with drawing the markers in rooms")
                    quests.append(quest)
                if quests:
                    return (quests,None)

            # draw some buildSites
            for room in terrain.rooms:
                if not room.floorPlan:
                    continue

                if "buildSites" in room.floorPlan:
                    if not room.floorPlan.get("buildSites"):
                        del room.floorPlan["buildSites"]

                if not room.floorPlan:
                    continue

                if not "buildSites" in room.floorPlan:
                    continue

                quests = []
                buildSites = room.floorPlan["buildSites"][:]
                random.shuffle(buildSites)
                counter = 0
                for buildSite in buildSites:
                    counter += 1
                    if counter > 5:
                        break
                    quest = src.quests.questMap["DrawBuildSite"](tryHard=True,itemType=buildSite[1],targetPositionBig=room.getPosition(),targetPosition=buildSite[0],extraInfo=buildSite[2],reason="to help with drawing the markers in rooms")
                    quests.append(quest)
                if quests:
                    return (quests,None)

            # draw some inputslots
            for room in terrain.rooms:
                if not room.floorPlan:
                    continue

                if "inputSlots" in room.floorPlan:
                    if not room.floorPlan.get("inputSlots"):
                        del room.floorPlan["inputSlots"]

                if not room.floorPlan:
                    continue

                if not "inputSlots" in room.floorPlan:
                    continue

                quests = []
                inputSlots = room.floorPlan["inputSlots"][:]
                random.shuffle(inputSlots)
                counter = 0
                for inputSlot in inputSlots:
                    counter += 1
                    if counter > 5:
                        break
                    quest = src.quests.questMap["DrawStockpile"](tryHard=True,itemType=outputSlot[1],stockpileType="i",targetPositionBig=room.getPosition(),targetPosition=outputSlot[0],reason="to help with drawing the markers in rooms")
                    quests.append(quest)
                if quests:
                    return (quests,None)

            # draw some storageslots
            for room in terrain.rooms:
                if not room.floorPlan:
                    continue

                if "storageSlots" in room.floorPlan:
                    if not room.floorPlan.get("storageSlots"):
                        del room.floorPlan["storageSlots"]

                if not room.floorPlan:
                    continue

                if not "storageSlots" in room.floorPlan:
                    continue

                quests = []
                outputSlots = room.floorPlan["storageSlots"][:]
                random.shuffle(outputSlots)
                counter = 0
                for outputSlot in outputSlots:
                    counter += 1
                    if counter > 5:
                        break
                    quest = src.quests.questMap["DrawStockpile"](tryHard=True,itemType=outputSlot[1],stockpileType="s",targetPositionBig=room.getPosition(),targetPosition=outputSlot[0],reason="to help with drawing the markers in rooms")
                    quests.append(quest)
                if quests:
                    return (quests,None)


            readyWallMachines = []
            readyDoorMachines = []
            readyMachines = []
            readyScrapCompactors = []
            caseRooms = []
            for room in terrain.rooms:
                for item in room.itemsOnFloor:
                    if item.type == "Machine":
                        if item.toProduce == "Wall" and item.readyToUse():
                            readyWallMachines.append(item)
                            continue
                        if item.toProduce == "Door" and item.readyToUse():
                            readyDoorMachines.append(item)
                            continue
                        if item.readyToUse():
                            readyMachines.append(item)
                            continue
                    if item.type == "ScrapCompactor":
                        if item.readyToUse():
                            readyScrapCompactors.append(item)
                            continue

                if room.getEmptyInputslots("Case",fullyEmpty=True):
                    caseRooms.append(room)

            quests = []
            for item in readyDoorMachines:
                quest = src.quests.questMap["OperateMachine"](targetPositionBig=item.container.getPosition(),targetPosition=item.getPosition(),reason="to help with producing basic buiding materials")
                quests.append(quest)
            if quests:
                return (quests,None)

            quests = []
            for item in readyWallMachines:
                quest = src.quests.questMap["OperateMachine"](targetPositionBig=item.container.getPosition(),targetPosition=item.getPosition(),reason="to help with producing basic buiding materials")
                quests.append(quest)
            if quests:
                return (quests,None)

            if caseRooms:
                foundSources = False
                for room in terrain.rooms:
                    if not room.getNonEmptyOutputslots("Case"):
                        continue
                    foundSources = True
                    break
                
                if foundSources:
                    quests = []
                    for room in caseRooms:
                        quest = src.quests.questMap["RestockRoom"](targetPosition=room.getPosition(),toRestock="Case",reason="speed up wall production")
                        quests.append(quest)
                        break
                    if not character.inventory or not character.inventory[-1].type == "Case":
                        quest = src.quests.questMap["FetchItems"](toCollect="Case",reason="have cases to place")
                        quests.append(quest)
                    if len(character.inventory) > 4 and not character.inventory[-1].type == "Case":
                        quest = src.quests.questMap["ClearInventory"](reason="have space for more items")
                        quests.append(quest)
                    if quests:
                        return (quests,None)

            quests = []
            for item in readyMachines:
                quest = src.quests.questMap["OperateMachine"](targetPositionBig=item.container.getPosition(),targetPosition=item.getPosition(),reason="help with item production")
                quests.append(quest)
            if quests:
                return (quests,None)

            quests = []
            for item in readyScrapCompactors:
                quest = src.quests.questMap["OperateMachine"](targetPositionBig=item.container.getPosition(),targetPosition=item.getPosition(),reason="help with item production")
                quests.append(quest)
            if quests:
                return (quests,None)

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
                            quest3 = src.quests.questMap["RestockRoom"](toRestock="Scrap",reason="ensure scrap supply",targetPosition=room.getPosition())
                            return ([quest3,quest1],None)
            
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

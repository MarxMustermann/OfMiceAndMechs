import random

import src


class ExtendBase(src.quests.MetaQuestSequence):
    type = "ExtendBase"

    def __init__(self, description="set up base", creator=None, command=None, lifetime=None):
        questList = []
        super().__init__(questList, creator=creator, lifetime=lifetime)
        self.metaDescription = description
        self.shownTutorialEnd = False
        self.shownTutorialStep1 = False

    def generateTextDescription(self):
        out = []
        if len(self.character.getTerrain().rooms) == 1:
            roomBuilder = src.items.itemMap["RoomBuilder"]()
            wall = src.items.itemMap["Wall"]()
            door = src.items.itemMap["Door"]()
            out.extend(["""
You remember that your task is to set up a base.
You know you are equipped for it, but you remember nothing more.
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
                self.startWatching(quest,self.handleQuestFailure,"failed")
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

    def handleQuestFailure(self,extraParam):
        if not extraParam["quest"] in self.subQuests:
            return

        self.subQuests.remove(extraParam["quest"])
        if extraParam.get("reason") and "no source" in extraParam["reason"] and "Painter" in extraParam["reason"]:
            quest = src.quests.questMap["FetchItems"](tryHard=True,toCollect="Painter",amount=1)
            self.startWatching(quest,self.handleQuestFailure,"failed")
            self.addQuest(quest)
            return

        if extraParam["reason"] == "no storage available":
            terrain = self.character.getTerrain()
            cityPlaner = terrain.getRoomByPosition((7,7,0))[0].getItemByPosition((5,2,0))
            if not cityPlaner:
                quest = src.quests.questMap["DiscardInventory"](reason="be able to act again")
                self.startWatching(quest,self.handleQuestFailure,"failed")
                self.addQuest(quest)
                return
            cityPlaner = cityPlaner[0]
            if cityPlaner.type != "CityPlaner":
                quest = src.quests.questMap["DiscardInventory"](reason="be able to act again")
                self.startWatching(quest,self.handleQuestFailure,"failed")
                self.addQuest(quest)
                return

            for generalPurposeRoom in cityPlaner.generalPurposeRooms:

                terrain = self.character.getTerrain()
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
                        if not dryRun:
                            self.startWatching(quest,self.handleQuestFailure,"failed")
                        quests.append(quest)

                for quest in reversed(quests):
                    self.addQuest(quest)

                quest = src.quests.questMap["DiscardInventory"](reason="be able to pick up a painter")
                self.startWatching(quest,self.handleQuestFailure,"failed")
                self.addQuest(quest)
                return

            quest = src.quests.questMap["DiscardInventory"](reason="be able to act again")
            self.startWatching(quest,self.handleQuestFailure,"failed")
            self.addQuest(quest)
            return

    def getNextStep(self,character=None,ignoreCommands=False,dryRun=True):

        if not self.subQuests:
            if not ignoreCommands:
                submenue = character.macroState.get("submenue")
                if submenue:
                    return (None,(["esc"],"exit the menu"))

            ######
            ###
            ##    analyse base
            #
            ######
            terrain = character.getTerrain()
            cityCore = terrain.getRoomByPosition((7,7,0))[0]
            epochArtwork = cityCore.getItemsByType("EpochArtwork",needsBolted=True)[0]
            cityPlaner = cityCore.getItemsByType("CityPlaner",needsBolted=True)
            if cityPlaner:
                cityPlaner = cityPlaner[0]
            else:
                cityPlaner = None

            # gather npc duties
            npcDuties = {}
            for otherChar in terrain.characters:
                for duty in otherChar.duties:
                    if not duty in npcDuties:
                        npcDuties[duty] = []
                    npcDuties[duty].append(otherChar)
            for checkRoom in character.getTerrain().rooms:
                for otherChar in checkRoom.characters:
                    if otherChar == character:
                        continue
                    for duty in otherChar.duties:
                        if not duty in npcDuties:
                            npcDuties[duty] = []
                        npcDuties[duty].append(otherChar)

            # get tile neighboring the base
            baseNeighbours = []
            offsets = ((0,1,0),(1,0,0),(0,-1,0),(-1,0,0))
            for room in terrain.rooms:
                pos = room.getPosition()
                for offset in offsets:
                    checkPos = (pos[0]+offset[0],pos[1]+offset[1],0)
                    if terrain.getRoomByPosition(checkPos):
                        continue
                    if checkPos in baseNeighbours:
                        continue
                    baseNeighbours.append(checkPos)
            random.shuffle(baseNeighbours)

            # get the possible build sited
            possibleBuildSites = []
            for candidate in baseNeighbours:
                if (not candidate in terrain.scrapFields) and (not candidate in terrain.forests):
                    possibleBuildSites.append(candidate)

            # get assigned floor plans
            assignedFloorPlans = []
            for room in terrain.rooms:
                if not room.tag:
                    continue
                assignedFloorPlans.append(room.tag)

            # get placed machines
            machineMap = {}
            readyMachines = []
            readyScrapCompactors = []
            for room in terrain.rooms:
                for item in room.itemsOnFloor:
                    if item.type == "Machine" and item.bolted:
                        if item.readyToUse():
                            readyMachines.append(item)
                        if not item.toProduce in machineMap:
                            machineMap[item.toProduce] = []
                        machineMap[item.toProduce].append(item)

                    if item.type == "ScrapCompactor" and item.bolted and item.readyToUse():
                        readyScrapCompactors.append(item)

            # count empty storage slots
            numFreeStorage = 0
            for room in terrain.rooms:
                for storageSlot in room.storageSlots:
                    if storageSlot[1] != None:
                        continue
                    items = room.getItemByPosition(storageSlot[0])
                    if items:
                        continue
                    numFreeStorage += 1

            # do storage inventory
            storedItems = {}
            for room in terrain.rooms:
                for storageSlot in room.storageSlots:
                    items = room.getItemByPosition(storageSlot[0])
                    if items:
                        if storageSlot[1] == None or items[-1].type == storageSlot[1]:
                            if not items[-1].type in storedItems:
                                storedItems[items[-1].type] = 0
                            storedItems[items[-1].type] += len(items)
                        continue

            # do output stockpile inventory
            for room in terrain.rooms:
                for outputSlot in room.outputSlots:
                    items = room.getItemByPosition(outputSlot[0])
                    if items:
                        if outputSlot[1] == None or items[-1].type == outputSlot[1]:
                            if not outputSlot[1] in storedItems:
                                storedItems[outputSlot[1]] = 0
                            storedItems[outputSlot[1]] += len(items)
                        continue

            # do inventory of scrap fields
            numItemsScrapfield = 0
            for scrapField in terrain.scrapFields:
                numItemsScrapfield += len(terrain.itemsByBigCoordinate.get(scrapField,[]))

            ######
            ###
            ##    get rewards
            #
            #####

            if epochArtwork.recalculateGlasstears(character,dryRun=True):
                quest = src.quests.questMap["GetEpochEvaluation"](reason="start getting the reward for building the first room")
                return ([quest],None)

            if numItemsScrapfield < 100 and epochArtwork.charges >= 20:
                quest = src.quests.questMap["GetEpochReward"](rewardType="spawn scrap",reason="ensure enough scrap is available")
                return ([quest],None)

            if numItemsScrapfield >= 100:
                for duty in ["room building","scavenging","machine operation","resource gathering","resource fetching","painting","machine placing","hauling"]:
                    if not duty in npcDuties and epochArtwork.charges >= 10:
                        quest = src.quests.questMap["GetEpochReward"](rewardType="spawn "+duty+" NPC",reason="spawn another clone to help you out")
                        return ([quest],None)

                if epochArtwork.charges >= 10:
                    duty = random.choice(["room building","scavenging","machine operation","resource gathering","resource fetching","painting","machine placing","hauling"])
                    quest = src.quests.questMap["GetEpochReward"](rewardType="spawn "+duty+" NPC",reason="spawn random clone")
                    return ([quest],None)

            ######
            ###
            ##    extend base
            #
            #####

            # set up city planer
            if not cityPlaner:
                quest = src.quests.questMap["PlaceItem"](targetPositionBig=(7,7,0),targetPosition=(5,2,0),itemType="CityPlaner",tryHard=True,boltDown=True,reason="to be able to plan city expansion")
                return ([quest],None)

            # ensure there is a general purpose room
            if cityPlaner and not cityPlaner.generalPurposeRooms:
                for room in terrain.rooms:
                    if room.getPosition() == (7,0,0):
                        continue
                    if room.getPosition() in cityPlaner.specialPurposeRooms:
                        continue
                    if room.getPosition() in cityPlaner.generalPurposeRooms:
                        continue
                    if (len(room.itemsOnFloor) > 13+13+11+11 or room.floorPlan or room.storageSlots or len(room.walkingSpace) > 4 or room.inputSlots):
                        continue

                    quest = src.quests.questMap["DesignateRoom"](roomPosition=room.getPosition(),roomType="generalPurposeRoom",reason="reserve some room for unforeseen needs")
                    return ([quest],None)

            # add storage room if needed
            if cityPlaner and cityPlaner.getAvailableRooms():
                if numFreeStorage < 20:
                    quest = src.quests.questMap["AssignFloorPlan"](roomPosition=cityPlaner.getAvailableRooms()[0].getPosition(),floorPlanType="storage",reason="increase storage")
                    return ([quest],None)

            # assign basic floor plans
            if cityPlaner and cityPlaner.getAvailableRooms():
                floorPlansToSet = ["storage","wallProduction","caseProduction","basicMaterialsProduction","scrapCompactor","scrapCompactorProduction","basicRoombuildingItemsProduction",]
                for room in terrain.rooms:
                    if room.tag in floorPlansToSet:
                        floorPlansToSet.remove(room.tag)
                if floorPlansToSet:
                    for room in cityPlaner.getAvailableRooms():
                        quest = src.quests.questMap["AssignFloorPlan"](roomPosition=room.getPosition(),floorPlanType=floorPlansToSet[0],reason="start the process of making the room useful")
                        return ([quest],None)

            # assign random floor plans
            if cityPlaner:
                for room in cityPlaner.getAvailableRooms():
                    floorPlansToSet = ["wallProduction","caseProduction","basicMaterialsProduction","scrapCompactor","scrapCompactorProduction","basicRoombuildingItemsProduction",]
                    quest = src.quests.questMap["AssignFloorPlan"](roomPosition=room.getPosition(),floorPlanType=random.choice(floorPlansToSet),reason="set a random floor plan")
                    return ([quest],None)

            # add emergency storage
            if cityPlaner.generalPurposeRooms and numFreeStorage < 10:
                for generalPurposeRoom in cityPlaner.generalPurposeRooms:
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

                    if quests:
                        return (list(reversed(quests)),None)

            # remove emergency storage
            if cityPlaner.generalPurposeRooms and numFreeStorage > 50:
                numStorageToRemove = numFreeStorage-30

                for generalPurposeRoom in cityPlaner.generalPurposeRooms:
                    room = terrain.getRoomByPosition(generalPurposeRoom)[0]

                    quests = []
                    counter = 0
                    for storageSlot in room.storageSlots:
                        counter += 1
                        if counter > numStorageToRemove:
                            break
                        if counter > 5:
                            break

                        quest = src.quests.questMap["CleanSpace"](targetPositionBig=room.getPosition(),targetPosition=storageSlot[0],reason="free up general purpose rooms")
                        quests.append(quest)
                        quest = src.quests.questMap["DeleteMarking"](targetPosition=storageSlot[0],targetPositionBig=room.getPosition(),reason="free up general purpose rooms")
                        quests.append(quest)

                    if quests:
                        return (quests,None)

            """
            # remove command centre storage
            if cityPlaner.generalPurposeRooms and numFreeStorage > 30:
                numStorageToRemove = numFreeStorage-30

                room = terrain.getRoomByPosition((7,7,0))[0]

                quests = []
                counter = 0
                for storageSlot in room.storageSlots:
                    counter += 1
                    if counter > numStorageToRemove:
                        break
                    if counter > 5:
                        break

                    quest = src.quests.questMap["CleanSpace"](targetPositionBig=room.getPosition(),targetPosition=storageSlot[0],reason="free up general purpose rooms")
                    quests.append(quest)
                    quest = src.quests.questMap["DeleteMarking"](targetPosition=storageSlot[0],targetPositionBig=room.getPosition(),reason="free up general purpose rooms")
                    quests.append(quest)

                if quests:
                    return (quests,None)
            """

            # clean up the command centre
            itemsOnFloor = cityCore.itemsOnFloor
            random.shuffle(itemsOnFloor)
            quests = []
            for item in itemsOnFloor:
                if item.bolted:
                    continue

                if not item.type in ("Wall","Door","RoomBuilder",):
                    continue

                inStorage = False
                pos = item.getPosition()
                for storageSlot in cityCore.storageSlots:
                    if storageSlot[0] == pos:
                        inStorage = True
                for outputSlot in cityCore.outputSlots:
                    if outputSlot[0] == pos and outputSlot[1] == item.type:
                        inStorage = True

                if inStorage:
                    continue

                generatedPath = cityCore.getPathCommandTile((6,6,0),item.getPosition(),character=character,ignoreEndBlocked=True)[0]
                if not generatedPath:
                    continue

                quest = src.quests.questMap["CleanSpace"](targetPositionBig=(7,7,0),targetPosition=item.getPosition(),reason="unclutter the city core and put the items into storage")
                quests.append(quest)

                if len(quests) > 4:
                    break
            if quests:
                return (quests,None)

            # remove items that on walkways (cleaning)
            quests = []
            for room in terrain.rooms:
                for walkingSpacePos in room.walkingSpace:
                    items = room.getItemByPosition(walkingSpacePos)
                    if not items:
                        continue
                    if items[0].bolted:
                        continue
                    quest = src.quests.questMap["CleanSpace"](targetPositionBig=room.getPosition(),targetPosition=walkingSpacePos,reason="keep walking spaces clear")
                    quests.append(quest)
            if quests:
                return (quests,None)

            # remove items that are in wrong places (cleaning)
            quests = []
            for room in terrain.rooms:
                for inputSlot in room.inputSlots:
                    items = room.getItemByPosition(inputSlot[0])
                    if not items:
                        continue
                    if items[0].bolted:
                        continue
                    if items[0].type == inputSlot[1]:
                        continue

                    quest = src.quests.questMap["CleanSpace"](targetPositionBig=room.getPosition(),targetPosition=inputSlot[0],reason="remove items that were in the wrong stockpile")
                    quests.append(quest)
            if quests:
                return (quests,None)

            # remove items that are in wrong places (cleaning)
            quests = []
            for room in terrain.rooms:
                for outputSlot in room.outputSlots:
                    items = room.getItemByPosition(outputSlot[0])
                    if not items:
                        continue
                    if items[0].bolted:
                        continue
                    if items[0].type == outputSlot[1]:
                        continue

                    quest = src.quests.questMap["CleanSpace"](targetPositionBig=room.getPosition(),targetPosition=outputSlot[0],reason="remove items that were in the wrong stockpile")
                    quests.append(quest)
            if quests:
                return (quests,None)

            # remove items that are in wrong places (cleaning)
            quests = []
            for room in terrain.rooms:
                for storageSlot in room.storageSlots:
                    if not storageSlot[1]:
                        continue
                    items = room.getItemByPosition(storageSlot[0])
                    if not items:
                        continue
                    if items[0].bolted:
                        continue
                    if items[0].type == storageSlot[1]:
                        continue

                    quest = src.quests.questMap["CleanSpace"](targetPositionBig=room.getPosition(),targetPosition=storageSlot[0],reason="remove items that were in the wrong stockpile")
                    quests.append(quest)
            if quests:
                return (quests,None)

            ######
            ###
            ##    emulate clone activity
            #
            #####

            if not "room building" in npcDuties:
                for candidate in possibleBuildSites:
                    if len(terrain.itemsByBigCoordinate.get(candidate,[])) < 5:
                        quest = src.quests.questMap["BuildRoom"](targetPosition=candidate,tryHard=True,reason="start extending the base",takeAnyUnbolted=True)
                        return ([quest],None)
                for candidate in possibleBuildSites:
                    quest = src.quests.questMap["BuildRoom"](targetPosition=candidate,tryHard=True,reason="start extending the base",takeAnyUnbolted=True)
                    return ([quest],None)

            if not "machine placing" in npcDuties:

                # set up machines
                for room in terrain.rooms:
                    if not room.buildSites:
                        continue

                    buildSites = room.buildSites[:]
                    quests = []
                    counter = 0
                    counter2 = 0
                    while counter < len(buildSites):
                        buildSite = buildSites[counter]
                        counter += 1
                        if buildSite[1] != "Machine":
                            continue

                        if counter2 > 4:
                            break

                        counter2 += 1
                        quest = src.quests.questMap["SetUpMachine"](itemType=buildSite[2]["toProduce"],targetPositionBig=room.getPosition(),targetPosition=buildSite[0],tryHard=True,reason="to help with setting up the rooms")
                        quests.append(quest)
                        for buildSite2 in buildSites[counter:]:
                            if buildSite[2] == buildSite2[2]:
                                quest = src.quests.questMap["SetUpMachine"](itemType=buildSite2[2]["toProduce"],targetPositionBig=room.getPosition(),targetPosition=buildSite2[0],tryHard=True,reason="to help with setting up the rooms")
                                quests.append(quest)
                                buildSites.remove(buildSite2)
                                counter2 += 1
                    if quests:
                        return (quests,None)

                # set up items
                for room in terrain.rooms:
                    if not room.buildSites:
                        continue

                    buildSites = room.buildSites[:]
                    quests = []
                    counter = 0
                    counter2 = 0
                    while counter < len(buildSites):
                        buildSite = buildSites[counter]
                        counter += 1

                        if counter2 > 4:
                            break

                        counter2 += 1
                        quest = src.quests.questMap["PlaceItem"](targetPositionBig=room.getPosition(),targetPosition=buildSite[0],itemType=buildSite[1],tryHard=True,boltDown=True,reason="to help with setting up the rooms")
                        quests.append(quest)
                        for buildSite2 in buildSites[counter:]:
                            if buildSite[1] == buildSite2[1]:
                                quest = src.quests.questMap["PlaceItem"](targetPositionBig=room.getPosition(),targetPosition=buildSite2[0],itemType=buildSite2[1],tryHard=True,boltDown=True,reason="to help with setting up the rooms")
                                quests.append(quest)
                                buildSites.remove(buildSite2)
                                counter2 += 1
                    if quests:
                        return (quests,None)

            if not "painting" in npcDuties:
                for room in terrain.rooms:
                    if not room.floorPlan:
                        continue

                    if "storageSlots" in room.floorPlan and not room.floorPlan.get("storageSlots"):
                        del room.floorPlan["storageSlots"]

                    if not room.floorPlan:
                        continue

                    quest1 = src.quests.questMap["GoToTile"](targetPosition=room.getPosition(),reason="go to unpainted room")
                    quest2 = src.quests.questMap["DrawFloorPlan"](targetPosition=room.getPosition(),reason="paint the markings for the new room")
                    return ([quest2,quest1],None)

            if not "machine operation" in npcDuties:
                # operate machines in general
                quests = []
                firstMachine = None
                for item in readyMachines:
                    if not firstMachine:
                        firstMachine = item

                    if item.container != firstMachine.container:
                        continue

                    quest = src.quests.questMap["OperateMachine"](targetPositionBig=item.container.getPosition(),targetPosition=item.getPosition(),reason="help with item production")
                    quests.append(quest)
                if quests:
                    return (quests,None)

                # operate scrap compactors in general
                quests = []
                firstMachine = None
                for item in readyScrapCompactors:
                    if not firstMachine:
                        firstMachine = item

                    if item.container != firstMachine.container:
                        continue

                    quest = src.quests.questMap["OperateMachine"](targetPositionBig=item.container.getPosition(),targetPosition=item.getPosition(),reason="help with item production")
                    quests.append(quest)
                if quests:
                    return (quests,None)

            if not "hauling" in npcDuties:
                for checkRoom in terrain.rooms:
                    for inputSlot in checkRoom.getEmptyInputslots(fullyEmpty=True):
                        if not inputSlot[1]:
                            continue

                        for _outputSlot in checkRoom.getNonEmptyOutputslots(inputSlot[1]):
                            amount = None
                            if inputSlot[1] == "Case":
                                amount = 1
                            quest2 = src.quests.questMap["FetchItems"](toCollect=inputSlot[1],amount=amount,reason="get material to fill input stockpiles")
                            quest4 = src.quests.questMap["RestockRoom"](toRestock=inputSlot[1],targetPosition=checkRoom.getPosition(),reason="fill input stockpiles for machines")
                            return ([quest4,quest2],None)

                for checkRoom in terrain.rooms:
                    for inputSlot in checkRoom.getEmptyInputslots():
                        if not inputSlot[1]:
                            continue

                        for _outputSlot in checkRoom.getNonEmptyOutputslots(inputSlot[1]):
                            amount = None
                            if inputSlot[1] == "Case":
                                amount = 1
                            quest2 = src.quests.questMap["FetchItems"](toCollect=inputSlot[1],amount=amount,reason="fetch materials from storage")
                            quest4 = src.quests.questMap["RestockRoom"](toRestock=inputSlot[1],targetPosition=checkRoom.getPosition(),reason="fill input stockpiles for machines")
                            return ([quest4,quest2],None)

            if not "resource fetching" in npcDuties:
                for checkRoom in terrain.rooms:
                    for inputSlot in checkRoom.getEmptyInputslots(fullyEmpty=True):
                        if not inputSlot[1]:
                            continue

                        for sourceRoom in terrain.rooms:
                            if sourceRoom == checkRoom:
                                continue

                            for _outputSlot in sourceRoom.getNonEmptyOutputslots(inputSlot[1]):
                                amount = None
                                if inputSlot[1] == "Case":
                                    amount = 1
                                quest2 = src.quests.questMap["FetchItems"](toCollect=inputSlot[1],amount=amount,reason="fetch materials from storage")
                                quest4 = src.quests.questMap["RestockRoom"](toRestock=inputSlot[1],targetPosition=checkRoom.getPosition(),reason="fill input stockpiles for machines")
                                return ([quest4,quest2],None)

                for checkRoom in terrain.rooms:
                    for inputSlot in checkRoom.getEmptyInputslots():
                        if not inputSlot[1]:
                            continue

                        for sourceRoom in terrain.rooms:
                            if sourceRoom == checkRoom:
                                continue

                            for _outputSlot in sourceRoom.getNonEmptyOutputslots(inputSlot[1]):
                                amount = None
                                if inputSlot[1] == "Case":
                                    amount = 1
                                quest2 = src.quests.questMap["FetchItems"](toCollect=inputSlot[1],amount=amount,reason="fetch materials from storage")
                                quest4 = src.quests.questMap["RestockRoom"](toRestock=inputSlot[1],targetPosition=checkRoom.getPosition(),reason="fill input stockpiles for machines")
                                return ([quest4,quest2],None)

            if not "resource gathering" in npcDuties:
                for room in character.getTerrain().rooms:
                    for inputSlot in room.inputSlots:
                        if inputSlot[1] == "Scrap":
                            items = room.getItemByPosition(inputSlot[0])
                            if not items:
                                quest1 = src.quests.questMap["GatherScrap"](reason="have Scrap to supply the city with")
                                quest3 = src.quests.questMap["RestockRoom"](toRestock="Scrap",reason="ensure scrap supply",targetPosition=room.getPosition())
                                return ([quest3,quest1],None)

                for room in character.getTerrain().rooms:
                    for inputSlot in room.inputSlots:
                        if inputSlot[1] == "Scrap":
                            items = room.getItemByPosition(inputSlot[0])
                            if items and items[-1].type == "Scrap" and items[-1].amount < 15:
                                quest1 = src.quests.questMap["GatherScrap"](reason="have Scrap to supply the city with")
                                quest3 = src.quests.questMap["RestockRoom"](toRestock="Scrap",reason="ensure scrap supply",targetPosition=room.getPosition())
                                return ([quest3,quest1],None)

            if not "scavenging" in npcDuties:
                if not character.getFreeInventorySpace():
                    quest = src.quests.questMap["ClearInventory"]()
                    return ([quest],None)

                quest = src.quests.questMap["Scavenge"]()
                return ([quest],None)

            ######
            ###
            ##    speed up production
            #
            #####

            # operate machines
            quests = []
            firstMachine = None
            for item in readyMachines:
                if not item.toProduce in ("Wall","Door","RoomBuilder",):
                    continue

                if not firstMachine:
                    firstMachine = item

                if item.container != firstMachine.container:
                    continue

                quest = src.quests.questMap["OperateMachine"](targetPositionBig=item.container.getPosition(),targetPosition=item.getPosition(),reason="help with item production")
                quests.append(quest)
            if quests:
                return (quests,None)

            # set up machines
            for room in terrain.rooms:
                if not room.buildSites:
                    continue

                buildSites = room.buildSites[:]
                quests = []
                counter = 0
                counter2 = 0
                while counter < len(buildSites):
                    buildSite = buildSites[counter]
                    counter += 1
                    if buildSite[1] != "Machine":
                        continue

                    if counter2 > 4:
                        break

                    counter2 += 1
                    quest = src.quests.questMap["SetUpMachine"](itemType=buildSite[2]["toProduce"],targetPositionBig=room.getPosition(),targetPosition=buildSite[0],tryHard=True,reason="to help with setting up the rooms")
                    quests.append(quest)
                    for buildSite2 in buildSites[counter:]:
                        if buildSite[2] == buildSite2[2]:
                            quest = src.quests.questMap["SetUpMachine"](itemType=buildSite2[2]["toProduce"],targetPositionBig=room.getPosition(),targetPosition=buildSite2[0],tryHard=True,reason="to help with setting up the rooms")
                            quests.append(quest)
                            buildSites.remove(buildSite2)
                            counter2 += 1
                if quests:
                    return (quests,None)

            # set up items
            for room in terrain.rooms:
                if not room.buildSites:
                    continue

                buildSites = room.buildSites[:]
                quests = []
                counter = 0
                counter2 = 0
                while counter < len(buildSites):
                    buildSite = buildSites[counter]
                    counter += 1

                    if counter2 > 4:
                        break

                    counter2 += 1
                    quest = src.quests.questMap["PlaceItem"](targetPositionBig=room.getPosition(),targetPosition=buildSite[0],itemType=buildSite[1],tryHard=True,boltDown=True,reason="to help with setting up the rooms")
                    quests.append(quest)
                    for buildSite2 in buildSites[counter:]:
                        if buildSite[1] == buildSite2[1]:
                            quest = src.quests.questMap["PlaceItem"](targetPositionBig=room.getPosition(),targetPosition=buildSite2[0],itemType=buildSite2[1],tryHard=True,boltDown=True,reason="to help with setting up the rooms")
                            quests.append(quest)
                            buildSites.remove(buildSite2)
                            counter2 += 1
                if quests:
                    return (quests,None)

            # draw some outputslots
            for room in terrain.rooms:
                if not room.floorPlan:
                    continue

                if "outputSlots" in room.floorPlan and not room.floorPlan.get("outputSlots"):
                    del room.floorPlan["outputSlots"]

                if not room.floorPlan:
                    continue

                if not "outputSlots" in room.floorPlan:
                    continue

                quests = []
                outputSlots = room.floorPlan["outputSlots"][:]
                random.shuffle(outputSlots)
                counter = 0
                counter2 = 0
                while counter < len(outputSlots):
                    outputSlot = outputSlots[counter]
                    if counter2 > 4:
                        break

                    counter += 1
                    counter2 += 1

                    quest = src.quests.questMap["DrawStockpile"](tryHard=True,itemType=outputSlot[1],stockpileType="o",targetPositionBig=room.getPosition(),targetPosition=outputSlot[0],reason="to help with drawing the markers in rooms")
                    quests.append(quest)

                    for outputSlot2 in outputSlots[counter:]:
                        if outputSlot[1] == outputSlot2[1]:
                            quest = src.quests.questMap["DrawStockpile"](tryHard=True,itemType=outputSlot2[1],stockpileType="o",targetPositionBig=room.getPosition(),targetPosition=outputSlot2[0],reason="to help with drawing the markers in rooms")
                            quests.append(quest)
                            outputSlots.remove(outputSlot2)
                            counter2 += 1

                if quests:
                    return (quests,None)

            # draw some buildSites
            for room in terrain.rooms:
                if not room.floorPlan:
                    continue

                if "buildSites" in room.floorPlan and not room.floorPlan.get("buildSites"):
                    del room.floorPlan["buildSites"]

                if not room.floorPlan:
                    continue

                if not "buildSites" in room.floorPlan:
                    continue

                quests = []
                buildSites = room.floorPlan["buildSites"][:]
                random.shuffle(buildSites)

                counter = 0
                counter2 = 0
                while counter < len(buildSites):
                    if counter2 > 4:
                        break
                    buildSite = buildSites[counter]

                    counter += 1
                    counter2 += 1

                    quest = src.quests.questMap["DrawBuildSite"](tryHard=True,itemType=buildSite[1],targetPositionBig=room.getPosition(),targetPosition=buildSite[0],extraInfo=buildSite[2],reason="to help with drawing the markers in rooms")
                    quests.append(quest)

                    for buildSite2 in buildSites[counter:]:
                        if buildSite[1] == buildSite2[1] and buildSite[2] == buildSite2[2]:
                            quest = src.quests.questMap["DrawBuildSite"](tryHard=True,itemType=buildSite2[1],targetPositionBig=room.getPosition(),targetPosition=buildSite2[0],extraInfo=buildSite2[2],reason="to help with drawing the markers in rooms")
                            quests.append(quest)
                            buildSites.remove(buildSite2)
                            counter2 += 1

                if quests:
                    return (quests,None)

            # draw some inputslots
            for room in terrain.rooms:
                if not room.floorPlan:
                    continue

                if "inputSlots" in room.floorPlan and not room.floorPlan.get("inputSlots"):
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
                    quest = src.quests.questMap["DrawStockpile"](tryHard=True,itemType=inputSlot[1],stockpileType="i",targetPositionBig=room.getPosition(),targetPosition=inputSlot[0],reason="to help with drawing the markers in rooms")
                    quests.append(quest)
                if quests:
                    return (quests,None)

            # draw some storageslots
            for room in terrain.rooms:
                if not room.floorPlan:
                    continue

                if "storageSlots" in room.floorPlan and not room.floorPlan.get("storageSlots"):
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

            ######
            ###
            ##    desperately speed up production
            #
            #####

            # operate machines
            quests = []
            firstMachine = None
            for item in readyMachines:
                if not item.toProduce in ("Case",):
                    continue

                if not firstMachine:
                    firstMachine = item

                if item.container != firstMachine.container:
                    continue

                quest = src.quests.questMap["OperateMachine"](targetPositionBig=item.container.getPosition(),targetPosition=item.getPosition(),reason="help with item production")
                quests.append(quest)
            if quests:
                return (quests,None)

            # fill fully empty inputs
            for checkRoom in terrain.rooms:
                for inputSlot in checkRoom.getEmptyInputslots(fullyEmpty=True):
                    if not inputSlot[1]:
                        continue

                    for sourceRoom in terrain.rooms:
                        for _outputSlot in sourceRoom.getNonEmptyOutputslots(inputSlot[1]):
                            amount = None
                            if inputSlot[1] == "Case":
                                amount = 1
                            quest2 = src.quests.questMap["FetchItems"](toCollect=inputSlot[1],amount=amount,reason="fetch materials from storage")
                            quest4 = src.quests.questMap["RestockRoom"](toRestock=inputSlot[1],targetPosition=checkRoom.getPosition(),reason="fill input stockpiles for machines")
                            return ([quest4,quest2],None)

            # clear inventory
            if character.inventory:
                quest = src.quests.questMap["ClearInventory"]()
                return ([quest],None)

            # directly produce missing items
            if not "Wall" in storedItems:
                quest = src.quests.questMap["ProduceItem"](itemType="Wall",tryHard=True)
                return ([quest],None)
            if not "Door" in storedItems:
                quest = src.quests.questMap["ProduceItem"](itemType="Door",tryHard=True)
                return ([quest],None)
            if not "RoomBuilder" in storedItems:
                quest = src.quests.questMap["ProduceItem"](itemType="RoomBuilder",tryHard=True)
                return ([quest],None)

            ######
            ###
            ##    really desperately speed up production
            #
            #####

            # operate machines in general
            quests = []
            firstMachine = None
            for item in readyMachines:
                if not firstMachine:
                    firstMachine = item

                if item.container != firstMachine.container:
                    continue

                quest = src.quests.questMap["OperateMachine"](targetPositionBig=item.container.getPosition(),targetPosition=item.getPosition(),reason="help with item production")
                quests.append(quest)
            if quests:
                return (quests,None)

            # operate scrap compactors in general
            quests = []
            firstMachine = None
            for item in readyScrapCompactors:
                if not firstMachine:
                    firstMachine = item

                if item.container != firstMachine.container:
                    continue

                quest = src.quests.questMap["OperateMachine"](targetPositionBig=item.container.getPosition(),targetPosition=item.getPosition(),reason="help with item production")
                quests.append(quest)
            if quests:
                return (quests,None)

            # fill partially empty inputs
            for checkRoom in terrain.rooms:
                for inputSlot in checkRoom.getEmptyInputslots():
                    if not inputSlot[1]:
                        continue

                    for sourceRoom in terrain.rooms:
                        for _outputSlot in sourceRoom.getNonEmptyOutputslots(inputSlot[1]):
                            amount = None
                            if inputSlot[1] == "Case":
                                amount = 1
                            quest2 = src.quests.questMap["FetchItems"](toCollect=inputSlot[1],amount=amount,reason="fetch materials from storage")
                            quest4 = src.quests.questMap["RestockRoom"](toRestock=inputSlot[1],targetPosition=checkRoom.getPosition(),reason="fill input stockpiles for machines")
                            return ([quest4,quest2],None)

            # produce wall yourself
            if cityPlaner.generalPurposeRooms or "wallProduction" in assignedFloorPlans:
                wallmachineWithoutCoolDown = None
                for item in machineMap.get("Wall",[]):
                    if item.checkCoolDownEnded():
                        wallmachineWithoutCoolDown = item

                quest = src.quests.questMap["ProduceItem"](itemType="Wall",tryHard=True)
                return ([quest],None)

            1337/0

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

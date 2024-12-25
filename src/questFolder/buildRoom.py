import src
import random

class BuildRoom(src.quests.MetaQuestSequence):
    type = "BuildRoom"

    def __init__(self, description="build room", creator=None, command=None, lifetime=None, targetPosition=None,tryHard=False, reason=None, takeAnyUnbolted=False):
        questList = []
        super().__init__(questList, creator=creator, lifetime=lifetime)
        self.metaDescription = description
        self.shortCode = "M"
        self.targetPosition = targetPosition
        self.tryHard = tryHard
        self.reason = reason
        self.takeAnyUnbolted = takeAnyUnbolted
        self.type = "BuildRoom"

    def builtRoom(self,extraParam):
        if self.targetPosition and extraParam["room"].getPosition() != self.targetPosition:
            return
        self.postHandler()

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character, self.builtRoom, "built room")
        super().assignToCharacter(character)

    def generateTextDescription(self):
        roombuilder = src.items.itemMap["RoomBuilder"]()
        reason = ""
        if self.reason:
            reason = f", to {self.reason}"
        out = [f"""
Build a room on the tile {self.targetPosition}{reason}.""","""

"""]

        if self.tryHard:
            out.append("""
Try as hard as you can to achieve this.
If something is missing, produce it.
If something disturbs you, destroy it.
""")

        if not self.subQuests:
            out.append((src.interaction.urwid.AttrSpec("#f00", "black"),"""
This quest has no subquests. Press r to generate subquests for this quest."""))
        else:
            out.append((src.interaction.urwid.AttrSpec("#080", "black"),"""
Press d to move the cursor and show the subquests description.
"""))

        return out

    def handleQuestFailure(self,extraParam):
        super().handleQuestFailure(extraParam)
        reason = extraParam.get("reason")
        if reason and self.tryHard:
            if reason.startswith("no source for item "):
                if reason.split(" ")[4] not in ("Wall","MetalBars","Scrap",):
                        newQuest = src.quests.questMap["MetalWorking"](toProduce=reason.split(" ")[4],amount=1,produceToInventory=True,tryHard=self.tryHard)
                        self.addQuest(newQuest)
                        self.startWatching(newQuest,self.handleQuestFailure,"failed")
                        return
                if "metal working" in self.character.duties:
                    if reason.split(" ")[4] not in ("MetalBars","Scrap",):
                        newQuest = src.quests.questMap["MetalWorking"](toProduce=reason.split(" ")[4],amount=1,produceToInventory=True,tryHard=self.tryHard)
                        self.addQuest(newQuest)
                        self.startWatching(newQuest,self.handleQuestFailure,"failed")
                        return

                if self.tryHard:
                    if reason.split(" ")[4] == "MetalBars":
                        newQuest = src.quests.questMap["ScrapHammering"](amount=1,tryHard=self.tryHard)
                        self.addQuest(newQuest)
                        self.startWatching(newQuest,self.handleQuestFailure,"failed")
                        return
                    if reason.split(" ")[4] == ("MetalBars","Scrap",):
                        newQuest = src.quests.questMap["GatherScrap"](tryHard=self.tryHard)
                        self.addQuest(newQuest)
                        self.startWatching(newQuest,self.handleQuestFailure,"failed")
                        return
            if reason.startswith("full inventory"):
                newQuest = src.quests.questMap["ClearInventory"]()
                self.addQuest(newQuest)
                self.startWatching(newQuest,self.handleQuestFailure,"failed")
                return
        self.fail(reason)

    def getNextStep(self,character=None,ignoreCommands=False, dryRun = True):
        terrain = character.getTerrain()
        if terrain.alarm and not self.tryHard:
            if not dryRun:
                self.fail("alarm")
            return (None,None)

        if not self.subQuests:
            if not ignoreCommands:
                submenue = character.macroState.get("submenue")
                if submenue:
                    return (None,(["esc"],"exit submenu"))

            items = terrain.getItemByPosition((15*self.targetPosition[0]+7,15*self.targetPosition[1]+7,0))
            if not items or items[-1].type != "RoomBuilder":
                quest = src.quests.questMap["PlaceItem"](targetPosition=(7,7,0),targetPositionBig=self.targetPosition,itemType="RoomBuilder",reason="start building the room")
                return ([quest],None)

            wallPositions = [(1,1,0),(1,13,0),(13,1,0),(13,13,0)]
            wallPositions.extend([(2,1,0),(3,1,0),(4,1,0),(5,1,0),(6,1,0)])
            wallPositions.extend([(8,1,0),(9,1,0),(10,1,0),(11,1,0),(12,1,0)])
            wallPositions.extend([(2,13,0),(3,13,0),(4,13,0),(5,13,0),(6,13,0)])
            wallPositions.extend([(8,13,0),(9,13,0),(10,13,0),(11,13,0),(12,13,0)])
            wallPositions.extend([(1,2,0),(1,3,0),(1,4,0),(1,5,0),(1,6,0)])
            wallPositions.extend([(13,2,0),(13,3,0),(13,4,0),(13,5,0),(13,6,0)])
            wallPositions.extend([(1,8,0),(1,9,0),(1,10,0),(1,11,0),(1,12,0)])
            wallPositions.extend([(13,8,0),(13,9,0),(13,10,0),(13,11,0),(13,12,0)])
            missingWallPositions = []
            for wallPos in wallPositions:
                items = character.getTerrain().getItemByPosition((15*self.targetPosition[0]+wallPos[0],15*self.targetPosition[1]+wallPos[1],0))
                if items and items[-1].type == "Wall":
                    continue
                missingWallPositions.append(wallPos)

            if missingWallPositions:
                if not character.inventory or character.inventory[-1].type != "Wall":
                    amount = None
                    if len(missingWallPositions) < 10:
                        amount = len(missingWallPositions)
                    quest = src.quests.questMap["FetchItems"](toCollect="Wall",takeAnyUnbolted=self.takeAnyUnbolted,tryHard=self.tryHard,amount=amount,reason="have walls for the rooms outline")
                    return ([quest],None)

                quests = []
                counter = 0
                for missingWallPos in missingWallPositions:
                    if not (len(character.inventory) > counter and character.inventory[-1-counter].type == "Wall"):
                        break
                    quest = src.quests.questMap["PlaceItem"](targetPosition=missingWallPos,targetPositionBig=self.targetPosition,itemType="Wall",tryHard=self.tryHard,reason="build the outline of the room")
                    quests.append(quest)
                    counter += 1
                return (list(reversed(quests)),None)

            doorPositions = [(7,1,0),(1,7,0),(7,13,0),(13,7,0)]
            missingDoorPositions = []
            for doorPos in doorPositions:
                items = character.getTerrain().getItemByPosition((15*self.targetPosition[0]+doorPos[0],15*self.targetPosition[1]+doorPos[1],0))
                if items and items[-1].type == "Door":
                    continue
                missingDoorPositions.append(doorPos)

            if missingDoorPositions:
                numDoors = 0
                for item in character.inventory:
                    if item.type == "Door":
                        numDoors += 1

                amount = len(missingDoorPositions)
                if numDoors < amount:
                    quest = src.quests.questMap["FetchItems"](toCollect="Door",takeAnyUnbolted=self.takeAnyUnbolted,tryHard=self.tryHard,amount=amount,reason="have doors to place")
                    return ([quest],None)

                quests = []
                counter = 0
                for missingDoorPos in missingDoorPositions:
                    if not numDoors:
                        break
                    numDoors -= 1
                    quest = src.quests.questMap["PlaceItem"](targetPosition=missingDoorPos,targetPositionBig=self.targetPosition,itemType="Door",tryHard=self.tryHard,reason="add doors to the room")
                    quests.append(quest)
                    counter += 1
                return (list(reversed(quests)),None)

            roomBuilderPos = (7,7,0)
            if character.getDistance((15*self.targetPosition[0]+7,15*self.targetPosition[1]+7,0)) > 1:
                quest = src.quests.questMap["GoToPosition"](targetPosition=roomBuilderPos,ignoreEndBlocked=True,reason="get next to the RoomBuilder")
                return ([quest], None)

            offsets = {(0,0,0):"j",(1,0,0):"Jd",(-1,0,0):"Ja",(0,1,0):"Js",(0,-1,0):"Jw"}
            for (offset,command) in offsets.items():
                if character.getPosition(offset=offset) == (15*self.targetPosition[0]+7,15*self.targetPosition[1]+7,0):
                    return (None, (command,"activate the RoomBuilder"))

        quest = src.quests.questMap["GoToTile"](targetPosition=self.targetPosition)
        return ([quest], None)

    def triggerCompletionCheck(self,character=None):
        if not character:
            return False
        if character.getTerrain().getRoomByPosition(self.targetPosition):
            self.postHandler()
            return True
        return False

    def getQuestMarkersTile(self,character):
        result = super().getQuestMarkersTile(character)
        result.append((self.targetPosition,"target"))
        return result

    @staticmethod
    def generateDutyQuest(beUsefull,character,currentRoom, dryRun):
        #src.gamestate.gamestate.mainChar = character
        terrain = character.getTerrain()
        try:
            terrain.alarm
        except:
            terrain.alarm = False
        if terrain.alarm:
            return (None,None)

        for x in range(1,13):
            for y in range(1,13):
                items = terrain.getItemByPosition((x*15+7,y*15+7,0))
                if items and items[0].type == "RoomBuilder":
                    quest = src.quests.questMap["BuildRoom"](targetPosition=(x,y,0),lifetime=1000)
                    if not dryRun:
                        beUsefull.idleCounter = 0
                    return ([quest],None)

        rooms = terrain.getRoomByPosition((7,7,0))
        if rooms:
            room = rooms[0]
            cityPlaner = room.getItemByType("CityPlaner")
            if cityPlaner:
                for candidate in cityPlaner.plannedRooms:
                    items = terrain.itemsByCoordinate.get((candidate[0]*15+7,candidate[1]*15+7,0))
                    if items and items[-1].type == "RoomBuilder":
                        quest = src.quests.questMap["BuildRoom"](targetPosition=candidate,lifetime=1000)
                        if not dryRun:
                            beUsefull.idleCounter = 0
                        return ([quest],None)

                while cityPlaner.plannedRooms:
                    if terrain.getRoomByPosition(cityPlaner.plannedRooms[0]):
                        cityPlaner.plannedRooms.remove(cityPlaner.plannedRooms[0])
                        continue

                    quest= src.quests.questMap["BuildRoom"](targetPosition=cityPlaner.plannedRooms[0],lifetime=1000)
                    if not dryRun:
                        beUsefull.idleCounter = 0
                    return ([quest],None)

        if not cityPlaner or cityPlaner.autoExtensionThreashold > 0:
            # do not build more rooms when there is an empty room
            numEmptyRooms = 0
            for room in terrain.rooms:
                if room.tag:
                    continue
                if (len(room.itemsOnFloor) > 13+13+11+11 or room.floorPlan or room.storageSlots or len(room.walkingSpace) > 4 or room.inputSlots or room.buildSites):
                    continue
                numEmptyRooms += 1

            threashold = 1
            if cityPlaner:
                threashold = cityPlaner.autoExtensionThreashold

            if numEmptyRooms >= threashold:
                return (None,None)

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

            possibleBuildSites = []
            for candidate in baseNeighbours:
                if (candidate not in terrain.scrapFields) and (candidate not in terrain.forests):
                    possibleBuildSites.append(candidate)

            for candidate in possibleBuildSites:
                items = terrain.itemsByCoordinate.get((candidate[0]*15+7,candidate[1]*15+7,0))
                if items and items[-1].type == "RoomBuilder":
                    quest = src.quests.questMap["BuildRoom"](targetPosition=candidate,lifetime=1000)
                    if not dryRun:
                        beUsefull.idleCounter = 0
                    return ([quest],None)

            for candidate in possibleBuildSites:
                if len(terrain.itemsByBigCoordinate.get(candidate,[])) < 5:
                    quest = src.quests.questMap["BuildRoom"](targetPosition=candidate,lifetime=1000)
                    if not dryRun:
                        beUsefull.idleCounter = 0
                    return ([quest],None)
            for candidate in possibleBuildSites:
                quest = src.quests.questMap["BuildRoom"](targetPosition=candidate,lifetime=1000)
                if not dryRun:
                        beUsefull.idleCounter = 0
                return ([quest],None)
            return (None,None)
        return (None,None)

src.quests.addType(BuildRoom)

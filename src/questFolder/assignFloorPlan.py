import src
import random

class AssignFloorPlan(src.quests.MetaQuestSequence):
    type = "AssignFloorPlan"

    def __init__(self, description="assign floor plan", creator=None, roomPosition=None, floorPlanType=None, reason=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        self.roomPosition = roomPosition
        self.floorPlanType = floorPlanType
        self.reason = reason

    def generateTextDescription(self):
        out = []
        reason = ""
        if self.reason:
            reason = f", to {self.reason}"
        text = f"""
Assign a floor plan to room {self.roomPosition}{reason}.

Set the floor plan: {self.floorPlanType}

(setting the wrong floor plan may break the tutorial, but is FUN)
"""
        out = [text]
        return out

    def getNextStep(self,character=None,ignoreCommands=False,dryRun=True):

        # handle weird edge cases
        if self.subQuests:
            return (None,None)

        # handle menues
        submenue = character.macroState["submenue"]
        if submenue and not ignoreCommands:

            # open map
            if submenue.tag == "applyOptionSelection":
                command = submenue.get_command_to_select_option("showMap")
                return (None,(command,"show the map"))

            # select build site on map
            if isinstance(submenue,src.menuFolder.mapMenu.MapMenu) and not ignoreCommands:
                cityPlaner = character.container.getItemsByType("CityPlaner")[0]
                if self.roomPosition not in cityPlaner.getAvailableRoomPositions():
                    return self._solver_trigger_fail(dryRun,"room already registered")
                selection_command = "f"
                if self.roomPosition in cityPlaner.plannedRooms:
                    selection_command = "x"
                command = submenue.get_command_to_select_position(coordinate=self.roomPosition,selectionCommand=selection_command)
                if command:
                    return (None,(command,"set a floor plan"))

            # select floor plan
            if submenue.tag == "floorplanSelection":
                command = submenue.get_command_to_select_option(self.floorPlanType)
                return (None,(command,"select the floor plan"))

            # close unkown menues
            if submenue.tag not in ("advancedInteractionSelection",):
                return (None,(["esc"],"close menu"))

        # activate production item when marked
        action = self.generate_confirm_interaction_command(allowedItems=["CityPlaner"])
        if action:
            return action

        # enter room
        if not character.container.isRoom:
            if character.getTerrain().getRoomByPosition(character.getBigPosition()):
                quest = src.quests.questMap["EnterRoom"](reason="be able to act properly")
                return ([quest],None)
            else:
                quest = src.quests.questMap["GoHome"](reason="go inside")
                return ([quest],None)

        # go to room with city planer
        cityPlaner = character.container.getItemByType("CityPlaner")
        if not cityPlaner:
            for room in character.getTerrain().rooms:
                cityPlaner = room.getItemByType("CityPlaner")
                if not cityPlaner:
                    continue
                quest = src.quests.questMap["GoToTile"](targetPosition=cityPlaner.getBigPosition(),description="go to command centre",reason="go to command centre")
                return ([quest],None)

            return self._solver_trigger_fail(dryRun,"no planer")

        # soft fail on weird state
        if not character.container.isRoom:
            return (None,(".","stand around confused"))

        # activate the CityPlaner
        cityPlaner = character.container.getItemsByType("CityPlaner")[0]
        command = None
        if character.getPosition(offset=(1,0,0)) == cityPlaner.getPosition():
            command = "d"
        if character.getPosition(offset=(-1,0,0)) == cityPlaner.getPosition():
            command = "a"
        if character.getPosition(offset=(0,1,0)) == cityPlaner.getPosition():
            command = "s"
        if character.getPosition(offset=(0,-1,0)) == cityPlaner.getPosition():
            command = "w"
        if character.getPosition(offset=(0,0,0)) == cityPlaner.getPosition():
            command = "."
        if command:
            interactionCommand = "J"
            if submenue:
                if submenue.tag == "advancedInteractionSelection":
                    interactionCommand = ""
                else:
                    return (None,(["esc"],"close menu"))
            return (None,(interactionCommand+command,"activate the CityPlaner"))

        # go to the CityPlaner
        quest = src.quests.questMap["GoToPosition"](targetPosition=cityPlaner.getPosition(), description="go to CityPlaner",ignoreEndBlocked=True,reason="be able to reach the CityPlaner")
        return ([quest],None)

    """
    never complete
    """
    def triggerCompletionCheck(self,character=None, dryRun=True):
        if not character:
            return None

        terrain = character.getTerrain()
        room = terrain.getRoomByPosition(self.roomPosition)[0]

        if room.floorPlan:
            if not dryRun:
                self.postHandler()
            return True
        return None

    def getSolvingCommandString(self, character, dryRun=True):
        nextStep = self.getNextStep(character)
        if nextStep == (None,None):
            return super().getSolvingCommandString(character)
        return self.getNextStep(character)[1]


    def handleAssignFloorPlan(self,extraParams):
        self.triggerCompletionCheck(extraParams["character"],dryRun=False)

    def getQuestMarkersTile(self,character):
        result = super().getQuestMarkersTile(character)
        result.append(((self.roomPosition[0],self.roomPosition[1]),"target"))
        return result

    def assignToCharacter(self, character):
        if self.character:
            return None

        self.startWatching(character,self.handleAssignFloorPlan, "assigned floor plan")

        return super().assignToCharacter(character)

    def getQuestMarkersSmall(self,character,renderForTile=False):
        '''
        return the quest markers for the normal map
        '''
        if isinstance(character.container,src.rooms.Room):
            if renderForTile:
                return []
        else:
            if not renderForTile:
                return []

        result = super().getQuestMarkersSmall(character,renderForTile=renderForTile)
        if not renderForTile:
            if isinstance(character.container,src.rooms.Room):
                for item in character.container.itemsOnFloor:
                    if not item.type == "CityPlaner":
                        continue
                    if not item.bolted:
                        continue
                    result.append((item.getPosition(),"target"))
        return result

    @staticmethod
    def generateDutyQuest(beUsefull,character,currentRoom, dryRun):
        if not character.getHomeRoomCord():
            return (None,None)

        terrain = character.getTerrain()
        cityPlaner = None
        cityPlaners = []
        for room in terrain.rooms:
            items = room.getItemsByType("CityPlaner",needsBolted=True)
            if items:
                cityPlaners.extend(items)

        if cityPlaners:
            cityPlaner = cityPlaners[0]

        if len(cityPlaners) > 1:
            quest = src.quests.questMap["CleanSpace"](reason="remove duplicate CityPlaner",targetPositionBig=cityPlaner.getBigPosition(),targetPosition=cityPlaner.getPosition(),abortOnfullInventory=False,pickUpBolted=True)
            return ([quest],None)

        # do inventory of scrap fields
        numItemsScrapfield = 0
        for scrapField in terrain.scrapFields:
            numItemsScrapfield += len(terrain.itemsByBigCoordinate.get(scrapField,[]))

        if numItemsScrapfield < 100 and terrain.mana >= 20:
            quests = [src.quests.questMap["GetEpochReward"](rewardType="spawn scrap",reason="ensure enough scrap is available")]

            if numItemsScrapfield < 50 and terrain.mana >= 40:
                quests.append(src.quests.questMap["GetEpochReward"](rewardType="spawn scrap",reason="ensure enough scrap is available"))
            return (quests,None)

        if not cityPlaner:
            quest = src.quests.questMap["PlaceItem"](targetPositionBig=character.getHomeRoomCord(),targetPosition=(4,1,0),itemType="CityPlaner",tryHard=True,boltDown=True,reason="be able to plan city expansion")
            return ([quest],None)

        numEmptyRooms = 0
        for room in terrain.rooms:
            if room.tag:
                continue
            if (len(room.itemsOnFloor) > 13+13+11+11 or room.floorPlan or room.storageSlots or len(room.walkingSpace) > 4 or room.inputSlots or room.buildSites):
                continue
            numEmptyRooms += 1

        numRoomsNeeded = cityPlaner.autoExtensionThreashold-len(cityPlaner.getAvailableRooms())-len(cityPlaner.plannedRooms)+len(cityPlaner.scheduledFloorPlans)-numEmptyRooms
        if numRoomsNeeded > 0:
            quests = []
            targets = []
            counter = 0
            for checkRoom in terrain.rooms:
                if checkRoom.tag == "shelter":
                    continue
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
                    targets.append(newPos)

                    quest = src.quests.questMap["ScheduleRoomBuilding"](roomPosition=newPos,reason="extend to base")
                    quests.append(quest)
                    if len(quests) >= numRoomsNeeded:
                        break
                if len(quests) >= numRoomsNeeded:
                    break
            if quests:
                return (quests,None)

        # assign scheduled floor plans
        if cityPlaner and cityPlaner.getAvailableRooms():
            if cityPlaner.scheduledFloorPlans:
                for room in cityPlaner.getAvailableRooms():
                    quest = src.quests.questMap["AssignFloorPlan"](roomPosition=room.getPosition(),floorPlanType=cityPlaner.scheduledFloorPlans[0],reason="set a scheduled floor plan",)
                    return ([quest],None)

        # ensure there is a general purpose room
        if cityPlaner and not cityPlaner.generalPurposeRooms:
            for room in terrain.rooms:
                if room.tag == "shelter":
                    continue
                if room.getPosition() == (7,0,0):
                    continue
                if room.getPosition() in cityPlaner.specialPurposeRooms:
                    continue
                if room.getPosition() in cityPlaner.generalPurposeRooms:
                    continue
                if (len(room.itemsOnFloor) > 13+13+11+11 or room.floorPlan or room.storageSlots or len(room.walkingSpace) > 4 or room.inputSlots or room.buildSites):
                    continue

                quest = src.quests.questMap["DesignateRoom"](roomPosition=room.getPosition(),roomType="generalPurposeRoom",reason="reserve some room for unforeseen needs")
                return ([quest],None)

        # add storage room if needed
        if cityPlaner and cityPlaner.getAvailableRooms():
            # count empty storage slots
            numFreeStorage = 0
            for room in terrain.rooms:
                for storageSlot in room.storageSlots:
                    if storageSlot[1] is not None:
                        continue
                    items = room.getItemByPosition(storageSlot[0])
                    if items:
                        continue
                    numFreeStorage += 1

            if numFreeStorage < 20:
                quest = src.quests.questMap["AssignFloorPlan"](roomPosition=cityPlaner.getAvailableRooms()[0].getPosition(),floorPlanType="storage",reason="increase storage")
                return ([quest],None)

        if cityPlaner and not cityPlaner.generalPurposeRooms:
            for room in terrain.rooms:
                if room.tag == "shelter":
                    continue
                if room.getPosition() == (7,0,0):
                    continue
                if room.getPosition() in cityPlaner.specialPurposeRooms:
                    continue
                if room.getPosition() in cityPlaner.generalPurposeRooms:
                    continue
                if (len(room.itemsOnFloor) > 13+13+11+11 or room.floorPlan or room.storageSlots or len(room.walkingSpace) > 4 or room.inputSlots or room.buildSites):
                    continue

                quest = src.quests.questMap["DesignateRoom"](roomPosition=room.getPosition(),roomType="generalPurposeRoom",reason="reserve some room for unforeseen needs")
                return ([quest],None)

        foundEnemies = False
        for checkCharacter in terrain.characters:
            if checkCharacter.faction == character.faction:
                continue
            foundEnemies = True

        if not foundEnemies:
            hasTemple = False
            for room in terrain.rooms:
                if room.tag != "temple":
                    continue
                hasTemple = True

            if not hasTemple:
                for room in cityPlaner.getAvailableRooms():
                    quest = src.quests.questMap["AssignFloorPlan"](roomPosition=room.getPosition(),floorPlanType="temple",reason="have a temple to place glass hearts")
                    return ([quest],None)

        """
        #set special purpose room
        foundMeetingHall = False
        for room in terrain.rooms:
            if room.tag == "meetingHall":
                foundMeetingHall = True

        if cityPlaner and cityPlaner.getAvailableRooms():
            if not foundMeetingHall:
                for room in cityPlaner.getAvailableRooms():
                    quest = src.quests.questMap["DesignateRoom"](roomPosition=room.getPosition(),roomType="specialPurposeRoom",roomTag="meetingHall",reason="have a place where idle NPCs meet")
                    self.addQuest(quest)
                    return True
        """

        # assign basic floor plans
        if cityPlaner and cityPlaner.getAvailableRooms():
            floorPlansToSet = ["gooProcessing","manufacturingHall","weaponProduction","smokingRoom","wallProduction","scrapCompactor","caseProduction","basicRoombuildingItemsProduction","basicMaterialsProduction"]
            for room in terrain.rooms:
                if room.tag in floorPlansToSet:
                    floorPlansToSet.remove(room.tag)
            if floorPlansToSet:
                for room in cityPlaner.getAvailableRooms():
                    quest = src.quests.questMap["AssignFloorPlan"](roomPosition=room.getPosition(),floorPlanType=random.choice(floorPlansToSet),reason="start the process of making the room useful")
                    return ([quest],None)
                return (None,None)
            return (None,None)
        return (None,None)

src.quests.addType(AssignFloorPlan)

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

        if self.subQuests:
            return (None,None)

        if character.macroState["submenue"] and isinstance(character.macroState["submenue"],src.menuFolder.MapMenu.MapMenu) and not ignoreCommands:
            submenue = character.macroState["submenue"]
            command = ""
            if submenue.cursor[0] > self.roomPosition[0]:
                command += "a"*(submenue.cursor[0]-self.roomPosition[0])
            if submenue.cursor[0] < self.roomPosition[0]:
                command += "d"*(self.roomPosition[0]-submenue.cursor[0])
            if submenue.cursor[1] > self.roomPosition[1]:
                command += "w"*(submenue.cursor[1]-self.roomPosition[1])
            if submenue.cursor[1] < self.roomPosition[1]:
                command += "s"*(self.roomPosition[1]-submenue.cursor[1])

            cityPlaner = character.container.getItemsByType("CityPlaner")[0]
            if self.roomPosition in cityPlaner.plannedRooms:
                command += "x"
                return (None,(command,"remove old construction site marker"))

            if self.roomPosition not in cityPlaner.getAvailableRoomPositions():
                if not dryRun:
                    self.fail("room already registered")
                return (None,None)

            command += "f"
            return (None,(command,"set a floor plan"))

        if character.macroState["submenue"] and isinstance(character.macroState["submenue"],src.menuFolder.SelectionMenu.SelectionMenu) and not ignoreCommands:
            submenue = character.macroState["submenue"]
            if submenue.tag == "floorplanSelection":
                counter = 1
                for option in submenue.options.items():
                    if option[1] == self.floorPlanType:
                        break
                    counter += 1

                command = ""
                if submenue.selectionIndex > counter:
                    command += "w"*(submenue.selectionIndex-counter)
                if submenue.selectionIndex < counter:
                    command += "s"*(counter-submenue.selectionIndex)
                command += "j"
                return (None,(command,"select the floor plan"))

            submenue = character.macroState["submenue"]
            rewardIndex = 0
            if rewardIndex == 0:
                counter = 1
                for option in submenue.options.items():
                    if option[1] == "showMap":
                        break
                    counter += 1
                rewardIndex = counter

            offset = rewardIndex-submenue.selectionIndex
            command = ""
            if offset > 0:
                command += "s"*offset
            else:
                command += "w"*(-offset)
            command += "j"
            return (None,(command,"show the map"))

        if character.macroState["submenue"] and not ignoreCommands:
            return (None,(["esc"],"exit submenu"))

        pos = character.getBigPosition()

        if pos != (7, 7, 0):
            quest = src.quests.questMap["GoHome"](description="go to command centre")
            return ([quest],None)

        if not character.container.isRoom:
            return (None,None)

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
            return (None,("J"+command,"activate the CityPlaner"))

        quest = src.quests.questMap["GoToPosition"](targetPosition=cityPlaner.getPosition(), description="go to CityPlaner",ignoreEndBlocked=True)
        return ([quest],None)

    """
    never complete
    """
    def triggerCompletionCheck(self,character=None):
        if not character:
            return None

        terrain = character.getTerrain()
        room = terrain.getRoomByPosition(self.roomPosition)[0]

        if room.floorPlan:
            self.postHandler()
            return True
        return None

    def getSolvingCommandString(self, character, dryRun=True):
        nextStep = self.getNextStep(character)
        if nextStep == (None,None):
            return super().getSolvingCommandString(character)
        return self.getNextStep(character)[1]


    def handleAssignFloorPlan(self,extraParams):
        self.triggerCompletionCheck(extraParams["character"])

    def getQuestMarkersTile(self,character):
        result = super().getQuestMarkersTile(character)
        result.append(((self.roomPosition[0],self.roomPosition[1]),"target"))
        return result

    def assignToCharacter(self, character):
        if self.character:
            return None

        self.startWatching(character,self.handleAssignFloorPlan, "assigned floor plan")

        return super().assignToCharacter(character)
    @staticmethod
    def generateDutyQuest(beUsefull,character,currentRoom, dryRun):
        terrain = character.getTerrain()
        cityCore = terrain.getRoomByPosition((7,7,0))[0]
        cityPlaner = cityCore.getItemByType("CityPlaner",needsBolted=True)

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
            quest = src.quests.questMap["PlaceItem"](targetPositionBig=(7,7,0),targetPosition=(4,1,0),itemType="CityPlaner",tryHard=True,boltDown=True,reason="be able to plan city expansion")
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

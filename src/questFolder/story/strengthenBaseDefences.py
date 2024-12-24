import src
import random

class StrengthenBaseDefences(src.quests.MetaQuestSequence):
    type = "StrengthenBaseDefences"

    def __init__(self, description="strengthen base defences", creator=None, lifetime=None, numTrapRoomsBuild=None, numTrapRoomsPlanned=None):
        questList = []
        super().__init__(questList, creator=creator,lifetime=lifetime)
        self.metaDescription = description
        self.numTrapRoomsBuild = numTrapRoomsBuild
        self.numTrapRoomsPlanned = numTrapRoomsPlanned

    def getNextStep(self,character=None,ignoreCommands=False, dryRun = True):
        if self.subQuests:
            return (None,None)

        if not character:
            return (None,None)

        terrain = character.getTerrain()

        edgeTrapRooms = []
        for room in character.getTerrain().rooms:
            if not room.tag == "traproom":
                continue

            offsets = [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0)]
            roomPos = room.getPosition()
            for offset in offsets:
                offsetedPosition = (roomPos[0]+offset[0],roomPos[1]+offset[1],roomPos[2]+offset[2])
                if terrain.getRoomByPosition(offsetedPosition):
                    continue
                if offset == (1,0,0):
                    if not room.getPositionWalkable((12,6,0)):
                        continue
                if offset == (-1,0,0):
                    if not room.getPositionWalkable((0,6,0)):
                        continue
                if offset == (0,1,0):
                    if not room.getPositionWalkable((6,12,0)):
                        continue
                if offset == (0,-1,0):
                    if not room.getPositionWalkable((6,0,0)):
                        continue

                edgeTrapRooms.append(room)
                break

        if len(edgeTrapRooms) != 1:
            1/0

        cityPlaner = None
        for room in terrain.rooms:
            for item in room.getItemsByType("CityPlaner",needsBolted=True):
                cityPlaner = item

        print(edgeTrapRooms)
        print(cityPlaner.plannedRooms)

        offsets = [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0)]
        roomPos = edgeTrapRooms[0].getPosition()
        plannedTraproomPositions = []
        candidateTraproomPositions = []
        for offset in offsets:
            offsetedPosition = (roomPos[0]+offset[0],roomPos[1]+offset[1],roomPos[2]+offset[2])
            if offsetedPosition in cityPlaner.plannedRooms:
                plannedTraproomPositions.append(offsetedPosition)
            if not terrain.getRoomByPosition(offsetedPosition) and offsetedPosition not in terrain.forests and offsetedPosition not in terrain.scrapFields:
                candidateTraproomPositions.append(offsetedPosition)

        print(plannedTraproomPositions)
        print("candidateTraproomPositions")
        print(candidateTraproomPositions)

        if plannedTraproomPositions:
            quest = src.quests.questMap["BuildRoom"](targetPosition=random.choice(plannedTraproomPositions),tryHard=True)
            return ([quest],None)
        else:
            offsetedPosition = (roomPos[0]+offset[0],roomPos[1]+offset[1],roomPos[2]+offset[2])
            quest = src.quests.questMap["ScheduleRoomBuilding"](roomPosition=random.choice(candidateTraproomPositions),priorityBuild=True)
            return ([quest],None)

    def generateTextDescription(self):
        text = ["""
Strengthen the base defences
"""]
        if self.lifetimeEvent:
            text.append(f"""\nlifetime: {self.lifetimeEvent.tick - src.gamestate.gamestate.tick} / {self.lifetime}\n""")
        return text

    def assignToCharacter(self, character):
        if self.character:
            return

        super().assignToCharacter(character)

    def wrapedTriggerCompletionCheck(self, extraInfo):
        if self.completed:
            1/0
        if not self.active:
            return

        self.triggerCompletionCheck(extraInfo[0])

    def triggerCompletionCheck(self,character=None):
        if not character:
            return False

        numTrapRooms = 0
        for room in character.getTerrain().rooms:
            if room.tag == "traproom":
                numTrapRooms += 1

        if numTrapRooms < self.numTrapRoomsBuild:
            return False

        self.postHandler()
        return True

src.quests.addType(StrengthenBaseDefences)

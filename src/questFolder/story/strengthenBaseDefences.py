import src
import random

class StrengthenBaseDefences(src.quests.MetaQuestSequence):
    '''
    quest to build up the base defences
    '''
    type = "StrengthenBaseDefences"
    def __init__(self, description="strengthen base defences", creator=None, lifetime=None, numTrapRoomsBuild=None, numTrapRoomsPlanned=None):
        questList = []
        super().__init__(questList, creator=creator,lifetime=lifetime)
        self.metaDescription = description
        self.numTrapRoomsBuild = numTrapRoomsBuild
        self.numTrapRoomsPlanned = numTrapRoomsPlanned

    def getNextStep(self,character=None,ignoreCommands=False, dryRun = True):
        '''
        generate the next step to solve this quest
        currently works by adding 
        '''

        # do nothing if there are subquests
        if self.subQuests:
            return (None,None)

        # do nothing on weird states
        if not character:
            return (None,None)

        # prepare common used variables
        terrain = character.getTerrain()

        # find edge rooms that are accessible from the outside 
        edgeTrapRooms = []
        for room in terrain.rooms:

            # filter room types
            if not room.tag in ("traproom","entryRoom",):
                continue

            # check for outside connectivity 
            offsets = [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0)]
            roomPos = room.getPosition()
            for offset in offsets:

                # check connectivity to neighbours
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

                # accept room as accessible from the outside
                edgeTrapRooms.append(room)
                break

        # handle a base without an outside trap room
        if len(edgeTrapRooms) != 1:
            1/0 #FIXME: ;-)

        # search for buildsides for the trap room
        cityPlaner = None
        for room in terrain.rooms:
            for item in room.getItemsByType("CityPlaner",needsBolted=True):
                cityPlaner = item
        offsets = [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0)]
        roomPos = edgeTrapRooms[0].getPosition()
        plannedTraproomPositions = []
        candidateTraproomPositions = []
        obsoleteRoomMarkers = []
        for offset in offsets:
            offsetedPosition = (roomPos[0]+offset[0],roomPos[1]+offset[1],roomPos[2]+offset[2])
            if offsetedPosition in cityPlaner.plannedRooms:
                if not terrain.getRoomByPosition(offsetedPosition):
                    plannedTraproomPositions.append(offsetedPosition)
                else:
                    obsoleteRoomMarkers.append(offsetedPosition)
            if not terrain.getRoomByPosition(offsetedPosition) and offsetedPosition not in terrain.forests and offsetedPosition not in terrain.scrapFields:
                candidateTraproomPositions.append(offsetedPosition)

        # remove obsolete room markers
        if obsoleteRoomMarkers:
            quest = src.quests.questMap["UnScheduleRoomBuilding"](roomPosition=random.choice(obsoleteRoomMarkers))
            return ([quest],None)

        # add subquest to built a rooom already scheduled
        if plannedTraproomPositions:
            quest = src.quests.questMap["BuildRoom"](targetPosition=random.choice(plannedTraproomPositions),tryHard=True)
            return ([quest],None)

        # add subquest to schedule building a rooom
        offsetedPosition = (roomPos[0]+offset[0],roomPos[1]+offset[1],roomPos[2]+offset[2])
        quest = src.quests.questMap["ScheduleRoomBuilding"](roomPosition=random.choice(candidateTraproomPositions),priorityBuild=True)
        return ([quest],None)

    def generateTextDescription(self):
        '''
        generate a text description
        '''
        text = ["""
Strengthen the base defences
"""]
        if self.lifetimeEvent:
            text.append(f"""\nlifetime: {self.lifetimeEvent.tick - src.gamestate.gamestate.tick} / {self.lifetime}\n""")
        return text

    def assignToCharacter(self, character):
        '''
        handle assignment to character
        '''

        # abort if the quest is already assigned to a character
        if self.character:
            return

        super().assignToCharacter(character)

    def wrapedTriggerCompletionCheck(self, extraInfo):
        '''
        calls triggerCompletionCheck with converted parameters
        '''
        
        #abort on weird states
        if self.completed:
            1/0
        if not self.active:
            return

        # call the function
        self.triggerCompletionCheck(extraInfo[0])

    def triggerCompletionCheck(self,character=None):
        '''
        checks if the quest is completed
        '''

        # abort on weird state
        if not character:
            return False

        # count traprooms
        numTrapRooms = 0
        for room in character.getTerrain().rooms:
            if room.tag == "traproom":
                numTrapRooms += 1

        # continue working if neccessary threashold is not met
        if numTrapRooms < self.numTrapRoomsBuild:
            return False

        # end the quest
        self.postHandler()
        return True

# register quest
src.quests.addType(StrengthenBaseDefences)

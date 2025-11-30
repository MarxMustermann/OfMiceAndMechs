import random

import src


class ClearPathToTile(src.quests.MetaQuestSequence):
    type = "ClearPathToTile"
    lowLevel = True

    def __init__(self, description="clear path to tile", creator=None, targetPositionBig=None, tryHard=False,reason=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description+f" {targetPositionBig}"
        self.targetPositionBig = targetPositionBig
        self.tryHard = tryHard
        self.reason = reason
        self.path = None

    def generateTextDescription(self):
        reason = ""
        if self.reason:
            reason = f",\nto {self.reason}"
        text = f"""
Clear path to tile {self.targetPositionBig}{reason}.

Open doors and break walls that are in the way.
"""

        return text

    def _expand_good_from(self,startPos,tile_map):
        """
        calulate a path to clear
        """

        # mark position as processed
        tile_map["visited"].append(startPos)
        path = tile_map["map"][startPos]

        # get room
        room = None
        rooms = self.character.getTerrain().getRoomByPosition(startPos)
        if rooms:
            room = rooms[0]

        # process neighbors
        offsets = [(0,1,0),(0,-1,0),(1,0,0),(-1,0,0)]
        random.shuffle(offsets)
        for offset in offsets:
            
            # get neighbor
            check_position = (startPos[0]+offset[0],startPos[1]+offset[1],0)
            if check_position[0] < 1 or check_position[0] > 12 or check_position[1] < 1 or check_position[1] > 12:
                continue
            rooms = self.character.getTerrain().getRoomByPosition(check_position)
            if rooms:
                neighbour = rooms[0]
            else:
                neighbour = None

            # skip known
            if check_position in tile_map["visited"] or check_position in tile_map["good"]:
                continue

            # check connectivity
            connected = True
            can_be_connected = True
            if room:
                if offset == (0,1,0):
                    door_position = (6,12,0)
                if offset == (0,-1,0):
                    door_position = (6,0,0)
                if offset == (1,0,0):
                    door_position = (12,6,0)
                if offset == (-1,0,0):
                    door_position = (0,6,0)

                for item in room.getItemByPosition(door_position):
                    if item.walkable:
                        continue
                    connected = False
                    if not item.type == "Door":
                        can_be_connected = False

            if neighbour:
                if offset == (0,1,0):
                    door_position = (6,0,0)
                if offset == (0,-1,0):
                    door_position = (6,12,0)
                if offset == (1,0,0):
                    door_position = (0,6,0)
                if offset == (-1,0,0):
                    door_position = (12,6,0)
                for item in neighbour.getItemByPosition(door_position):
                    if item.walkable:
                        continue
                    can_be_connected = False
                    connected = False
            
            # sort position by connectivity
            if can_be_connected:
                if connected:
                    tile_map["good"].append(check_position)
                    tile_map["map"][check_position] = path
                    if neighbour in tile_map["bad"]:
                        tile_map["bad"].remove(check_position)
                else:
                    tile_map["bad"].append(check_position)
                    tile_map["map"][check_position] = path[:]+[("unblock door",startPos,door_position)]

    def _expand_good(self,tile_map):
        while tile_map.get("good"):
            position = tile_map["good"].pop()
            self._expand_good_from(position,tile_map)

    def _expand_bad(self,tile_map):
        random.shuffle(tile_map.get("bad"))
        for position in tile_map.get("bad")[:]:
            tile_map["good"].append(position)
            tile_map["bad"].remove(position)

    def _expand(self,tile_map):
        self._expand_good(tile_map)
        self._expand_bad(tile_map)

    def _generatePath(self,startPos,endPos):
        tile_map = {"good":[startPos],"bad":[],"visited":[],"map":{startPos:[]}}
        while tile_map["good"] or tile_map["bad"]:
            self._expand(tile_map)
        return tile_map["map"][endPos]

    def triggerCompletionCheck(self,character=None,dryRun=True):
        if not character:
            return None

        pos = character.getBigPosition()
        pos = (pos[0]%15,pos[1]%15,pos[2]%15)
        if pos[0] == self.targetPositionBig[0] and pos[1] == self.targetPositionBig[1]:
            if not dryRun:
                self.postHandler()
            return True
        return False

    def getNextStep(self,character=None,ignoreCommands=False, dryRun = True):
        if self.subQuests:
            return (None,None)

        self.path = None

        path = self.path

        if not path:
            path = self._generatePath(character.getBigPosition(),self.targetPositionBig)

            if not dryRun:
                self.path = path

        if not path:
            quest = src.quests.questMap["GoToTile"](targetPosition=self.targetPositionBig)
            return ([quest],None)

        path = path[:]
        step = path.pop(0) 
        if not dryRun:
            self.path = path

        if not (character.getBigPosition() == step[1]):
            quest = src.quests.questMap["GoToTile"](targetPosition=step[1])
            return ([quest],None)
        quest = src.quests.questMap["UnblockDoor"](targetPositionBig=step[1],targetPosition=step[2])
        return ([quest],None)
        
    def handleChangedTile(self, extraInfo = None):
        if not self.active:
            return
        if not self.character:
            return
        if self.completed:
            1/0

        self.triggerCompletionCheck(character=self.character,dryRun=False)

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.handleChangedTile, "changedTile")

        super().assignToCharacter(character)

src.quests.addType(ClearPathToTile)

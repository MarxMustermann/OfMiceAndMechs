import src

class BuildRoom(src.quests.MetaQuestSequence):
    type = "BuildRoom"

    def __init__(self, description="build room", creator=None, command=None, lifetime=None, targetPosition=None,tryHard=False):
        questList = []
        super().__init__(questList, creator=creator, lifetime=lifetime)
        self.metaDescription = description
        self.shortCode = "M"
        self.targetPosition = targetPosition
        self.tryHard = tryHard

    def unhandledSubQuestFail(self,extraParam):
        self.fail(extraParam["reason"])

    def generateTextDescription(self):
        out = """
Build a room on the tile %s.

Rooms are build using the RoomBuilder (RB).
The RoomBuilder needs to be placed in the middle of a tile.
Walls and doors have to be placed in a room shaped pattern around that.
When all of that is done, the Roombuilder can be activated to build a room.
"""%(self.targetPosition,)

        if self.tryHard:
            out += """
Try as hard as you can to achieve this.
If something is missing, produce it.
If something disturbs you, destroy it.
"""

        if not self.subQuests:
            out += """
This quest has no subquests. Press r to generate subquests for this quest.
The subquests will guide you, but you don't have to follow them as long as the is getting extended."""
        else:
            out += """
Follow this quests sub quests. They will guide you and try to explain how to build a base.
Press d to move the cursor and show the subquests description.
"""

        out += """
Press a to move back to the main quest.
"""
        return out

    def solver(self, character):
        (nextQuests,nextCommand) = self.getNextStep(character)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
            return

        if nextCommand:
            character.runCommandString(nextCommand)
            return
        super().solver(character)

    def getSolvingCommandString(self, character, dryRun=True):
        return self.getNextStep(character)[1]

    def generateSubquests(self, character=None):
        (nextQuests,nextCommand) = self.getNextStep(character,ignoreCommands=True)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
            return

    def getNextStep(self,character=None,ignoreCommands=False):
        if not self.subQuests:
            items = character.getTerrain().getItemByPosition((15*self.targetPosition[0]+7,15*self.targetPosition[1]+7,0))
            if not items or not items[-1].type == "RoomBuilder":
                quest = src.quests.questMap["PlaceItem"](targetPosition=(7,7,0),targetPositionBig=self.targetPosition,itemType="RoomBuilder")
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
                if items:
                    continue
                missingWallPositions.append(wallPos)

            if missingWallPositions:
                if not character.inventory or not character.inventory[-1].type == "Wall":
                    amount = None
                    if len(missingWallPositions) < 10:
                        amount = len(missingWallPositions)
                    quest = src.quests.questMap["FetchItems"](toCollect="Wall",takeAnyUnbolted=True,tryHard=self.tryHard,amount=amount)
                    return ([quest],None)

                quests = []

                counter = 0
                for missingWallPos in missingWallPositions:
                    if not (len(character.inventory) > counter and character.inventory[-1-counter].type == "Wall"):
                        break
                    quest = src.quests.questMap["PlaceItem"](targetPosition=missingWallPos,targetPositionBig=self.targetPosition,itemType="Wall",tryHard=self.tryHard)
                    quests.append(quest)
                    counter += 1
                return (list(reversed(quests)),None)
            
            doorPositions = [(7,1,0),(1,7,0),(7,13,0),(13,7,0)]
            missingDoorPos = False
            for doorPos in doorPositions:
                items = character.getTerrain().getItemByPosition((15*self.targetPosition[0]+doorPos[0],15*self.targetPosition[1]+doorPos[1],0))
                if items:
                    continue
                missingDoorPos = doorPos
                break 

            if missingDoorPos:
                if not character.inventory or not character.inventory[-1].type == "Door":
                    foundRoom = None
                    for room in character.getTerrain().rooms:
                        for item in room.itemsOnFloor:
                            if item.bolted == False and item.type == "Door":
                                foundRoom = room
                                break
                        if foundRoom:
                            break

                    if not foundRoom:
                        self.fail("no doors found")
                        return (None,None)

                    if not character.getBigPosition() == room.getPosition():
                        quest = src.quests.questMap["GoToTile"](targetPosition=room.getPosition())
                        return ([quest],None)

                    quest = src.quests.questMap["FetchItems"](toCollect="Door",takeAnyUnbolted=True,amount=4)
                    return ([quest],None)

                if not character.getBigPosition() == self.targetPosition:
                    quest = src.quests.questMap["GoToTile"](targetPosition=self.targetPosition)
                    return ([quest],None)

                if not character.getSpacePosition() == missingDoorPos:
                    quest = src.quests.questMap["GoToPosition"](targetPosition=missingDoorPos)
                    return ([quest],None)

                return (None,"l")
            
            roomBuilderPos = (7,7,0)
            if character.getDistance((15*self.targetPosition[0]+7,15*self.targetPosition[1]+7,0)) > 1:
                quest = src.quests.questMap["GoToPosition"](targetPosition=roomBuilderPos,ignoreEndBlocked=True)
                return ([quest], None)

            offsets = {(0,0,0):"j",(1,0,0):"Jd",(-1,0,0):"Ja",(0,1,0):"Js",(0,-1,0):"Jw"}
            for (offset,command) in offsets.items():
                if character.getPosition(offset=offset) == (15*self.targetPosition[0]+7,15*self.targetPosition[1]+7,0):
                    return (None, command)
            1/0
        return (None,None)
    
    def generateSubquests(self, character=None):
        (nextQuests,nextCommand) = self.getNextStep(character,ignoreCommands=True)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
            return

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

src.quests.addType(BuildRoom)

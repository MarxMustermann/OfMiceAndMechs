import src
import random

class RestockRoom(src.quests.MetaQuestSequence):
    type = "RestockRoom"

    def __init__(self, description="restock room", creator=None, targetPosition=None,toRestock=None,allowAny=False,reason=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        if targetPosition:
            self.metaDescription += " %s"%(targetPosition,)
        self.toRestock = None
        self.allowAny = allowAny
        self.reason = reason

        self.targetPosition = None
        if targetPosition:
            self.setParameters({"targetPosition":targetPosition})
        if toRestock:
            self.setParameters({"toRestock":toRestock})
        if allowAny:
            self.setParameters({"allowAny":allowAny})
        self.type = "RestockRoom"

        self.shortCode = "r"

    def generateTextDescription(self):
        reason = ""
        if self.reason:
            reason = ",\nto %s"%(self.reason,)
        return """
Restock the room with items from your inventory%s.

Place the items in the correct input or storage stockpile.

%s"""%(reason,self.targetPosition,)

    def setParameters(self,parameters):
        if "targetPosition" in parameters and "targetPosition" in parameters:
            self.targetPosition = parameters["targetPosition"]
        if "toRestock" in parameters and "toRestock" in parameters:
            self.toRestock = parameters["toRestock"]
        if "allowAny" in parameters and "allowAny" in parameters:
            self.allowAny = parameters["allowAny"]
        return super().setParameters(parameters)

    def triggerCompletionCheck(self,character=None):
        if not character:
            return

        if self.targetPosition and not character.getBigPosition() == self.targetPosition:
            return

        if isinstance(character.container,src.rooms.Room):
            room = character.container

            foundNeighbour = None
            inputSlots = room.getEmptyInputslots(itemType=self.toRestock,allowAny=self.allowAny)
            if not inputSlots:
                self.postHandler()
                return

            for slot in inputSlots:
                for direction in ((-1,0),(1,0),(0,-1),(0,1)):
                    if len(slot[0]) < 3:
                        slot = ((slot[0][0],slot[0][1],0),slot[1],slot[2])
                    neighbour = (slot[0][0]-direction[0],slot[0][1]-direction[1],slot[0][2])
                    if not neighbour in room.walkingSpace:
                        continue
                    foundNeighbour = (neighbour,direction)
                    break
                if not foundNeighbour:
                    for direction in ((-1,0),(1,0),(0,-1),(0,1)):
                        neighbour = (slot[0][0]-direction[0],slot[0][1]-direction[1],slot[0][2])
                        if not room.getPositionWalkable(neighbour):
                            continue
                        foundNeighbour = (neighbour,direction)

            if not foundNeighbour:
                character.addMessage("no neighbour")
                self.postHandler()
                return True

        if not self.getNumDrops(character):
            self.postHandler()
            return True
        return

    def getNumDrops(self,character):
        numDrops = 0
        for item in reversed(character.inventory):
            if not item.type == self.toRestock:
                break
            numDrops += 1
        return numDrops

    def droppedItem(self, extraInfo):
        self.triggerCompletionCheck(self.character)

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.droppedItem, "dropped")

        super().assignToCharacter(character)

    def getRequiredParameters(self):
        parameters = super().getRequiredParameters()
        parameters.append({"name":"targetPosition","type":"coordinate"})
        return parameters

    def getNextStep(self,character=None,ignoreCommands=False):
        if self.subQuests:
            return (None,None)

        if self.targetPosition and not character.getBigPosition() == self.targetPosition:
            quest = src.quests.questMap["GoToTile"](targetPosition=self.targetPosition)
            return ([quest],None)

        if isinstance(character.container,src.rooms.Room):
            room = character.container

            if not hasattr(room,"inputSlots"):
                self.fail(reason="no input slot attribute")
                return (None,None)

            inputSlots = room.getEmptyInputslots(itemType=self.toRestock,allowAny=self.allowAny)
            random.shuffle(inputSlots)

            # find neighboured input fields
            foundDirectDrop = None
            for direction in ((-1,0),(1,0),(0,-1),(0,1),(0,0)):
                neighbour = (character.xPosition+direction[0],character.yPosition+direction[1],character.zPosition)
                for inputSlot in inputSlots:
                    if neighbour[0] == inputSlot[0][0] and neighbour[1] == inputSlot[0][1]:
                        foundDirectDrop = (neighbour,direction,inputSlot)
                        break

            if character.inventory and foundDirectDrop:
                dropContent = room.getItemByPosition(foundDirectDrop[0])
                if not dropContent or not dropContent[0].type == "Scrap":
                    maxSpace = foundDirectDrop[2][2].get("maxAmount")
                    if not maxSpace:
                        maxSpace = 25
                    if not dropContent:
                        spaceTaken = 0
                    else:
                        spaceTaken = len(dropContent)
                    numToDrop = min(maxSpace-spaceTaken,self.getNumDrops(character))
                    if not character.inventory[-1].walkable:
                        numToDrop = 1

                    if foundDirectDrop[1] == (-1,0):
                        return (None,("La"*numToDrop,"store an item"))
                    if foundDirectDrop[1] == (1,0):
                        return (None,("Ld"*numToDrop,"store an item"))
                    if foundDirectDrop[1] == (0,-1):
                        return (None,("Lw"*numToDrop,"store an item"))
                    if foundDirectDrop[1] == (0,1):
                        return (None,("Ls"*numToDrop,"store an item"))
                    if foundDirectDrop[1] == (0,0):
                        return (None,("l"*numToDrop,"store an item"))
                else:
                    if foundDirectDrop[1] == (-1,0):
                        return (None,("Ja"*10,"put scrap on scrap pile"))
                    if foundDirectDrop[1] == (1,0):
                        return (None,("Jd"*10,"put scrap on scrap pile"))
                    if foundDirectDrop[1] == (0,-1):
                        return (None,("Jw"*10,"put scrap on scrap pile"))
                    if foundDirectDrop[1] == (0,1):
                        return (None,("Js"*10,"put scrap on scrap pile"))
                    if foundDirectDrop[1] == (0,0):
                        return (None,("j"*self.getNumDrops(character),"put scrap on scrap pile"))

            foundNeighbour = None
            for slot in inputSlots:
                if len(slot[0]) < 3:
                    slot = ((slot[0][0],slot[0][1],0),slot[1],slot[2])
                for direction in ((-1,0),(1,0),(0,-1),(0,1)):
                    neighbour = (slot[0][0]-direction[0],slot[0][1]-direction[1],slot[0][2])
                    if not neighbour in room.walkingSpace:
                        continue
                    if not room.getPositionWalkable(neighbour):
                        continue
                    foundNeighbour = (neighbour,direction)
                    break
                if foundNeighbour:
                    break

            if not foundNeighbour:
                for slot in inputSlots:
                    if len(slot[0]) < 3:
                        slot = ((slot[0][0],slot[0][1],0),slot[1],slot[2])
                    for direction in ((-1,0),(1,0),(0,-1),(0,1)):
                        neighbour = (slot[0][0]-direction[0],slot[0][1]-direction[1],slot[0][2])
                        foundNeighbour = (neighbour,direction)
                        if not room.getPositionWalkable(neighbour):
                            continue
                        break
                    if foundNeighbour:
                        break

            if not foundNeighbour:
                self.fail(reason="neighbour not found")
                return (None,None)

            quest = src.quests.questMap["GoToPosition"](reason="get to the stockpile")
            quest.setParameters({"targetPosition":foundNeighbour[0]})
            return ([quest],None)

        charPos = (character.xPosition%15,character.yPosition%15,character.zPosition%15)
        if charPos == (7,0,0):
            return (None,("s","enter tile"))
        if charPos == (7,14,0):
            return (None,("w","enter tile"))
        if charPos == (0,7,0):
            return (None,("d","enter tile"))
        if charPos == (14,7,0):
            return (None,("a","enter tile"))

        self.fail()
        return (None,None)

    def solver(self, character):
        if self.triggerCompletionCheck(character):
            return

        (nextQuests,nextCommand) = self.getNextStep(character)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
            return

        if nextCommand:
            character.runCommandString(nextCommand[0])
            return
        super().solver(character)

    def getSolvingCommandString(self, character, dryRun=True):
        nextStep = self.getNextStep(character)
        if nextStep == (None,None):
            return super().getSolvingCommandString(character)
        return self.getNextStep(character)[1]

    def getQuestMarkersTile(self,character):
        result = super().getQuestMarkersTile(character)
        if self.targetPosition:
            result.append(((self.targetPosition[0],self.targetPosition[1]),"target"))
        return result

src.quests.addType(RestockRoom)

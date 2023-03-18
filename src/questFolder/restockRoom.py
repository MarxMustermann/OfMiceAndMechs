import src
import random

class RestockRoom(src.quests.MetaQuestSequence):
    type = "RestockRoom"

    def __init__(self, description="restock room", creator=None, targetPosition=None,toRestock=None,allowAny=False):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        self.toRestock = None
        self.allowAny = allowAny

        if targetPosition:
            self.setParameters({"targetPosition":targetPosition})
        if toRestock:
            self.setParameters({"toRestock":toRestock})
        if allowAny:
            self.setParameters({"allowAny":allowAny})
        self.type = "RestockRoom"

        self.shortCode = "r"

    def generateTextDescription(self):
        return """
Restock the room with items from your inventory.
Place the items in the correct input stockpile."""

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

        if isinstance(character.container,src.rooms.Room):
            room = character.container

            foundNeighbour = None
            inputSlots = room.getEmptyInputslots(itemType=self.toRestock,allowAny=self.allowAny)
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
                return

        if not self.getNumDrops(character):
            self.postHandler()
            return
        return

    def getNumDrops(self,character):
        numDrops = 0
        for item in reversed(character.inventory):
            if not item.type == self.toRestock:
                break
            numDrops += 1
        return numDrops

    def getRequiredParameters(self):
        parameters = super().getRequiredParameters()
        parameters.append({"name":"targetPosition","type":"coordinate"})
        return parameters

    def getSolvingCommandString(self,character,dryRun=True):
        if self.subQuests:
            return super().getSolvingCommandString(character,dryRun=dryRun)

        self.triggerCompletionCheck(character)

        if isinstance(character.container,src.rooms.Room):
            room = character.container

            if not hasattr(room,"inputSlots"):
                return "..23.."

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

            if foundDirectDrop:
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

                    if foundDirectDrop[1] == (-1,0):
                        return "La"*numToDrop
                    if foundDirectDrop[1] == (1,0):
                        return "Ld"*numToDrop
                    if foundDirectDrop[1] == (0,-1):
                        return "Lw"*numToDrop
                    if foundDirectDrop[1] == (0,1):
                        return "Ls"*numToDrop
                    if foundDirectDrop[1] == (0,0):
                        return "l"*numToDrop
                else:
                    if foundDirectDrop[1] == (-1,0):
                        return "Ja"*10
                    if foundDirectDrop[1] == (1,0):
                        return "Jd"*10
                    if foundDirectDrop[1] == (0,-1):
                        return "Jw"*10
                    if foundDirectDrop[1] == (0,1):
                        return "Js"*10
                    if foundDirectDrop[1] == (0,0):
                        return "l"*self.getNumDrops(character)

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
                return "..24.."

            if not dryRun:
                quest = src.quests.questMap["GoToPosition"]()
                quest.assignToCharacter(character)
                quest.setParameters({"targetPosition":foundNeighbour[0]})
                quest.activate()
                self.addQuest(quest)

                return "."
            return "................."

        charPos = (character.xPosition%15,character.yPosition%15,character.zPosition%15)
        if charPos == (7,0,0):
            return "s"
        if charPos == (7,14,0):
            return "w"
        if charPos == (0,7,0):
            return "d"
        if charPos == (14,7,0):
            return "a"

    def solver(self, character):
        self.activate()
        self.assignToCharacter(character)
        if self.subQuests:
            return super().solver(character)

        commandString = self.getSolvingCommandString(character,dryRun=False)
        self.reroll()
        if commandString:
            character.runCommandString(commandString)
            return False
        else:
            return True

src.quests.addType(RestockRoom)

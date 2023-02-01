import src
import random

class FetchItems(src.quests.MetaQuestSequence):
    type = "FetchItems"

    def __init__(self, description="fetch items", creator=None, targetPosition=None, toCollect=None, amount=None, returnToTile=True,lifetime=None):
        questList = []
        super().__init__(questList, creator=creator,lifetime=lifetime)
        self.metaDescription = description
        self.amount = None
        self.toCollect = None
        self.returnToTile = True
        self.tileToReturnTo = None
        self.collectedItems = False

        if toCollect:
            self.setParameters({"toCollect":toCollect})
        if amount:
            self.setParameters({"amount":amount})
        if returnToTile:
            self.setParameters({"returnToTile":returnToTile})

        self.attributesToStore.append("toCollect")
        self.attributesToStore.append("amount")
        self.attributesToStore.append("returnToTile")
        self.tuplesToStore.append("tileToReturnTo")

        self.shortCode = "f"

    def generateTextDescription(self):
        if not self.amount:
            text = """
Fetch an inventory full of %ss.

"""%(self.toCollect,)
        else:
            extraS = "s"
            if self.amount == 1:
                extraS = ""
            text = """
Fetch %s %s"""+extraS+""".

"""%(self.toCollect,)

        if self.returnToTile:
            tile = self.tileToReturnTo
            if not tile:
                tile = "this tile"
            text += """
Return to %s after to complete this quest."""%(tile,)
        return text

    def pickedUpItem(self,extraInfo):
        self.triggerCompletionCheck(extraInfo[0])

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.pickedUpItem, "itemPickedUp")
        return super().assignToCharacter(character)

    def setParameters(self,parameters):
        if "toCollect" in parameters and "toCollect" in parameters:
            self.toCollect = parameters["toCollect"]
            self.metaDescription += " "+self.toCollect
        if "amount" in parameters and "amount" in parameters:
            self.amount = parameters["amount"]
        if "returnToTile" in parameters and "returnToTile" in parameters:
            self.returnToTile = parameters["returnToTile"]
        return super().setParameters(parameters)

    def getRequiredParameters(self):
        parameters = super().getRequiredParameters()
        parameters.append({"name":"toCollect","type":"itemType"})
        return parameters

    def triggerCompletionCheck(self,character=None):

        if not character:
            return

        if self.amount:
            numItems = 0
            for item in reversed(character.inventory):
                if not item.type == self.toCollect:
                    break
                numItems += 1

            if numItems >= self.amount:
                self.collectedItems = True
                return

        if character.getFreeInventorySpace() <= 0 and character.inventory[-1].type == self.toCollect:
            self.collectedItems = True

        if self.collectedItems:
            self.postHandler()
            return

        if isinstance(character.container,src.rooms.Room):
            outputSlots = character.container.getNonEmptyOutputslots(itemType=self.toCollect)
            random.shuffle(outputSlots)
            if outputSlots:
                return

            if self.getSource():
                return

            character.addMessage("failed fetching items")
            self.fail()
            self.postHandler()
        return

    def getSource(self):
        if not isinstance(self.character.container,src.rooms.Room):
            return None

        source = None
        for room in self.character.getTerrain().rooms:
            if room.getNonEmptyOutputslots(itemType=self.toCollect):
                return (room.getPosition(),)

    def getSolvingCommandString(self,character,dryRun=True):

        charPos = (character.xPosition%15,character.yPosition%15,character.zPosition%15)

        if self.subQuests:
            return super().getSolvingCommandString(character,dryRun=dryRun)

        if isinstance(character.container,src.rooms.Room):
            room = character.container

            outputSlots = room.getNonEmptyOutputslots(itemType=self.toCollect)

            foundDirectPickup = None
            for direction in ((-1,0),(1,0),(0,-1),(0,1),(0,0)):
                neighbour = (character.xPosition+direction[0],character.yPosition+direction[1],character.zPosition)
                for outputSlot in outputSlots:
                    if neighbour == outputSlot[0]:
                        foundDirectPickup = (neighbour,direction)
                        break

            if foundDirectPickup:
                inventorySpace = 10-len(character.inventory)
                if self.amount:
                    numItems = 0
                    for item in reversed(character.inventory):
                        if not item.type == self.toCollect:
                            break
                        numItems += 1
                    inventorySpace = min(inventorySpace,self.amount-numItems)
                if foundDirectPickup[1] == (-1,0):
                    return "Ka"*inventorySpace
                if foundDirectPickup[1] == (1,0):
                    return "Kd"*inventorySpace
                if foundDirectPickup[1] == (0,-1):
                    return "Kw"*inventorySpace
                if foundDirectPickup[1] == (0,1):
                    return "Ks"*inventorySpace
                if foundDirectPickup[1] == (0,0):
                    return "l"*inventorySpace

            foundNeighbour = None
            for slot in outputSlots:
                for direction in ((-1,0),(1,0),(0,-1),(0,1)):
                    neighbour = (slot[0][0]-direction[0],slot[0][1]-direction[1],slot[0][2])
                    if not neighbour in room.walkingSpace:
                        continue
                    foundNeighbour = (neighbour,direction)
                    break

            if not foundNeighbour:
                return "..24.."

            if not dryRun:
                quest = src.quests.questMap["GoToPosition"](ignoreEnd=True)
                quest.assignToCharacter(character)
                quest.setParameters({"targetPosition":foundNeighbour[0]})
                quest.activate()
                self.addQuest(quest)

                return "."
            return str(foundNeighbour)

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

        self.triggerCompletionCheck(character)
        if character.getFreeInventorySpace() <= 0:
            quest = src.quests.questMap["ClearInventory"]()
            quest.activate()
            quest.assignToCharacter(character)
            self.addQuest(quest)
            return

        if self.collectedItems and self.tileToReturnTo:
            charPos = None
            if isinstance(character.container,src.rooms.Room):
                charPos = (character.container.xPosition,character.container.yPosition,0)
            else:
                charPos = (character.xPosition//15,character.yPosition//15,0)
            if not charPos == self.tileToReturnTo:
                self.addQuest(src.quests.questMap["GoToTile"](targetPosition=self.tileToReturnTo))
                self.tileToReturnTo = None
                return

        if not self.collectedItems and isinstance(character.container,src.rooms.Room):
            room = character.container
            outputSlots = room.getNonEmptyOutputslots(itemType=self.toCollect)
            if not outputSlots:
                source = self.getSource()
                if source:
                    self.addQuest(src.quests.questMap["GoToTile"](targetPosition=source[0]))
                    if self.returnToTile:
                        self.tileToReturnTo = (room.xPosition,room.yPosition,0)
                    return
                else:
                    character.runCommandString("11.")
                    return

        commandString = self.getSolvingCommandString(character,dryRun=False)
        self.reroll()
        if commandString:
            character.runCommandString(commandString)
            return False
        else:
            return True

src.quests.addType(FetchItems)

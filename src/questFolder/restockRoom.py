import random

import src


class RestockRoom(src.quests.MetaQuestSequence):
    type = "RestockRoom"

    def __init__(self, description="restock room", creator=None, targetPositionBig=None,toRestock=None,allowAny=False,reason=None,targetPosition=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        if targetPositionBig:
            self.metaDescription += f" {targetPositionBig}"
        self.toRestock = None
        self.allowAny = allowAny
        self.reason = reason

        self.targetPositionBig = None
        if targetPositionBig:
            self.setParameters({"targetPositionBig":targetPositionBig})
        if toRestock:
            self.setParameters({"toRestock":toRestock})
        if allowAny:
            self.setParameters({"allowAny":allowAny})
        self.targetPosition = targetPosition
        self.type = "RestockRoom"

        self.shortCode = "r"

    def generateTextDescription(self):
        reason = ""
        if self.reason:
            reason = f",\nto {self.reason}"
        roomString = "a room"
        if self.targetPositionBig:
            roomString += f"the room on tile {self.targetPositionBig}"
        typeString = "any items"
        if self.toRestock:
            typeString = self.toRestock
        text = f"""
Restock {roomString} with {typeString} from your inventory{reason}.

Place the items in the correct input or storage stockpile.
"""
        if self.targetPosition:
            text += f"""Use the stocpile in position {self.targetPosition}"""

        return text

    def setParameters(self,parameters):
        if "targetPositionBig" in parameters and "targetPositionBig" in parameters:
            self.targetPositionBig = parameters["targetPositionBig"]
        if "toRestock" in parameters and "toRestock" in parameters:
            self.toRestock = parameters["toRestock"]
        if "allowAny" in parameters and "allowAny" in parameters:
            self.allowAny = parameters["allowAny"]
        return super().setParameters(parameters)

    def triggerCompletionCheck(self,character=None):
        if not character:
            return None

        if self.targetPositionBig and character.getBigPosition() != self.targetPositionBig:
            return None

        if isinstance(character.container,src.rooms.Room):
            room = character.container

            foundNeighbour = None
            inputSlots = room.getEmptyInputslots(itemType=self.toRestock,allowAny=self.allowAny)
            if not inputSlots:
                self.postHandler()
                return None

            for slot in inputSlots:
                if self.targetPosition and self.targetPosition != slot[0]:
                    continue
                for direction in ((-1,0),(1,0),(0,-1),(0,1)):
                    if len(slot[0]) < 3:
                        slot = ((slot[0][0],slot[0][1],0),slot[1],slot[2])
                    neighbour = (slot[0][0]-direction[0],slot[0][1]-direction[1],slot[0][2])
                    if neighbour not in room.walkingSpace:
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
        return None

    def getNumDrops(self,character):
        numDrops = 0
        for item in reversed(character.inventory):
            if item.type != self.toRestock:
                continue
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
        parameters.append({"name":"targetPositionBig","type":"coordinate"})
        return parameters

    def getNextStep(self,character=None,ignoreCommands=False,dryRun=True):
        if self.subQuests:
            return (None,None)

        if character.macroState["submenue"] and not ignoreCommands:
            if not isinstance(character.macroState["submenue"],src.menuFolder.inventoryMenu.InventoryMenu):
                return (None,(["esc"],"close the menu"))

        if self.targetPositionBig and character.getBigPosition() != self.targetPositionBig:
            quest = src.quests.questMap["GoToTile"](targetPosition=self.targetPositionBig)
            return ([quest],None)

        if isinstance(character.container,src.rooms.Room):
            room = character.container

            if not hasattr(room,"inputSlots"):
                if not dryRun:
                    self.fail(reason="no input slot attribute")
                return (None,None)

            if not character.inventory:
                return (None,None)

            fullyEmpty = not character.inventory[-1].walkable
            inputSlots = room.getEmptyInputslots(itemType=self.toRestock,allowAny=self.allowAny,allowStorage=False,fullyEmpty=fullyEmpty)
            if not inputSlots:
                inputSlots = room.getEmptyInputslots(itemType=self.toRestock,allowAny=self.allowAny,allowStorage=True,fullyEmpty=fullyEmpty)
            random.shuffle(inputSlots)

            if self.targetPosition:
                newInputs = []
                for slot in inputSlots:
                    if self.targetPosition != slot[0]:
                        continue
                    newInputs.append(slot)
                inputSlots = newInputs

            # find neighbored input fields
            foundDirectDrop = None
            for direction in ((-1,0),(1,0),(0,-1),(0,1),(0,0)):
                neighbour = (character.xPosition+direction[0],character.yPosition+direction[1],character.zPosition)
                for inputSlot in inputSlots:
                    if neighbour[0] == inputSlot[0][0] and neighbour[1] == inputSlot[0][1]:
                        foundDirectDrop = (neighbour,direction,inputSlot)
                        break

            if character.inventory and foundDirectDrop:
                dropContent = room.getItemByPosition(foundDirectDrop[0])
                if not dropContent or dropContent[0].type != "Scrap":
                    maxSpace = foundDirectDrop[2][2].get("maxAmount")
                    if not maxSpace:
                        if (dropContent and dropContent[0].walkable == False) or character.inventory[-1].walkable == False:
                            maxSpace = 1
                        else:
                            maxSpace = 25
                    if not dropContent:
                        spaceTaken = 0
                    else:
                        spaceTaken = len(dropContent)
                    numToDrop = min(maxSpace-spaceTaken,self.getNumDrops(character))
                    if numToDrop > 0:
                        item = character.inventory[-1]
                        counter = -1
                        while item.type != self.toRestock:
                            counter += 1
                            item = character.inventory[counter]

                        if not item.walkable:
                            numToDrop = 1
    
                        inventoryCommand = ""
                        if counter > -1:
                            submenue = character.macroState["submenue"]
                            if not submenue:
                                inventoryCommand += "i"+"s"*counter
                            if isinstance(submenue,src.menuFolder.inventoryMenu.InventoryMenu):
                                if counter > submenue.cursor:
                                    inventoryCommand += "s"*(counter-submenue.cursor)
                                else:
                                    inventoryCommand += "w"*(submenue.cursor-counter)
                            numToDrop = 1

                        numToDrop = 1

                        interactionCommand = "L"
                        if inventoryCommand == "":
                            if "advancedDrop" in character.interactionState:
                                interactionCommand = ""
                            if character.macroState.get("submenue"):
                                print("submenue")
                                print(character.macroState.get("submenue"))
                                print(character.macroState.get("submenue").tag)
                            if character.macroState.get("submenue") and character.macroState.get("submenue").tag == "dropDirection":
                                interactionCommand = ""
                        if foundDirectDrop[1] == (-1,0):
                            return (None,((inventoryCommand+interactionCommand+"a")*numToDrop,"store an item"))
                        if foundDirectDrop[1] == (1,0):
                            return (None,((inventoryCommand+interactionCommand+"d")*numToDrop,"store an item"))
                        if foundDirectDrop[1] == (0,-1):
                            return (None,((inventoryCommand+interactionCommand+"w")*numToDrop,"store an item"))
                        if foundDirectDrop[1] == (0,1):
                            return (None,((inventoryCommand+interactionCommand+"s")*numToDrop,"store an item"))
                        if foundDirectDrop[1] == (0,0):
                            return (None,((inventoryCommand+"l")*numToDrop,"store an item"))
                else:
                    if foundDirectDrop[1] == (-1,0):
                        command = "Ja"*10
                        if "advancedInteraction" in character.interactionState:
                            command = command[1:]
                        return (None,(command,"put scrap on scrap pile"))
                    if foundDirectDrop[1] == (1,0):
                        command = "Jd"*10
                        if "advancedInteraction" in character.interactionState:
                            command = command[1:]
                        return (None,(command,"put scrap on scrap pile"))
                    if foundDirectDrop[1] == (0,-1):
                        command = "Jw"*10
                        if "advancedInteraction" in character.interactionState:
                            command = command[1:]
                        return (None,(command,"put scrap on scrap pile"))
                    if foundDirectDrop[1] == (0,1):
                        command = "Js"*10
                        if "advancedInteraction" in character.interactionState:
                            command = command[1:]
                        return (None,(command,"put scrap on scrap pile"))
                    if foundDirectDrop[1] == (0,0):
                        return (None,("j"*self.getNumDrops(character),"put scrap on scrap pile"))

            foundNeighbour = None
            for slot in inputSlots:
                if len(slot[0]) < 3:
                    slot = ((slot[0][0],slot[0][1],0),slot[1],slot[2])
                for direction in ((-1,0),(1,0),(0,-1),(0,1)):
                    neighbour = (slot[0][0]-direction[0],slot[0][1]-direction[1],slot[0][2])
                    if neighbour not in room.walkingSpace:
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
                        if not room.getPositionWalkable(neighbour):
                            continue
                        foundNeighbour = (neighbour,direction)
                        break
                    if foundNeighbour:
                        break

            if not foundNeighbour:
                if not dryRun:
                    self.fail(reason="no dropoff found")
                return (None,None)

            quest = src.quests.questMap["GoToPosition"](reason="get to the stockpile and be able to fill it")
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

        if not dryRun:
            self.fail()
        return (None,None)

    def getQuestMarkersTile(self,character):
        result = super().getQuestMarkersTile(character)
        if self.targetPositionBig:
            result.append(((self.targetPositionBig[0],self.targetPositionBig[1]),"target"))
        return result

    @staticmethod
    def generateDutyQuest(beUsefull,character,currentRoom, dryRun):
        checkedTypes = set()
        rooms = character.getTerrain().rooms[:]
        random.shuffle(rooms)

        for trueInput in (True,False):
            for room in beUsefull.getRandomPriotisedRooms(character,currentRoom):
                emptyInputSlots = room.getEmptyInputslots(allowStorage=(not trueInput),allowAny=True)
                random.shuffle(emptyInputSlots)

                if emptyInputSlots:
                    for inputSlot in emptyInputSlots:
                        if inputSlot[1] is None:
                            items = room.getItemByPosition(inputSlot[0])
                            if items:
                                inputSlot = (inputSlot[0],items[0].type,inputSlot[2])
                        if inputSlot[1] in checkedTypes:
                            continue
                        checkedTypes.add(inputSlot[1])

                        hasItem = False
                        if character.inventory and (character.inventory[-1].type == inputSlot[1] or not inputSlot[1]):
                            hasItem = True

                        if not hasItem:
                            allowStorage = trueInput
                            if inputSlot[2].get("desiredState") == "filled":
                                allowStorage = True
                            sources = room.getNonEmptyOutputslots(itemType=inputSlot[1],allowStorage=allowStorage,allowDesiredFilled=trueInput)
                            if not sources:
                                continue

                        reason = "finish hauling"
                        quests = []
                        if inputSlot[1]:
                            quests.append(src.quests.questMap["RestockRoom"](toRestock=inputSlot[1],allowAny=True,reason=reason,targetPosition=inputSlot[0]))
                            if character.container != room:
                                quests.append(src.quests.questMap["GoToTile"](targetPosition=room.getPosition()))
                        else:
                            if hasItem:
                                quests.append(src.quests.questMap["RestockRoom"](toRestock=character.inventory[-1].type,allowAny=True,reason=reason,targetPosition=inputSlot[0]))
                                if character.container != room:
                                    quests.append(src.quests.questMap["GoToTile"](targetPosition=room.getPosition()))
                                if not dryRun:
                                    beUsefull.idleCounter = 0
                                return (quests,None)

                        if not hasItem:
                            if trueInput:
                                quests.append(src.quests.questMap["FetchItems"](toCollect=inputSlot[1]))
                                if not dryRun:
                                    beUsefull.idleCounter = 0
                                return (quests,None)
                            else:
                                quests.append(src.quests.questMap["CleanSpace"](targetPositionBig=room.getPosition(),targetPosition=sources[0][0]))
                                if not dryRun:
                                    beUsefull.idleCounter = 0
                                return (quests,None)

        for trueInput in (True,False):
            for room in beUsefull.getRandomPriotisedRooms(character,currentRoom):
                emptyInputSlots = room.getEmptyInputslots(allowStorage=(not trueInput),allowAny=True)

                if emptyInputSlots:
                    for inputSlot in random.sample(list(emptyInputSlots),len(emptyInputSlots)):
                        if inputSlot[1] is None:
                            items = room.getItemByPosition(inputSlot[0])
                            if items:
                                inputSlot = (inputSlot[0],items[0].type,inputSlot[2])
                        if inputSlot[1] in checkedTypes:
                            continue
                        checkedTypes.add(inputSlot[1])

                        hasItem = False
                        if character.inventory and (character.inventory[-1].type == inputSlot[1] or not inputSlot[1]):
                            hasItem = True

                        if not hasItem:
                            sources = room.getNonEmptyOutputslots(itemType=inputSlot[1],allowStorage=trueInput)
                            if not sources:
                                continue

                        reason = "finish hauling"
                        quests = []
                        if inputSlot[1]:
                            quests.append(src.quests.questMap["RestockRoom"](toRestock=inputSlot[1],allowAny=True,reason=reason))
                        else:
                            if hasItem:
                                quests.append(src.quests.questMap["RestockRoom"](toRestock=character.inventory[-1].type,allowAny=True,reason=reason))
                                if not dryRun:
                                    beUsefull.idleCounter = 0
                                return (quests,None)


                        if not hasItem:
                            if trueInput:
                                quests.append(src.quests.questMap["FetchItems"](toCollect=inputSlot[1]))
                                if not dryRun:
                                    beUsefull.idleCounter = 0
                                return (quests,None)
                            else:
                                quests.append(src.quests.questMap["CleanSpace"](targetPositionBig=room.getPosition(),targetPosition=sources[0][0]))
                                if not dryRun:
                                    beUsefull.idleCounter = 0
                                return (quests,None)

        for room in beUsefull.getRandomPriotisedRooms(character,currentRoom):
            for storageSlot in room.storageSlots:
                if storageSlot[2].get("desiredState") != "filled":
                    continue

                items = room.getItemByPosition(storageSlot[0])
                if items and (not items[0].walkable or len(items) >= 20):
                    continue
                if items and items[0].type != storageSlot[1]:
                    continue

                for checkStorageSlot in room.storageSlots:
                    if checkStorageSlot[1] == storageSlot[1] or not checkStorageSlot[1]:
                        items = room.getItemByPosition(checkStorageSlot[0])
                        if checkStorageSlot[2].get("desiredState") == "filled":
                            continue
                        if not items or items[0].type != storageSlot[1] or not items[0].walkable:
                            continue

                        quests = [src.quests.questMap["RestockRoom"](targetPositionBig=room.getPosition(),targetPosition=storageSlot[0],allowAny=True,toRestock=items[0].type,reason="fill a storage stockpile designated to be filled")
                                 ,src.quests.questMap["CleanSpace"](targetPositionBig=room.getPosition(),targetPosition=checkStorageSlot[0],reason="to get the items to fill a storage stockpile designated to be filled",abortOnfullInventory=True)]
                        if not dryRun:
                            beUsefull.idleCounter = 0
                        return (quests,None)
        return (None,None)

src.quests.addType(RestockRoom)

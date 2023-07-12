import src
import random

class BeUsefull(src.quests.MetaQuestSequence):
    type = "BeUsefull"

    def __init__(self, description="be useful", creator=None, targetPosition=None, strict=False):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description

        self.targetPosition = None
        self.idleCounter = 0
        if targetPosition:
            self.setParameters({"targetPosition":targetPosition})

        self.shortCode = " "
        self.strict = strict

    def generateTextDescription(self):
        out = """
Be useful.

Try fulfill your duties on this base with the skills you have.

You can lern new skills at the basic trainer in the command centre.
You can change your duties and get promotions at the assimilator.

Your duties are:

"""
        if not self.character.duties:
            out += "You have no duties, something has gone wrong."

        for duty in self.character.duties:
            if duty == "Questing":
                out += duty+""":
Get quests from the quest artwork and complete them.
The quest artwork is in the command centre.
Kill more enemies for additional reputation.\n\n"""
            elif duty == "resource gathering":
                out += duty+""":
Search for rooms with empty scrap input stockpiles.
Gather scrap and fill up those stockpiles.
Reputation is rewarded for filling up stockpiles.\n\n"""
            elif duty == "trap setting":
                out += duty+""":
Search for trap rooms without full charge.
Recharge them with ligthning rods.
Reputation is rewarded for recharging trap rooms.\n\n"""
            elif duty == "cleaning":
                out += duty+""":
Search for rooms with items cluttering the floor.
Remove those items.
Reputation is rewarded for picking up items from walkways.\n\n"""
            else:
                out += "%s\n\n"%(duty,)

        if not self.character.rank == 3:
            reputationForPromotion = "???"
            if self.character.rank == 6:
                reputationForPromotion = 300
            if self.character.rank == 5:
                reputationForPromotion = 500
            if self.character.rank == 4:
                reputationForPromotion = 750

            out += "%s"%(self.idleCounter,)

            out += """

You need %s reputation for a promotion.
You currently have %s reputation.
Do your duty to gain more reputation.
Try to avoid losing reputation due to beeing careless.

"""%(reputationForPromotion,self.character.reputation,)

        if not self.subQuests:
            out += """

This quest currently has no sub quests.
Press r to generate subquest and recive detailed instructions
"""


        return out

    def getSolvingCommandString(self,character,dryRun=True):
        if not self.subQuests:
            submenue = character.macroState.get("submenue")
            if submenue:
                if isinstance(submenue,src.interaction.SelectionMenu):
                    return ["enter"]
                return ["esc"]
        return super().getSolvingCommandString(character,dryRun=dryRun)

    def awardnearbyKillReputation(self,extraInfo):
        if not extraInfo["deadChar"].faction == self.character.faction:
            if "Questing" in self.character.duties:
                amount = 5*self.character.rank
                amount += extraInfo["deadChar"].maxHealth//3
                self.character.awardReputation(amount,reason="an enemy dying nearby")
        else:
            amount = 30
            if extraInfo["deadChar"].rank == 3:
                amount = 500
            if extraInfo["deadChar"].rank == 4:
                amount = 250
            if extraInfo["deadChar"].rank == 5:
                amount = 100
            if extraInfo["deadChar"].rank == 6:
                amount = 50
            self.character.revokeReputation(amount,reason="an ally dying nearby")
    
    def handleMovement(self, extraInfo):
        toRemove = []
        for quest in self.subQuests:
            if quest.completed:
                toRemove.append(quest)

        for quest in toRemove:
            self.subQuests.remove(quest)

    def handleChangedDuties(self,character=None):
        for quest in self.subQuests[:]:
            quest.fail()
        self.handleMovement(None)

    def handleChargedTrapRoom(self,extraInfo):
        # reload trap room
        if "trap setting" in self.character.duties:
            self.character.awardReputation(10, reason="charging a trap room")

    def handleDroppedItem(self,extraInfo):
        if isinstance(self.character.container,src.terrains.Terrain):
            self.character.revokeReputation(2, reason="discarding an item")
            return
        else:
            item = extraInfo[1]
            itemPos = item.getPosition()
            room = self.character.container
            if itemPos in room.walkingSpace:
                if item.walkable:
                    self.character.revokeReputation(5, reason="cluttering a walkway")
                else:
                    self.character.revokeReputation(50, reason="cluttering a walkway")

            for inputSlot in room.inputSlots:
                if inputSlot[0] == itemPos:
                    if inputSlot[1] == item.type:
                        if "resource gathering" in self.character.duties:
                            items = room.getItemByPosition(itemPos)
                            if len(items) == 1 and not (items[0].type == "Scrap" and items[0].amount > 1):
                                self.character.awardReputation(20, reason="delivering an item into an empty input stockpile")
                            else:
                                self.character.awardReputation(5, reason="delivering an item into an input stockpile")
                    else:
                        self.character.revokeReputation(50, reason="delivering a wrong item into an input stockpile")
            
            for outputSlot in room.outputSlots:
                if outputSlot[0] == itemPos:
                    if outputSlot[1] == item.type:
                        self.character.revokeReputation(1, reason="putting an item into an output stockpile")
                    else:
                        self.character.revokeReputation(50, reason="putting a wrong item into an output stockpile")

    def handleOperatedMachine(self,extraInfo):
        if "machine operation" in self.character.duties:
            if extraInfo["machine"].type == "ScrapCompactor":
                self.character.awardReputation(5, reason="operating a scrap compactor")
            else:
                self.character.awardReputation(10, reason="operating a machine")

    def pickedUpItem(self,extraInfo):
        if not self.character == src.gamestate.gamestate.mainChar:
            return
        
        if isinstance(self.character.container,src.terrains.Terrain):
            if "resource gathering" in self.character.duties:
                self.character.awardReputation(1, reason="gathering an item")
        else:
            room = self.character.container
            if "cleaning" in self.character.duties:
                if extraInfo[2] in room.walkingSpace:
                    self.character.awardReputation(2, reason="cleaning a cluttered walkway")

            for inputSlot in room.inputSlots:
                if inputSlot[0] == extraInfo[2]:
                    self.character.revokeReputation(50, reason="taking an item out of an input stockpile")
            
    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.awardnearbyKillReputation, "character died on tile")
        self.startWatching(character,self.handleMovement, "moved")
        self.startWatching(character,self.handleChangedDuties, "changed duties")
        self.startWatching(character,self.handleChargedTrapRoom, "charged traproom")
        self.startWatching(character,self.handleDroppedItem, "dropped")
        self.startWatching(character,self.pickedUpItem, "itemPickedUp")
        self.startWatching(character,self.handleOperatedMachine, "operated machine")
        super().assignToCharacter(character)

    def triggerCompletionCheck(self,character=None):
        return

    def setParameters(self,parameters):
        if "targetPosition" in parameters and "targetPosition" in parameters:
            self.targetPosition = parameters["targetPosition"]
        return super().setParameters(parameters)

    def solver(self, character):
        for quest in self.subQuests[:]:
            if quest.completed:
                self.subQuests.remove(quest)

        if not self.subQuests:
            self.generateSubquests(character)
            if self.subQuests:
                character.timeTaken += 1
                return

            command = self.getSolvingCommandString(character)
            if command:
                character.runCommandString(command)
                character.timeTaken += 1
                return

        super().solver(character)

    def checkTriggerTrapSetting(self,character,room):
        if hasattr(room,"electricalCharges"):
            if room.electricalCharges < room.maxElectricalCharges:

                quest = src.quests.questMap["ReloadTraproom"](targetPosition=room.getPosition())
                self.addQuest(quest)
                quest.activate()
                self.idleCounter = 0
                return True

    def checkTriggerMachineOperation(self,character,room):
        items = room.itemsOnFloor[:]
        random.shuffle(items)
        for item in items:
            #if not item.bolted:
            #    continue
            if not item.type in ("Machine","ScrapCompactor","MaggotFermenter","BioPress","GooProducer"):
                continue
            if not item.readyToUse():
                continue
            quest = src.quests.questMap["OperateMachine"](targetPosition=item.getPosition())
            self.addQuest(quest)
            quest.activate()
            self.idleCounter = 0
            return True

    def checkTriggerResourceGathering(self,character,room):
        emptyInputSlots = room.getEmptyInputslots(itemType="Scrap")
        if emptyInputSlots:
            for inputSlot in emptyInputSlots:
                if not inputSlot[1] == "Scrap":
                    continue

                source = None
                if room.sources:
                    for potentialSource in random.sample(list(room.sources),len(room.sources)):
                        if potentialSource[1] == "rawScrap":
                            source = potentialSource
                            break

                if source == None and not character.getTerrain().scrapFields:
                    continue

                if self.triggerClearInventory(character,room):
                    return True

                if source:
                    pos = source[0]
                else:
                    pos = random.choice(character.getTerrain().scrapFields)

                self.addQuest(src.quests.questMap["RestockRoom"](toRestock="Scrap"))
                self.addQuest(src.quests.questMap["GoToTile"](targetPosition=(room.xPosition,room.yPosition)))
                self.addQuest(src.quests.questMap["GatherScrap"](targetPosition=pos))
                self.addQuest(src.quests.questMap["GoToTile"](targetPosition=pos))
                self.idleCounter = 0
                return True

    def checkTriggerMaggotGathering(self,character,room):
        emptyInputSlots = room.getEmptyInputslots(itemType="VatMaggot")
        if emptyInputSlots:
            for inputSlot in emptyInputSlots:
                if not inputSlot[1] == "VatMaggot":
                    continue

                source = None
                if room.sources:
                    for potentialSource in random.sample(list(room.sources),len(room.sources)):
                        if potentialSource[1] == "rawVatMaggots":
                            source = potentialSource
                            break

                if source == None and not character.getTerrain().forests:
                    continue

                if self.triggerClearInventory(character,room):
                    return True

                if source:
                    pos = source[0]
                else:
                    pos = random.choice(character.getTerrain().forests)

                self.addQuest(src.quests.questMap["RestockRoom"](toRestock="VatMaggot"))
                self.addQuest(src.quests.questMap["GoToTile"](targetPosition=(room.xPosition,room.yPosition)))
                self.addQuest(src.quests.questMap["GatherVatMaggots"](targetPosition=pos))
                self.addQuest(src.quests.questMap["GoToTile"](targetPosition=pos))
                self.idleCounter = 0
                return True

    def checkTriggerScratchChecking(self,character,room):
        for item in random.sample(list(room.itemsOnFloor),len(room.itemsOnFloor)):
            if not item.bolted:
                continue
            if item.type == "ScratchPlate":
                if item.hasScratch():
                    continue
                self.addQuest(src.quests.questMap["RunCommand"](command="jsj"))
                self.addQuest(src.quests.questMap["GoToPosition"](targetPosition=item.getPosition()))
                self.idleCounter = 0
                return

    def checkTriggerCleaning(self,character,room):
        # clean up room
        if not room.floorPlan:
            for position in random.sample(list(room.walkingSpace),len(room.walkingSpace)):
                items = room.getItemByPosition(position)

                if not items:
                    continue
                if items[0].bolted:
                    continue

                if character.getFreeInventorySpace() <= 0:
                    quest = src.quests.questMap["ClearInventory"]()
                    self.addQuest(quest)
                    return True

                quest = src.quests.questMap["ClearTile"](targetPosition=room.getPosition())
                self.addQuest(quest)
                quest.assignToCharacter(character)
                quest.activate()
                self.idleCounter = 0
                return True

            if len(character.inventory):
                if room.getEmptyInputslots(itemType=character.inventory[-1].type,allowAny=True):
                    quest = src.quests.questMap["ClearInventory"]()
                    self.addQuest(quest)
                    return True

    def checkTriggerHauling(self,character,room):
        if hasattr(room,"inputSlots"):
            checkedTypes = set()

            emptyInputSlots = room.getEmptyInputslots(allowStorage=False)
            if emptyInputSlots:

                for inputSlot in random.sample(list(emptyInputSlots),len(emptyInputSlots)):
                    if inputSlot[1] == None:
                        continue
                    if inputSlot[1] in checkedTypes:
                        continue
                    checkedTypes.add(inputSlot[1])

                    hasItem = False
                    if character.inventory and character.inventory[-1].type == inputSlot[1]:
                        hasItem = True

                    if not hasItem:
                        if not room.getNonEmptyOutputslots(itemType=inputSlot[1]):
                            continue

                    self.addQuest(src.quests.questMap["RestockRoom"](toRestock=inputSlot[1]))

                    if not hasItem:
                        if self.triggerClearInventory(character,room):
                            return True

                    self.addQuest(src.quests.questMap["FetchItems"](toCollect=inputSlot[1]))
                    self.idleCounter = 0
                    return True

    def checkTriggerResourceFetching(self,character,room):
        if hasattr(room,"inputSlots"):
            emptyInputSlots = room.getEmptyInputslots()
            if emptyInputSlots:
                checkedTypes = set()

                for inputSlot in random.sample(list(emptyInputSlots),len(emptyInputSlots)):
                    if inputSlot[1] == None:
                        continue
                    if inputSlot[1] in checkedTypes:
                        continue
                    checkedTypes.add(inputSlot[1])

                    hasItem = False
                    if character.inventory and character.inventory[-1].type == inputSlot[1]:
                        hasItem = True

                    if not hasItem:
                        source = None
                        for candidateSource in room.sources:
                            if not candidateSource[1] == inputSlot[1]:
                                continue

                            sourceRoom = room.container.getRoomByPosition(candidateSource[0])
                            if not sourceRoom:
                                continue

                            sourceRoom = sourceRoom[0]
                            if not sourceRoom.getNonEmptyOutputslots(itemType=inputSlot[1]):
                                continue

                            source = candidateSource
                            break

                        if not source:
                            for otherRoom in random.sample(character.getTerrain().rooms,len(character.getTerrain().rooms)):
                                if otherRoom == character.container:
                                    continue

                                if not otherRoom.getNonEmptyOutputslots(itemType=inputSlot[1]):
                                    continue

                                source = (otherRoom.getPosition(),inputSlot[1])
                                break

                        if not source:
                            character.addMessage("no filled output slots")
                            continue

                    if not hasItem:
                        if self.triggerClearInventory(character,room):
                            return True

                    self.addQuest(src.quests.questMap["RestockRoom"](toRestock=inputSlot[1],reason="restock the room with the items fetched"))
                    self.idleCounter = 0

                    if not hasItem:
                        amountToFetch = None
                        if src.gamestate.gamestate.mainChar == character:
                            walkable = False
                            if inputSlot[1] in src.items.itemMap:
                                walkable = src.items.itemMap[inputSlot[1]]().walkable
                            amountNeeded = 0
                            for checkInputSlot in emptyInputSlots:
                                if checkInputSlot[1] == inputSlot[1]:
                                    if walkable:
                                        amountNeeded += 20-len(room.getItemByPosition(inputSlot[0]))
                                    else:
                                        amountNeeded += 1

                            if amountNeeded < character.maxInventorySpace:
                                amountToFetch = amountNeeded

                        roomPos = (room.xPosition,room.yPosition,0)
                        if not source[0] == roomPos:
                            self.addQuest(src.quests.questMap["GoToTile"](targetPosition=roomPos))

                        self.addQuest(src.quests.questMap["FetchItems"](toCollect=inputSlot[1], amount=amountToFetch))
                        if not source[0] == roomPos:
                            self.addQuest(src.quests.questMap["GoToTile"](targetPosition=(source[0])))

                        if character.inventory and (not amountToFetch or amountToFetch > character.getFreeInventorySpace()):
                            self.addQuest(src.quests.questMap["ClearInventory"](returnToTile=False))


                    return True

                character.addMessage("no valid input slot found")
            character.addMessage("no empty input slot found")
        character.addMessage("no input slots")

    def checkTriggerPainting(self,character,room):
        # set up machines
        if room.floorPlan:
            self.addQuest(src.quests.questMap["DrawFloorPlan"](targetPosition=room.getPosition()))
            self.idleCounter = 0
            return True

    def checkTriggerRoomBuilding(self,character,room):
        #src.gamestate.gamestate.mainChar = character
        terrain = character.getTerrain()
        for x in range(1,13):
            for y in range(1,13):
                items = terrain.getItemByPosition((x*15+7,y*15+7,0))
                if items:
                    if items[0].type == "RoomBuilder":
                        self.addQuest(src.quests.questMap["BuildRoom"](targetPosition=(x,y,0)))
                        self.idleCounter = 0
                        return True

        rooms = terrain.getRoomByPosition((7,7,0))
        if rooms:
            room = rooms[0]
            cityPlaner = room.getItemByType("CityPlaner")
            if cityPlaner:
                while cityPlaner.plannedRooms:
                    if terrain.getRoomByPosition(cityPlaner.plannedRooms[-1]):
                        cityPlaner.plannedRooms.pop()
                        continue

                    self.addQuest(src.quests.questMap["BuildRoom"](targetPosition=cityPlaner.plannedRooms[-1]))
                    self.idleCounter = 0
                    return True
                
    def checkTriggerMachinePlacing(self,character,room):
        if (not room.floorPlan) and room.buildSites:
            for buildSite in room.buildSites:
                if buildSite[1] == "Machine":
                    self.addQuest(src.quests.questMap["SetUpMachine"](itemType=buildSite[2]["toProduce"],targetPositionBig=room.getPosition(),targetPosition=buildSite[0]))
                    return True
            checkedMaterial = set()
            #for buildSite in random.sample(room.buildSites,len(room.buildSites)):
            for buildSite in room.buildSites:
                if "reservedTill" in buildSite[2] and buildSite[2]["reservedTill"] > room.timeIndex:
                    continue
                if buildSite[1] in checkedMaterial:
                    continue
                checkedMaterial.add(buildSite[1])

                neededItem = buildSite[1]
                if buildSite[1] == "Command":
                    neededItem = "Sheet"
                hasItem = False
                source = None
                if character.inventory and character.inventory[-1].type == neededItem:
                    hasItem = True

                if not hasItem:
                    for candidateSource in room.sources:
                        if not candidateSource[1] == neededItem:
                            continue

                        sourceRoom = room.container.getRoomByPosition(candidateSource[0])
                        if not sourceRoom:
                            continue

                        sourceRoom = sourceRoom[0]
                        if not sourceRoom.getNonEmptyOutputslots(itemType=neededItem):
                            continue

                        source = candidateSource
                        break

                    if not source:
                        for room in random.sample(character.getTerrain().rooms,len(character.getTerrain().rooms)):
                            if not room.getNonEmptyOutputslots(itemType=neededItem):
                                continue

                            source = (room.getPosition(),neededItem)
                            break

                    if not source:
                        character.addMessage("no machine placing - no filled output slots")
                        continue

                if hasItem:
                    if buildSite[1] == "Command":
                        if "command" in buildSite[2]:
                            self.addQuest(src.quests.questMap["RunCommand"](command="jjssj%s\n"%(buildSite[2]["command"])))
                        else:
                            self.addQuest(src.quests.questMap["RunCommand"](command="jjssj.\n"))
                    self.addQuest(src.quests.questMap["RunCommand"](command="l"))
                    self.addQuest(src.quests.questMap["GoToPosition"](targetPosition=buildSite[0]))
                    buildSite[2]["reservedTill"] = room.timeIndex+100
                elif source:
                    if not character.getFreeInventorySpace() > 0:
                        quest = src.quests.questMap["ClearInventory"]()
                        self.addQuest(quest)
                        quest.assignToCharacter(character)
                        quest.activate()
                        return True

                    roomPos = (room.xPosition,room.yPosition)

                    if not source[0] == roomPos:
                        self.addQuest(src.quests.questMap["GoToTile"](targetPosition=roomPos))
                    self.addQuest(src.quests.questMap["FetchItems"](toCollect=neededItem,amount=1))
                    if not source[0] == roomPos:
                        self.addQuest(src.quests.questMap["GoToTile"](targetPosition=(source[0])))
                self.idleCounter = 0
                return True

    def checkTriggerFillFlask(self,character,room):
        if character.flask and character.flask.uses < 3:
            self.addQuest(src.quests.questMap["FillFlask"]())
            return True

    def checkTriggerScavenging(self,character,room):
        terrain = character.getTerrain()
        while terrain.collectionSpots:
            if not terrain.itemsByBigCoordinate.get(terrain.collectionSpots[-1]):
                terrain.collectionSpots.pop()
                continue
            self.addQuest(src.quests.questMap["ScavengeTile"](targetPosition=(terrain.collectionSpots[-1])))
            return True

    def checkTriggerEat(self,character,room):
        if character.satiation < 200:
            self.addQuest(src.quests.questMap["Eat"]())
            return True

    def triggerClearInventory(self,character,room):
        if len(character.inventory) > 9:
            self.addQuest(src.quests.questMap["ClearInventory"]())
            return True
        # clear inventory local
        if len(character.inventory) > 1:
            emptyInputSlots = room.getEmptyInputslots(character.inventory[-1].type, allowAny=True)
            if emptyInputSlots:
                self.addQuest(src.quests.questMap["RestockRoom"](toRestock=character.inventory[-1].type, allowAny=True,reason="clear your inventory"))
                return True

        # go to garbage stockpile and unload
        if len(character.inventory) > 6:
            if not "HOMEx" in character.registers:
                return True
            homeRoom = room.container.getRoomByPosition((character.registers["HOMEx"],character.registers["HOMEy"]))[0]
            if not hasattr(homeRoom,"storageRooms") or not homeRoom.storageRooms:
                return False

            quest = src.quests.questMap["GoToTile"](targetPosition=(homeRoom.storageRooms[0].xPosition,homeRoom.storageRooms[0].yPosition,0))
            self.addQuest(quest)
            quest.assignToCharacter(character)
            quest.activate()
            return True
        if len(character.inventory) > 9:
            quest = src.quests.questMap["ClearInventory"]()
            self.addQuest(quest)
            quest.assignToCharacter(character)
            quest.activate()
            return True
        return False

    def generateSubquests(self,character):

        for quest in self.subQuests:
            if quest.completed:
                self.subQuests.remove(quest)
                break

        self.triggerCompletionCheck(character)

        if not character.container:
            return

        if not character.superior and character.rank == 6 and character.reputation >= 300:
            quest = src.quests.questMap["GetPromotion"](5)
            self.addQuest(quest)
            quest.activate()
            quest.assignToCharacter(character)
            return

        if not character.superior and character.rank == 5 and character.reputation >= 500:
            quest = src.quests.questMap["GetPromotion"](4)
            self.addQuest(quest)
            quest.activate()
            quest.assignToCharacter(character)
            return

        if not character.superior and character.rank == 4 and character.reputation >= 750:
            quest = src.quests.questMap["GetPromotion"](3)
            self.addQuest(quest)
            quest.activate()
            quest.assignToCharacter(character)
            return

        if (character.rank == 5 and character.getNumSubordinates() < 1) or (character.rank == 4 and character.getNumSubordinates() < 2) or (character.rank == 3 and character.getNumSubordinates() < 3):
            homeRoom = character.getHomeRoom()
            if homeRoom:
                personelArtwork = homeRoom.getItemByType("PersonnelArtwork")
                if personelArtwork and personelArtwork.charges:
                    quest = src.quests.questMap["GetBodyGuards"]()
                    self.addQuest(quest)
                    quest.activate()
                    quest.assignToCharacter(character)
                    return

        if not isinstance(character.container,src.rooms.Room):
            if character.yPosition%15 == 14:
                character.runCommandString("w")
                return
            if character.yPosition%15 == 0:
                character.runCommandString("s")
                return
            if character.xPosition%15 == 14:
                character.runCommandString("a")
                return
            if character.xPosition%15 == 0:
                character.runCommandString("d")
                return

        if not isinstance(character.container,src.rooms.Room):
            if self.targetPosition:
                quest = src.quests.questMap["GoToTile"](targetPosition=self.targetPosition)
                self.addQuest(quest)
                quest.activate()
                quest.assignToCharacter(character)
            else:
                quest = src.quests.questMap["GoHome"]()
                self.addQuest(quest)
                quest.activate()
                quest.assignToCharacter(character)
            return

        room = character.container

        if character.rank == 3:
            self.addQuest(src.quests.questMap["ManageBase"]())
            return

        if not self.strict and (self.idleCounter > 15 or (character.rank == 6 and len(character.duties) < 1) or (character.rank == 5 and len(character.duties) < 2) or (character.rank == 4 and len(character.duties) < 3) or (character.rank == 3 and len(character.duties) < 4)):
            quest = src.quests.questMap["ChangeJob"]()
            self.addQuest(quest)
            quest.activate()
            quest.assignToCharacter(character)
            self.idleCounter = 0
            return

        if character.health < character.maxHealth//2:
            foundItem = None
            for item in character.inventory:
                if not item.type == "Vial":
                    continue
                if not item.uses:
                    continue
                foundItem = item

            if foundItem:
                quest = src.quests.questMap["Heal"]()
                self.addQuest(quest)
                quest.assignToCharacter(character)
                quest.activate()
                return

        if "guarding" in character.duties:
            for otherCharacter in room.characters:
                if not otherCharacter.faction == character.faction:
                    character.runCommandString("gg")
                    self.idleCounter = 0
                    return

        if character.isMilitary or "guarding" in character.duties or "Questing" in character.duties:
            if not character.weapon or not character.armor:
                quest = src.quests.questMap["Equip"](lifetime=1000)
                quest.assignToCharacter(character)
                self.addQuest(quest)
                self.idleCounter = 0
                return

        if character.isMilitary or "Questing" in character.duties:
            quest = src.quests.questMap["GetQuestFromQuestArtwork"]()
            self.addQuest(quest)
            quest.active = True
            quest.assignToCharacter(character)
            self.idleCounter = 0
            return

        if self.targetPosition:
            if not (self.targetPosition[0] == room.xPosition and self.targetPosition[1] == room.yPosition):
                quest = src.quests.questMap["GoToTile"](targetPosition=self.targetPosition)
                self.addQuest(quest)
                quest.assignToCharacter(character)
                quest.activate()
                return

        if self.checkTriggerFillFlask(character,room):
            return

        if self.checkTriggerEat(character,room):
            return

        terrain = character.getTerrain()
        for checkRoom in terrain.rooms:
            try:
                checkRoom.requiredDuties
            except:
                checkRoom.requiredDuties = []

            if not checkRoom.requiredDuties:
                continue

            for duty in checkRoom.requiredDuties:
                if not duty in character.duties:
                    continue

                """
                if duty == "machine operation":
                    quest = src.quests.questMap["OperateMachine"](targetPosition=item.getPosition())
                    self.addQuest(quest)
                    quest.activate()
                    self.idleCounter = 0
                    print(room.requiredDuties)
                """

                checkRoom.requiredDuties.remove(duty)

                quest = src.quests.questMap["GoToTile"](targetPosition=checkRoom.getPosition())
                self.addQuest(quest)
                quest.activate()
                return

        for duty in character.duties:
            if duty == "trap setting":
                if self.checkTriggerTrapSetting(character,room):
                    return

            if duty == "machine operation":
                if self.checkTriggerMachineOperation(character,room):
                    return

            if duty == "resource gathering":
                if self.checkTriggerResourceGathering(character,room):
                    return

            if duty == "maggot gathering":
                if self.checkTriggerMaggotGathering(character,room):
                    return

            if duty == "scratch checking":
                if self.checkTriggerScratchChecking(character,room):
                    return

            if duty == "cleaning":
                if self.checkTriggerCleaning(character,room):
                    return

            if duty == "hauling":
                if self.checkTriggerHauling(character,room):
                    return

            if duty == "resource fetching":
                if self.checkTriggerResourceFetching(character,room):
                    return

            if duty == "painting":
                if self.checkTriggerPainting(character,room):
                    return

            if duty == "machine placing":
                if self.checkTriggerMachinePlacing(character,room):
                    return

            if duty == "room building":
                if self.checkTriggerRoomBuilding(character,room):
                    return

            if duty == "scavenging":
                if self.checkTriggerScavenging(character,room):
                    return

        if not self.targetPosition:
            directions = [(-1,0),(1,0),(0,-1),(0,1)]
            random.shuffle(directions)
            for direction in directions:
                newPos = (room.xPosition+direction[0],room.yPosition+direction[1])
                if room.container.getRoomByPosition(newPos):
                    quest = src.quests.questMap["GoToTile"](targetPosition=newPos,description="look for job on tile ")
                    self.idleCounter += 1
                    self.addQuest(quest)
                    quest.assignToCharacter(character)
                    quest.activate()
                    character.runCommandString("%s."%(self.idleCounter,))
                    return

        self.idleCounter += 5
        character.runCommandString("20.")

src.quests.addType(BeUsefull)

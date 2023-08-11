import src
import random

class BeUsefull(src.quests.MetaQuestSequence):
    type = "BeUsefull"

    def __init__(self, description="be useful", creator=None, targetPosition=None, strict=False, reason=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description

        self.targetPosition = None
        self.idleCounter = 0
        if targetPosition:
            self.setParameters({"targetPosition":targetPosition})

        self.shortCode = " "
        self.strict = strict

        self.checkedRoomPositions = []
        self.reason = reason

    def generateTextDescription(self):
        reason = ""
        if self.reason:
            reason = ", to %s"%(self.reason,)
        out = """
Be useful%s.

Try fulfill your duties on this base with the skills you have.

Your duties are:

%s

    
"""%(reason,"\n".join(self.character.duties),)
        if not self.character.duties:
            out += "You have no duties, something has gone wrong."

        if not len(self.character.duties) > 2:
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

        out = [out]
        if not self.subQuests:
            out.append((src.interaction.urwid.AttrSpec("#f00", "black"),"""
This quest has no subquests. Press r to generate subquests for this quest."""))
        else:
            out.append((src.interaction.urwid.AttrSpec("#080", "black"),"""
This quests has subquests.
Press d to move the cursor and show the subquests description.
"""))
        return out

    def getSolvingCommandString(self,character,dryRun=True):
        if not self.subQuests:
            submenue = character.macroState.get("submenue")
            if submenue:
                if isinstance(submenue,src.interaction.SelectionMenu):
                    return ["esc"]
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
        character.timeTaken += 0.01
        for quest in self.subQuests[:]:
            if quest.completed:
                self.subQuests.remove(quest)

        if not self.subQuests:
            command = self.getSolvingCommandString(character)
            if command:
                character.runCommandString(command)
                character.timeTaken += 1
                return

            self.generateSubquests(character)
            if self.subQuests:
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
        terrain = character.getTerrain()
        rooms = terrain.rooms
        random.shuffle(rooms)
        for room in [room]+rooms:
            items = room.itemsOnFloor[:]
            random.shuffle(items)
            for item in items:
                #if not item.bolted:
                #    continue
                if not item.type in ("Machine","ScrapCompactor","MaggotFermenter","BioPress","GooProducer"):
                    continue
                if not item.readyToUse():
                    continue
                if room == character.container:
                    quest = src.quests.questMap["OperateMachine"](targetPosition=item.getPosition())
                    self.addQuest(quest)
                    quest.activate()
                    self.idleCounter = 0
                    return True
                else:
                    quest = src.quests.questMap["GoToTile"](targetPosition=room.getPosition(),reason="go to a machine room")
                    self.addQuest(quest)
                    quest.activate()
                    self.idleCounter = 0
                    return True

    def checkTriggerScrapHammering(self,character,room):
        for room in character.getTerrain().rooms:
            for anvil in room.getItemsByType("Anvil"):
                if anvil.scheduledItems:
                    self.addQuest(src.quests.questMap["ScrapHammering"](amount=min(10,len(anvil.scheduledItems))))
                    self.idleCounter = 0
                    return True

        itemsInStorage = {}
        freeStorage = 0
        for room in character.getTerrain().rooms:
            for storageSlot in room.storageSlots:
                items = room.getItemByPosition(storageSlot[0])
                if not items:
                    freeStorage += 1
                for item in items:
                    itemsInStorage[item.type] = itemsInStorage.get(item.type,0)+1

        if freeStorage:
            if itemsInStorage.get("MetalBars",0) < 40:
                self.addQuest(src.quests.questMap["ScrapHammering"](amount=10))
                self.idleCounter = 0
                return True

    def checkTriggerMetalWorking(self,character,room):
        for room in character.getTerrain().rooms:
            for metalWorkingBench in room.getItemsByType("MetalWorkingBench"):
                if metalWorkingBench.scheduledItems:
                    self.addQuest(src.quests.questMap["ClearInventory"]())
                    self.addQuest(src.quests.questMap["MetalWorking"](amount=1,toProduce=metalWorkingBench.scheduledItems[0]))
                    self.idleCounter = 0
                    return True

        itemsInStorage = {}
        freeStorage = 0
        for room in character.getTerrain().rooms:
            for storageSlot in room.storageSlots:
                items = room.getItemByPosition(storageSlot[0])
                if not items:
                    freeStorage += 1
                for item in items:
                    itemsInStorage[item.type] = itemsInStorage.get(item.type,0)+1

        if freeStorage:
            checkItems = [("RoomBuilder",1,1),("Door",4,1),("Painter",2,1),("Wall",10,3),("ScrapCompactor",2,1)]
            for checkItem in checkItems:
                if itemsInStorage.get(checkItem[0],0) < checkItem[1]:
                    self.addQuest(src.quests.questMap["ClearInventory"](returnToTile=False))
                    self.addQuest(src.quests.questMap["MetalWorking"](amount=checkItem[2],toProduce=checkItem[0]))
                    self.idleCounter = 0
                    return True

    def checkTriggerCloneSpawning(self,character,room):
        terrain = character.getTerrain()
        cityCore = terrain.getRoomByPosition((7,7,0))[0]
        epochArtwork = cityCore.getItemsByType("EpochArtwork",needsBolted=True)[0]

        if epochArtwork.recalculateGlasstears(character,dryRun=True):
            quest = src.quests.questMap["GetEpochEvaluation"](reason="collect the glass tears you earned")
            self.addQuest(quest)
            return True

        # gather npc duties
        npcDuties = {}
        for otherChar in terrain.characters:
            for duty in otherChar.duties:
                if otherChar == character:
                    continue
                if not duty in npcDuties:
                    npcDuties[duty] = []
                npcDuties[duty].append(otherChar)
        for checkRoom in character.getTerrain().rooms:
            for otherChar in checkRoom.characters:
                if otherChar == character:
                    continue
                for duty in otherChar.duties:
                    if not duty in npcDuties:
                        npcDuties[duty] = []
                    npcDuties[duty].append(otherChar)

        chargesUsed = 0
        quests = []
        for duty in ["metal working","scrap hammering","resource gathering","resource fetching","hauling","scavenging","machine operation","room building","painting","machine placing","maggot gathering"]:

            if not duty in npcDuties and epochArtwork.charges >= 10+chargesUsed:
                quest = src.quests.questMap["GetEpochReward"](rewardType="spawn "+duty+" NPC",reason="spawn another clone to help you out")
                chargesUsed += 10
                quests.append(quest)
        for quest in reversed(quests):
            self.addQuest(quest)
        if quests:
            return True

    def checkTriggerCityPlaning(self,character,room):
        terrain = character.getTerrain()
        cityCore = terrain.getRoomByPosition((7,7,0))[0]
        cityPlaner = cityCore.getItemByType("CityPlaner",needsBolted=True)
        epochArtwork = cityCore.getItemByType("EpochArtwork",needsBolted=True)

        if epochArtwork.recalculateGlasstears(character,dryRun=True):
            quest = src.quests.questMap["GetEpochEvaluation"](reason="collect the glass tears you earned")
            self.addQuest(quest)
            return True

        # do inventory of scrap fields
        numItemsScrapfield = 0
        for scrapField in terrain.scrapFields:
            numItemsScrapfield += len(terrain.itemsByBigCoordinate.get(scrapField,[]))

        if numItemsScrapfield < 100 and epochArtwork.charges >= 20:
            quest = src.quests.questMap["GetEpochReward"](rewardType="spawn scrap",reason="ensure enough scrap is available")
            self.addQuest(quest)

            if numItemsScrapfield < 50 and epochArtwork.charges >= 40:
                quest = src.quests.questMap["GetEpochReward"](rewardType="spawn scrap",reason="ensure enough scrap is available")
                self.addQuest(quest)
            return True

        if not cityPlaner:
            quest = src.quests.questMap["PlaceItem"](targetPositionBig=(7,7,0),targetPosition=(4,1,0),itemType="CityPlaner",tryHard=True,boltDown=True,reason="to be able to plan the citys expansion")
            self.addQuest(quest)
            return True

        numEmptyRooms = 0
        for room in terrain.rooms:
            if room.tag:
                continue
            if (len(room.itemsOnFloor) > 13+13+11+11 or room.floorPlan or room.storageSlots or len(room.walkingSpace) > 4 or room.inputSlots):
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
                for quest in quests:
                    self.addQuest(quest)
                return True

        # assign scheduled floor plans
        if cityPlaner and cityPlaner.getAvailableRooms():
            if cityPlaner.scheduledFloorPlans:
                for room in cityPlaner.getAvailableRooms():
                    quest = src.quests.questMap["AssignFloorPlan"](roomPosition=room.getPosition(),floorPlanType=cityPlaner.scheduledFloorPlans[0],reason="set a scheduled floor plan",)
                    self.addQuest(quest)
                    return True

        # ensure there is a general purpose room
        if cityPlaner and not cityPlaner.generalPurposeRooms:
            for room in terrain.rooms:
                if room.getPosition() == (7,0,0):
                    continue
                if room.getPosition() in cityPlaner.specialPurposeRooms:
                    continue
                if room.getPosition() in cityPlaner.generalPurposeRooms:
                    continue
                if (len(room.itemsOnFloor) > 13+13+11+11 or room.floorPlan or room.storageSlots or len(room.walkingSpace) > 4 or room.inputSlots):
                    continue

                quest = src.quests.questMap["DesignateRoom"](roomPosition=room.getPosition(),roomType="generalPurposeRoom",reason="reserve some room for unforseen needs")
                self.addQuest(quest)
                return True

        # add storage room if needed
        if cityPlaner and cityPlaner.getAvailableRooms():
            # count empty storage slots
            numFreeStorage = 0
            for room in terrain.rooms:
                for storageSlot in room.storageSlots:
                    if not storageSlot[1] == None:
                        continue
                    items = room.getItemByPosition(storageSlot[0])
                    if items:
                        continue
                    numFreeStorage += 1

            if numFreeStorage < 20:
                quest = src.quests.questMap["AssignFloorPlan"](roomPosition=cityPlaner.getAvailableRooms()[0].getPosition(),floorPlanType="storage",reason="increase storage")
                self.addQuest(quest)
                return True

        # add meeting hall if there is none
        if cityPlaner and not cityPlaner.generalPurposeRooms:
            for room in terrain.rooms:
                if room.getPosition() == (7,0,0):
                    continue
                if room.getPosition() in cityPlaner.specialPurposeRooms:
                    continue
                if room.getPosition() in cityPlaner.generalPurposeRooms:
                    continue
                if (len(room.itemsOnFloor) > 13+13+11+11 or room.floorPlan or room.storageSlots or len(room.walkingSpace) > 4 or room.inputSlots):
                    continue

                quest = src.quests.questMap["DesignateRoom"](roomPosition=room.getPosition(),roomType="generalPurposeRoom",reason="reserve some room for unforseen needs")
                self.addQuest(quest)
                return True


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

        # assign basic floor plans
        if cityPlaner and cityPlaner.getAvailableRooms():
            floorPlansToSet = ["gooProcessing"]
            for room in terrain.rooms:
                if room.tag in floorPlansToSet:
                    floorPlansToSet.remove(room.tag)
            if floorPlansToSet:
                for room in cityPlaner.getAvailableRooms():
                    quest = src.quests.questMap["AssignFloorPlan"](roomPosition=room.getPosition(),floorPlanType=floorPlansToSet[0],reason="start the process of making the room useful")
                    self.addQuest(quest)
                    return True

    def checkTriggerResourceGathering(self,character,room):
        for room in [room]+character.getTerrain().rooms:
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
                        self.idleCounter = 0
                        return True

                    if source:
                        pos = source[0]
                    else:
                        pos = random.choice(character.getTerrain().scrapFields)

                    self.addQuest(src.quests.questMap["RestockRoom"](toRestock="Scrap",reason="fill scrap inputs"))
                    self.addQuest(src.quests.questMap["GoToTile"](targetPosition=(room.xPosition,room.yPosition)))
                    self.addQuest(src.quests.questMap["GatherScrap"](targetPosition=pos))
                    self.addQuest(src.quests.questMap["GoToTile"](targetPosition=pos))
                    self.idleCounter = 0
                    return True

    def checkTriggerMaggotGathering(self,character,room):
        for room in [room]+character.getTerrain().rooms:
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
                        self.idleCounter = 0
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
                    self.idleCounter = 0
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
                    self.idleCounter = 0
                    return True

    def checkTriggerHauling(self,character,room):
        checkedTypes = set()

        for trueInput in (True,False):
            for room in [room] + character.getTerrain().rooms:
                emptyInputSlots = room.getEmptyInputslots(allowStorage=(not trueInput),allowAny=True)

                if emptyInputSlots:

                    for inputSlot in random.sample(list(emptyInputSlots),len(emptyInputSlots)):
                        if inputSlot[1] == None:
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
                        if inputSlot[1]:
                            self.addQuest(src.quests.questMap["RestockRoom"](toRestock=inputSlot[1],allowAny=True,reason=reason))
                            if not character.container == room:
                                self.addQuest(src.quests.questMap["GoToTile"](targetPosition=room.getPosition()))
                        else:
                            if hasItem:
                                self.addQuest(src.quests.questMap["RestockRoom"](toRestock=character.inventory[-1].type,allowAny=True,reason=reason))
                                if not character.container == room:
                                    self.addQuest(src.quests.questMap["GoToTile"](targetPosition=room.getPosition()))
                                self.idleCounter = 0
                                return True

                        if not hasItem:
                            if trueInput:
                                self.addQuest(src.quests.questMap["FetchItems"](toCollect=inputSlot[1]))
                                self.idleCounter = 0
                                return True
                            else:
                                self.addQuest(src.quests.questMap["CleanSpace"](targetPositionBig=room.getPosition(),targetPosition=sources[0][0]))
                                self.idleCounter = 0
                                return True

        for trueInput in (True,False):
            for room in [room] + character.getTerrain().rooms:
                emptyInputSlots = room.getEmptyInputslots(allowStorage=(not trueInput),allowAny=True)

                if emptyInputSlots:

                    for inputSlot in random.sample(list(emptyInputSlots),len(emptyInputSlots)):
                        if inputSlot[1] == None:
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
                        if inputSlot[1]:
                            self.addQuest(src.quests.questMap["RestockRoom"](toRestock=inputSlot[1],allowAny=True,reason=reason))
                        else:
                            if hasItem:
                                self.addQuest(src.quests.questMap["RestockRoom"](toRestock=character.inventory[-1].type,allowAny=True,reason=reason))
                                self.idleCounter = 0
                                return True
                                

                        if not hasItem:
                            if trueInput:
                                self.addQuest(src.quests.questMap["FetchItems"](toCollect=inputSlot[1]))
                                self.idleCounter = 0
                                return True
                            else:
                                self.addQuest(src.quests.questMap["CleanSpace"](targetPositionBig=room.getPosition(),targetPosition=sources[0][0]))
                                self.idleCounter = 0
                                return True

        for room in [room] + character.getTerrain().rooms:
            for storageSlot in room.storageSlots:
                if not storageSlot[2].get("desiredState") == "filled":
                    continue

                items = room.getItemByPosition(storageSlot[0])
                if items and (not items[0].walkable or len(items) >= 20):
                    continue

                for checkStorageSlot in room.storageSlots:
                    if checkStorageSlot[1] == storageSlot[1] or not checkStorageSlot[1]:
                        items = room.getItemByPosition(checkStorageSlot[0])
                        if checkStorageSlot[2].get("desiredState") == "filled":
                            continue
                        if not items or not items[0].type == storageSlot[1]:
                            continue

                        self.addQuest(src.quests.questMap["RestockRoom"](targetPositionBig=room.getPosition(),targetPosition=storageSlot[0],allowAny=True,toRestock=items[0].type,reason="to fill a storage stockpile designated to be filled"))
                        self.addQuest(src.quests.questMap["CleanSpace"](targetPositionBig=room.getPosition(),targetPosition=checkStorageSlot[0],reason="to fill a storage stockpile designated to be filled",abortOnfullInventory=True))
                        self.idleCounter = 0
                        return True

    def checkTriggerResourceFetching(self,character,room):
        checkedTypes = set()

        for trueInput in (True,False):
            for room in [room] + character.getTerrain().rooms:
                emptyInputSlots = room.getEmptyInputslots(allowStorage=(not trueInput),allowAny=True)

                if emptyInputSlots:

                    for inputSlot in random.sample(list(emptyInputSlots),len(emptyInputSlots)):
                        if inputSlot[1] == None:
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
                            source = None
                            for candidateSource in room.sources:
                                if not candidateSource[1] == inputSlot[1]:
                                    continue

                                sourceRoom = room.container.getRoomByPosition(candidateSource[0])
                                if not sourceRoom:
                                    continue

                                sourceRoom = sourceRoom[0]
                                if sourceRoom == character.container:
                                    continue
                                if not sourceRoom.getNonEmptyOutputslots(itemType=inputSlot[1],allowStorage=trueInput):
                                    continue

                                source = candidateSource
                                break

                            if not source:
                                for otherRoom in random.sample(character.getTerrain().rooms,len(character.getTerrain().rooms)):
                                    if otherRoom == character.container:
                                        continue

                                    outputSlots = otherRoom.getNonEmptyOutputslots(itemType=inputSlot[1],allowStorage=trueInput)
                                    if not outputSlots:
                                        continue

                                    source = (otherRoom.getPosition(),inputSlot[1],outputSlots)
                                    break

                            if not source:
                                continue

                        if not hasItem:
                            if self.triggerClearInventory(character,room):
                                self.idleCounter = 0
                                return True

                        if trueInput:
                            self.addQuest(src.quests.questMap["RestockRoom"](toRestock=inputSlot[1],reason="restock the room with the items fetched"))
                        else:
                            if hasItem:
                                self.addQuest(src.quests.questMap["RestockRoom"](toRestock=character.inventory[-1].type,reason="restock the room with the items fetched",allowAny=True))
                                if not character.room == room:
                                    self.addQuest(src.quests.questMap["GoToTile"](targetPosition=room.getPosition()))
                                self.idleCounter = 0
                                return True
                        
                        if not hasItem:
                            if trueInput:
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
                            else:
                                roomPos = (room.xPosition,room.yPosition,0)
                                if not source[0] == roomPos:
                                    self.addQuest(src.quests.questMap["GoToTile"](targetPosition=roomPos))

                                self.addQuest(src.quests.questMap["CleanSpace"](targetPositionBig=source[0],targetPosition=source[2][0][0]))
                                self.idleCounter = 0
                                return True



                        self.idleCounter = 0
                        return True

        for room in [room] + character.getTerrain().rooms:
            for storageSlot in room.storageSlots:
                if not storageSlot[2].get("desiredState") == "filled":
                    continue

                items = room.getItemByPosition(storageSlot[0])
                if items and (not items[0].walkable or len(items) >= 20):
                    continue

                for otherRoom in character.getTerrain().rooms:
                    if otherRoom == room:
                        continue
                    for checkStorageSlot in otherRoom.storageSlots:
                        if checkStorageSlot[1] == storageSlot[1] or not checkStorageSlot[1]:
                            items = otherRoom.getItemByPosition(checkStorageSlot[0])
                            if checkStorageSlot[2].get("desiredState") == "filled":
                                continue
                            if not items or not items[0].type == storageSlot[1]:
                                continue

                            self.addQuest(src.quests.questMap["RestockRoom"](targetPositionBig=room.getPosition(),targetPosition=storageSlot[0],allowAny=True,toRestock=items[0].type,reason="to fill a storage stockpile designated to be filled"))
                            self.addQuest(src.quests.questMap["CleanSpace"](targetPositionBig=otherRoom.getPosition(),targetPosition=checkStorageSlot[0],reason="to fill a storage stockpile designated to be filled",abortOnfullInventory=True))
                            if character.inventory:
                                self.addQuest(src.quests.questMap["ClearInventory"]())
                            self.idleCounter = 0
                            return True

    def checkTriggerPainting(self,character,room):
        for room in [room]+character.getTerrain().rooms:
            if room.floorPlan:
                self.addQuest(src.quests.questMap["DrawFloorPlan"](targetPosition=room.getPosition()))
                self.idleCounter = 0
                return True

        # get storage stockpiles that have the filled tag
        desireFilledStorageSlots = {}
        for room in character.getTerrain().rooms:
            if not room.tag == "storage":
                continue
            for storageSlot in room.storageSlots:
                if storageSlot[2].get("desiredState") == "filled":
                    if not storageSlot[1] in desireFilledStorageSlots:
                        desireFilledStorageSlots[storageSlot[1]] = 0
                    desireFilledStorageSlots[storageSlot[1]] += 1
        print(desireFilledStorageSlots)

        # check rules to add more to be filled storage slots
        checkDesireFilledStorageSlots = [("Wall",10),("Door",5),("RoomBuilder",1),("Painter",1),("ScrapCompactor",2),("MetalBars",3),("Scrap",2)]
        for checkDesireFilledStorageSlot in checkDesireFilledStorageSlots:
            if desireFilledStorageSlots.get(checkDesireFilledStorageSlot[0],0) >= checkDesireFilledStorageSlot[1]:
                continue
            
            for room in character.getTerrain().rooms:
                if not room.tag == "storage":
                    continue
                storageSlots = room.storageSlots[:]
                random.shuffle(storageSlots)
                for storageSlot in storageSlots:
                    if storageSlot[1] or storageSlot[2]:
                        continue
                    quest = src.quests.questMap["DrawStockpile"](stockpileType="s",targetPositionBig=room.getPosition(),targetPosition=storageSlot[0],reason="designate special storage for basic items",itemType=checkDesireFilledStorageSlot[0],extraInfo={"desiredState":"filled"})
                    self.addQuest(quest)
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
                for candidate in cityPlaner.plannedRooms:
                    items = terrain.itemsByCoordinate.get((candidate[0]*15+7,candidate[1]*15+7,0))
                    if items and items[-1].type == "RoomBuilder":
                        quest = src.quests.questMap["BuildRoom"](targetPosition=candidate)
                        self.addQuest(quest)
                        self.idleCounter = 0
                        return True

                while cityPlaner.plannedRooms:
                    if terrain.getRoomByPosition(cityPlaner.plannedRooms[0]):
                        cityPlaner.plannedRooms.remove(cityPlaner.plannedRooms[0])
                        continue

                    self.addQuest(src.quests.questMap["BuildRoom"](targetPosition=cityPlaner.plannedRooms[0]))
                    self.idleCounter = 0
                    return True

        if not cityPlaner or cityPlaner.autoExtensionThreashold > 0:
            # do not build more rooms when there is an empty room
            numEmptyRooms = 0
            for room in terrain.rooms:
                if room.tag:
                    continue
                if (len(room.itemsOnFloor) > 13+13+11+11 or room.floorPlan or room.storageSlots or len(room.walkingSpace) > 4 or room.inputSlots):
                    continue
                numEmptyRooms += 1

            threashold = 1
            if cityPlaner:
                threashold = cityPlaner.autoExtensionThreashold

            if numEmptyRooms >= threashold:
                return

            baseNeighbours = []
            offsets = ((0,1,0),(1,0,0),(0,-1,0),(-1,0,0))
            for room in terrain.rooms:
                pos = room.getPosition()
                for offset in offsets:
                    checkPos = (pos[0]+offset[0],pos[1]+offset[1],0)
                    if terrain.getRoomByPosition(checkPos):
                        continue
                    if checkPos in baseNeighbours:
                        continue
                    baseNeighbours.append(checkPos)
            random.shuffle(baseNeighbours)

            possibleBuildSites = []
            for candidate in baseNeighbours:
                if (not candidate in terrain.scrapFields) and (not candidate in terrain.forests):
                    possibleBuildSites.append(candidate)

            for candidate in possibleBuildSites:
                items = terrain.itemsByCoordinate.get((candidate[0]*15+7,candidate[1]*15+7,0))
                if items and items[-1].type == "RoomBuilder":
                    quest = src.quests.questMap["BuildRoom"](targetPosition=candidate)
                    self.addQuest(quest)
                    self.idleCounter = 0
                    return True

            for candidate in possibleBuildSites:
                if len(terrain.itemsByBigCoordinate.get(candidate,[])) < 5:
                    quest = src.quests.questMap["BuildRoom"](targetPosition=candidate)
                    self.addQuest(quest)
                    self.idleCounter = 0
                    return True
            for candidate in possibleBuildSites:
                quest = src.quests.questMap["BuildRoom"](targetPosition=candidate)
                self.addQuest(quest)
                self.idleCounter = 0
                return True
        
    def checkTriggerMachinePlacing(self,character,room):
        terrain = character.getTerrain()
        cityCore = terrain.getRoomByPosition((7,7,0))[0]
        cityPlaner = cityCore.getItemByType("CityPlaner",needsBolted=True)

        if not cityPlaner:
            itemsInStorage = {}
            freeStorage = 0
            for room in character.getTerrain().rooms:
                for storageSlot in room.storageSlots:
                    items = room.getItemByPosition(storageSlot[0])
                    if not items:
                        freeStorage += 1
                    for item in items:
                        itemsInStorage[item.type] = itemsInStorage.get(item.type,0)+1
            
            if itemsInStorage.get("CityPlaner") or "metal working" in character.duties:
                quest = src.quests.questMap["PlaceItem"](targetPositionBig=(7,7,0),targetPosition=(4,1,0),itemType="CityPlaner",tryHard=True,boltDown=True,reason="to have it to plan the city with")
                self.addQuest(quest)
                return True

        for room in [room]+terrain.rooms:
            if (not room.floorPlan) and room.buildSites:
                for buildSite in room.buildSites:
                    if buildSite[1] == "Machine":
                        self.addQuest(src.quests.questMap["SetUpMachine"](itemType=buildSite[2]["toProduce"],targetPositionBig=room.getPosition(),targetPosition=buildSite[0]))
                        self.idleCounter = 0
                        return True
                checkedMaterial = set()
                for buildSite in random.sample(room.buildSites,len(room.buildSites)):
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
                            for checkRoom in random.sample(character.getTerrain().rooms,len(character.getTerrain().rooms)):
                                if not checkRoom.getNonEmptyOutputslots(itemType=neededItem):
                                    continue

                                source = (checkRoom.getPosition(),neededItem)
                                break

                        if not source:
                            if not buildSite[1] == "Machine" and "metal working" in character.duties:
                                self.addQuest(src.quests.questMap["MetalWorking"](toProduce=buildSite[1],amount=1,produceToInventory=True))
                                return True

                            character.addMessage("no machine placing - no filled output slots")
                            continue

                    if hasItem:
                        if buildSite[1] == "Command":
                            if "command" in buildSite[2]:
                                self.addQuest(src.quests.questMap["RunCommand"](command="jjssj%s\n"%(buildSite[2]["command"])))
                            else:
                                self.addQuest(src.quests.questMap["RunCommand"](command="jjssj.\n"))
                        if not character.container == room:
                            self.addQuest(src.quests.questMap["GoToTile"](targetPosition=room.getPosition()))
                            return True
                        self.addQuest(src.quests.questMap["RunCommand"](command="lcb"))
                        self.addQuest(src.quests.questMap["GoToPosition"](targetPosition=buildSite[0]))
                        buildSite[2]["reservedTill"] = room.timeIndex+100
                    elif source:
                        if not character.getFreeInventorySpace() > 0:
                            quest = src.quests.questMap["ClearInventory"]()
                            self.addQuest(quest)
                            quest.assignToCharacter(character)
                            quest.activate()
                            self.idleCounter = 0
                            return True

                        roomPos = (room.xPosition,room.yPosition)

                        if not source[0] == roomPos:
                            self.addQuest(src.quests.questMap["GoToTile"](targetPosition=(roomPos[0],roomPos[1],0)))
                        self.addQuest(src.quests.questMap["FetchItems"](toCollect=neededItem,amount=1))
                    self.idleCounter = 0
                    return True

    def checkTriggerFillFlask(self,character,room):
        if character.flask and character.flask.uses < 3:
            self.addQuest(src.quests.questMap["FillFlask"]())
            self.idleCounter = 0
            return True

    def checkTriggerScavenging(self,character,room):
        if not character.getFreeInventorySpace():
            self.addQuest(src.quests.questMap["ClearInventory"]())
            self.idleCounter = 0
            return True

        terrain = character.getTerrain()
        while terrain.collectionSpots:
            if not terrain.itemsByBigCoordinate.get(terrain.collectionSpots[-1]):
                terrain.collectionSpots.pop()
                continue
            self.addQuest(src.quests.questMap["ScavengeTile"](targetPosition=(terrain.collectionSpots[-1])))
            self.idleCounter = 0
            return True
        self.addQuest(src.quests.questMap["Scavenge"]())
        self.idleCounter = 0
        return True

    def checkTriggerEat(self,character,room):
        if character.satiation < 200:
            self.addQuest(src.quests.questMap["Eat"]())
            self.idleCounter = 0
            return True

    def triggerClearInventory(self,character,room):
        if len(character.inventory) > 9:
            self.addQuest(src.quests.questMap["ClearInventory"]())
            self.idleCounter = 0
            return True
        # clear inventory local
        if len(character.inventory) > 1 and character.container.isRoom:
            emptyInputSlots = character.container.getEmptyInputslots(character.inventory[-1].type, allowAny=True)
            if emptyInputSlots:
                self.addQuest(src.quests.questMap["RestockRoom"](toRestock=character.inventory[-1].type, allowAny=True,reason="clear your inventory"))
                self.idleCounter = 0
                return True

        # go to garbage stockpile and unload
        if len(character.inventory) > 6:
            if not "HOMEx" in character.registers:
                self.idleCounter = 0
                return True
            homeRoom = room.container.getRoomByPosition((character.registers["HOMEx"],character.registers["HOMEy"]))[0]
            if not hasattr(homeRoom,"storageRooms") or not homeRoom.storageRooms:
                return False

            quest = src.quests.questMap["GoToTile"](targetPosition=(homeRoom.storageRooms[0].xPosition,homeRoom.storageRooms[0].yPosition,0))
            self.addQuest(quest)
            quest.assignToCharacter(character)
            quest.activate()
            self.idleCounter = 0
            return True
        if len(character.inventory) > 9:
            quest = src.quests.questMap["ClearInventory"]()
            self.addQuest(quest)
            quest.assignToCharacter(character)
            quest.activate()
            self.idleCounter = 0
            return True
        return False

    def generateSubquests(self,character):

        for quest in self.subQuests:
            if quest.completed:
                self.subQuests.remove(quest)
                break

        self.triggerCompletionCheck(character)

        """
        if not self.idleCounter:
            self.checkedRoomPositions = []
        """

        try:
            self.checkedRoomPositions
        except:
            self.checkedRoomPositions = []

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

        #if character.rank == 3:
        #    self.addQuest(src.quests.questMap["ManageBase"]())
        #    return

        #if not self.strict and (self.idleCounter > 15 or (character.rank == 6 and len(character.duties) < 1) or (character.rank == 5 and len(character.duties) < 2) or (character.rank == 4 and len(character.duties) < 3) or (character.rank == 3 and len(character.duties) < 4)):
        #    quest = src.quests.questMap["ChangeJob"]()
        #    self.addQuest(quest)
        #    quest.activate()
        #    quest.assignToCharacter(character)
        #    self.idleCounter = 0
        #    return

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
                self.idleCounter = 0
                return

        room = character.container
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

            if duty == "scrap hammering":
                if self.checkTriggerScrapHammering(character,room):
                    return

            if duty == "metal working":
                if self.checkTriggerMetalWorking(character,room):
                    return

            if duty == "city planning":
                if self.checkTriggerCityPlaning(character,room):
                    return

            if duty == "clone spawning":
                if self.checkTriggerCloneSpawning(character,room):
                    return

        for room in character.getTerrain().rooms:
            if room.tag == "meetingHall":
                if not room == character.container:
                    quest = src.quests.questMap["GoToTile"](targetPosition=room.getPosition(),description="go to meeting hall")
                    self.idleCounter += 1
                    self.addQuest(quest)
                    return
                quest = src.quests.questMap["GoToPosition"](targetPosition=(random.randint(1,11),random.randint(1,11),0),description="wait for something to happen",reason="ensure nothing exciting will happening")
                self.idleCounter += 1
                self.addQuest(quest)
                character.timeTaken += self.idleCounter
                return

        if not self.targetPosition:
            self.checkedRoomPositions.append(character.getBigPosition())

            directions = [(-1,0),(1,0),(0,-1),(0,1)]
            random.shuffle(directions)
            for direction in directions:
                newPos = (room.xPosition+direction[0],room.yPosition+direction[1],0)
                if newPos in self.checkedRoomPositions:
                    continue
                if room.container.getRoomByPosition(newPos):
                    quest = src.quests.questMap["GoToTile"](targetPosition=newPos,description="look for job on tile ")
                    self.idleCounter += 1
                    self.addQuest(quest)
                    quest.assignToCharacter(character)
                    quest.activate()
                    character.runCommandString("%s."%(self.idleCounter,))
                    return

            for room in terrain.rooms:
                newPos = room.getPosition()
                if newPos in self.checkedRoomPositions:
                    continue
                quest = src.quests.questMap["GoToTile"](targetPosition=newPos,description="look for job on tile ")
                self.idleCounter += 3
                self.addQuest(quest)
                quest.assignToCharacter(character)
                quest.activate()
                character.runCommandString("%s."%(self.idleCounter,))
                return

            self.checkedRoomPositions = []
            self.idleCounter += 10
            character.runCommandString("20.")
            return

        self.idleCounter += 5
        character.runCommandString("20.")

src.quests.addType(BeUsefull)

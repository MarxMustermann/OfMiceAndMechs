import logging
import random

import src

logger = logging.getLogger(__name__)

class BeUsefull(src.quests.MetaQuestSequence):
    type = "BeUsefull"

    def __init__(self, description="be useful", creator=None, targetPosition=None, strict=False, reason=None, endOnIdle=False,numTasksToDo=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description

        self.targetPosition = None
        self.idleCounter = 0
        self.numTasksToDo = numTasksToDo
        self.numTasksDone = 0
        if targetPosition:
            self.setParameters({"targetPosition":targetPosition})

        self.shortCode = " "
        self.strict = strict

        self.checkedRoomPositions = []
        self.reason = reason
        self.endOnIdle = endOnIdle

    def generateTextDescription(self):
        reason = ""
        if self.reason:
            reason = f", to {self.reason}"
        out = """
Be useful{}.

Try fulfill your duties on this base with the skills you have.

Your duties are:

{}


""".format(reason,"\n".join(self.character.duties),)
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
Recharge them with lightning rods.
Reputation is rewarded for recharging trap rooms.\n\n"""
                elif duty == "cleaning":
                    out += duty+""":
Search for rooms with items cluttering the floor.
Remove those items.
Reputation is rewarded for picking up items from walkways.\n\n"""
                else:
                    out += f"{duty}\n\n"

        if self.character.rank != 3:
            reputationForPromotion = "???"
            if self.character.rank == 6:
                reputationForPromotion = 300
            if self.character.rank == 5:
                reputationForPromotion = 500
            if self.character.rank == 4:
                reputationForPromotion = 750

            out += f"{self.idleCounter}"

            out += f"""

You need {reputationForPromotion} reputation for a promotion.
You currently have {self.character.reputation} reputation.
Do your duty to gain more reputation.
Try to avoid losing reputation due to being careless.

"""

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
        if extraInfo["deadChar"].faction != self.character.faction:
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
        if self.character != src.gamestate.gamestate.mainChar:
            return

        if isinstance(self.character.container,src.terrains.Terrain):
            if "resource gathering" in self.character.duties:
                self.character.awardReputation(1, reason="gathering an item")
        else:
            room = self.character.container
            if "cleaning" in self.character.duties and extraInfo[2] in room.walkingSpace:
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

        if character.health > character.maxHealth//5:
            if (not len(self.subQuests) or not isinstance(self.subQuests[0],src.quests.questMap["Fight"])) and character.getNearbyEnemies():
                quest = src.quests.questMap["Fight"]()
                self.addQuest(quest)
                quest.activate()
                quest.assignToCharacter(character)
                return

        character.timeTaken += 0.1
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
        if hasattr(room,"electricalCharges") and room.electricalCharges < room.maxElectricalCharges:

            quest = src.quests.questMap["ReloadTraproom"](targetPosition=room.getPosition())
            self.addQuest(quest)
            quest.activate()
            self.idleCounter = 0
            return True
        return None

    def checkTriggerTurretLoading(self,character,room):
        return None

    def checkTriggerMachineOperation(self,character,currentRoom):
        terrain = character.getTerrain()
        for checkRoom in self.getRandomPriotisedRooms(character,currentRoom):
            items = checkRoom.itemsOnFloor[:]
            random.shuffle(items)
            for item in items:
                #if not item.bolted:
                #    continue
                if item.type not in ("Machine","ScrapCompactor","MaggotFermenter","BioPress","GooProducer","Electrifier",):
                    continue
                if not item.readyToUse():
                    continue
                if checkRoom == character.container:
                    quest = src.quests.questMap["OperateMachine"](targetPosition=item.getPosition())
                    self.addQuest(quest)
                    quest.activate()
                    self.idleCounter = 0
                    return True
                else:
                    quest = src.quests.questMap["GoToTile"](targetPosition=checkRoom.getPosition(),reason="go to a machine room")
                    self.addQuest(quest)
                    quest.activate()
                    self.idleCounter = 0
                    return True
        return None

    def checkTriggerManufacturing(self,character,currentRoom):
        terrain = character.getTerrain()
        for checkRoom in self.getRandomPriotisedRooms(character,currentRoom):
            items = checkRoom.itemsOnFloor[:]
            random.shuffle(items)
            for item in items:
                if not item.bolted:
                    continue
                if item.type not in ("ManufacturingTable",):
                    continue
                if not item.readyToUse():
                    continue
                if not item.isOutputEmpty():
                    continue

                if checkRoom == character.container:
                    quest = src.quests.questMap["Manufacture"](targetPosition=item.getPosition())
                    self.addQuest(quest)
                    quest.activate()
                    self.idleCounter = 0
                    return True
                else:
                    quest = src.quests.questMap["GoToTile"](targetPosition=checkRoom.getPosition(),reason="go to a machine room")
                    self.addQuest(quest)
                    quest.activate()
                    self.idleCounter = 0
                    return True
        for checkRoom in self.getRandomPriotisedRooms(character,currentRoom):
            items = checkRoom.itemsOnFloor[:]
            random.shuffle(items)
            for item in items:
                if not item.bolted:
                    continue
                if item.type not in ("ManufacturingTable",):
                    continue
                if not item.readyToUse():
                    continue

                if checkRoom == character.container:
                    quest = src.quests.questMap["Manufacture"](targetPosition=item.getPosition())
                    self.addQuest(quest)
                    quest.activate()
                    self.idleCounter = 0
                    return True
                else:
                    quest = src.quests.questMap["GoToTile"](targetPosition=checkRoom.getPosition(),reason="go to a machine room")
                    self.addQuest(quest)
                    quest.activate()
                    self.idleCounter = 0
                    return True
        return None

    def checkTriggerScrapHammering(self,character,currentRoom):
        for room in self.getRandomPriotisedRooms(character,currentRoom):
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

        if freeStorage and itemsInStorage.get("MetalBars",0) < 40:
            self.addQuest(src.quests.questMap["ScrapHammering"](amount=10))
            self.idleCounter = 0
            return True
        return None

    def checkTriggerMetalWorking(self,character,currentRoom):
        freeMetalWorkingBenches = []

        for room in self.getRandomPriotisedRooms(character,currentRoom):
            for metalWorkingBench in room.getItemsByType("MetalWorkingBench"):
                if not metalWorkingBench.readyToUse():
                    continue

                freeMetalWorkingBenches.append(metalWorkingBench)

        random.shuffle(freeMetalWorkingBenches)
        for metalWorkingBench in freeMetalWorkingBenches:
            if metalWorkingBench.scheduledItems:
                self.addQuest(src.quests.questMap["ClearInventory"]())
                self.addQuest(src.quests.questMap["MetalWorking"](amount=1,toProduce=metalWorkingBench.scheduledItems[0]))
                self.idleCounter = 0
                return True

        if not freeMetalWorkingBenches:
            return

        itemsInStorage = {}
        freeStorage = 0
        for room in character.getTerrain().rooms:
            for storageSlot in room.storageSlots:
                items = room.getItemByPosition(storageSlot[0])
                if not items:
                    freeStorage += 1
                for item in items:
                    itemsInStorage[item.type] = itemsInStorage.get(item.type,0)+1
            for outputSlot in room.outputSlots:
                items = room.getItemByPosition(outputSlot[0])
                for item in items:
                    itemsInStorage[item.type] = itemsInStorage.get(item.type,0)+1

        if freeStorage:

            for room in character.getTerrain().rooms:
                for buildSite in room.buildSites:
                    if buildSite[1] == "Machine":
                        continue
                    if buildSite[1] in itemsInStorage:
                        continue
                    self.addQuest(src.quests.questMap["ClearInventory"](returnToTile=False))
                    newQuest = src.quests.questMap["MetalWorking"](toProduce=buildSite[1],amount=1,produceToInventory=False)
                    self.addQuest(newQuest)
                    return True

            checkItems = [("RoomBuilder",1,1),("Door",1,1),("Wall",1,1),("Painter",1,1),("ScrapCompactor",1,1),("Case",1,1),("Frame",1,1),("Rod",1,1),("MaggotFermenter",1,1),("Sword",1,1),("Armor",1,1),("Bolt",10,5),("Vial",1,1),("CoalBurner",1,1),("BioPress",1,1),("GooProducer",1,1),("GooDispenser",1,1),("VialFiller",1,1),("Door",4,1),("Painter",2,1),("Wall",10,3),("ScrapCompactor",2,1)]
            for checkItem in checkItems:
                if itemsInStorage.get(checkItem[0],0) < checkItem[1]:
                    self.addQuest(src.quests.questMap["ClearInventory"](returnToTile=False))
                    self.addQuest(src.quests.questMap["MetalWorking"](amount=checkItem[2],toProduce=checkItem[0]))
                    self.idleCounter = 0
                    return True
            return None
        return None

    def checkTriggerMachining(self,character,currentRoom):
        for room in self.getRandomPriotisedRooms(character,currentRoom):
            for machiningTable in room.getItemsByType("MachiningTable"):
                if machiningTable.scheduledItems:
                    self.addQuest(src.quests.questMap["ClearInventory"]())
                    self.addQuest(src.quests.questMap["Machining"](amount=1,toProduce=machiningTable.scheduledItems[0]))
                    self.idleCounter = 0
                    return True

        machinesInStorage = {}
        for room in self.getRandomPriotisedRooms(character,currentRoom):
            for storageSlot in room.storageSlots:
                items = room.getItemByPosition(storageSlot[0])
                for item in items:
                    if item.type != "Machine":
                        continue
                    machinesInStorage[item.toProduce] = machinesInStorage.get(item.toProduce,0)+1
            for outputSlot in room.outputSlots:
                items = room.getItemByPosition(outputSlot[0])
                for item in items:
                    if item.type != "Machine":
                        continue
                    machinesInStorage[item.toProduce] = machinesInStorage.get(item.toProduce,0)+1

        for room in self.getRandomPriotisedRooms(character,currentRoom):
            for buildSite in random.sample(room.buildSites,len(room.buildSites)):
                if buildSite[1] != "Machine":
                    continue
                if buildSite[2]["toProduce"] in machinesInStorage:
                    continue
                self.addQuest(src.quests.questMap["ClearInventory"]())
                newQuest = src.quests.questMap["Machining"](toProduce=buildSite[2]["toProduce"],amount=1,produceToInventory=False)
                self.addQuest(newQuest)
                return True

        itemsToCheck = ["Wall","Case","Frame","Rod","Door","RoomBuilder","ScrapCompactor","Sword","Armor"]
        for itemType in itemsToCheck:
            if itemType not in machinesInStorage:
                self.addQuest(src.quests.questMap["ClearInventory"]())
                newQuest = src.quests.questMap["Machining"](toProduce=itemType,amount=1,produceToInventory=False)
                self.addQuest(newQuest)
                return True
        return None

    def checkTriggerCloneSpawning(self,character,currentRoom):
        terrain = character.getTerrain()

        foundShrine = None
        for room in self.getRandomPriotisedRooms(character,currentRoom):
            for checkShrine in room.getItemsByType("Shrine"):
                if checkShrine.god != 1:
                    continue
                foundShrine = checkShrine

        if not foundShrine:
            return False

        # gather npc duties
        npcDuties = {}
        for otherChar in terrain.characters:
            if not otherChar.burnedIn:
                continue
            for duty in otherChar.duties:
                if otherChar == character:
                    continue
                if duty not in npcDuties:
                    npcDuties[duty] = []
                npcDuties[duty].append(otherChar)
        for checkRoom in character.getTerrain().rooms:
            for otherChar in checkRoom.characters:
                if not otherChar.burnedIn:
                    continue
                if otherChar == character:
                    continue
                for duty in otherChar.duties:
                    if duty not in npcDuties:
                        npcDuties[duty] = []
                    npcDuties[duty].append(otherChar)

        chargesUsed = 0
        quests = []
        for duty in ["room building","cleaning","scavenging","manufacturing","resource gathering","scrap hammering","hauling","metal working","resource fetching","painting","machining","machine placing","machine operation","maggot gathering",]:

            if duty not in npcDuties:
                cost = foundShrine.getBurnedInCharacterSpawningCost(character)
                cost *= foundShrine.get_glass_heart_rebate()
                foundFlask = None
                for item in character.inventory:
                    if item.type != "GooFlask":
                        continue
                    if item.uses < 100:
                        continue
                    foundFlask = item
                if foundFlask:
                    cost /= 2
                cost += chargesUsed

                if character.getTerrain().mana >= cost:
                    quest = src.quests.questMap["GetEpochReward"](rewardType="spawn "+duty+" NPC",reason="spawn another clone to help you out")
                    chargesUsed += 10
                    quests.append(quest)
                    break

        for quest in reversed(quests):
            self.addQuest(quest)
        if quests:
            return True
        return None

    def checkTriggerCityPlaning(self,character,room):
        terrain = character.getTerrain()
        cityCore = terrain.getRoomByPosition((7,7,0))[0]
        cityPlaner = cityCore.getItemByType("CityPlaner",needsBolted=True)
        #epochArtwork = cityCore.getItemByType("EpochArtwork",needsBolted=True)

        #if epochArtwork.recalculateGlasstears(character,dryRun=True):
        #    quest = src.quests.questMap["GetEpochEvaluation"](reason="collect the glass tears you earned")
        #    self.addQuest(quest)
        #    return True

        # do inventory of scrap fields
        numItemsScrapfield = 0
        for scrapField in terrain.scrapFields:
            numItemsScrapfield += len(terrain.itemsByBigCoordinate.get(scrapField,[]))

        if numItemsScrapfield < 100 and terrain.mana >= 20:
            quest = src.quests.questMap["GetEpochReward"](rewardType="spawn scrap",reason="ensure enough scrap is available")
            self.addQuest(quest)

            if numItemsScrapfield < 50 and terrain.mana >= 40:
                quest = src.quests.questMap["GetEpochReward"](rewardType="spawn scrap",reason="ensure enough scrap is available")
                self.addQuest(quest)
            return True

        if not cityPlaner:
            quest = src.quests.questMap["PlaceItem"](targetPositionBig=(7,7,0),targetPosition=(4,1,0),itemType="CityPlaner",tryHard=True,boltDown=True,reason="be able to plan city expansion")
            self.addQuest(quest)
            return True

        numEmptyRooms = 0
        for room in terrain.rooms:
            if room.tag:
                continue
            if (len(room.itemsOnFloor) > 13+13+11+11 or room.floorPlan or room.storageSlots or len(room.walkingSpace) > 4 or room.inputSlots or room.buildSites):
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
                if (len(room.itemsOnFloor) > 13+13+11+11 or room.floorPlan or room.storageSlots or len(room.walkingSpace) > 4 or room.inputSlots or room.buildSites):
                    continue

                quest = src.quests.questMap["DesignateRoom"](roomPosition=room.getPosition(),roomType="generalPurposeRoom",reason="reserve some room for unforeseen needs")
                self.addQuest(quest)
                return True

        # add storage room if needed
        if cityPlaner and cityPlaner.getAvailableRooms():
            # count empty storage slots
            numFreeStorage = 0
            for room in terrain.rooms:
                for storageSlot in room.storageSlots:
                    if storageSlot[1] is not None:
                        continue
                    items = room.getItemByPosition(storageSlot[0])
                    if items:
                        continue
                    numFreeStorage += 1

            if numFreeStorage < 20:
                quest = src.quests.questMap["AssignFloorPlan"](roomPosition=cityPlaner.getAvailableRooms()[0].getPosition(),floorPlanType="storage",reason="increase storage")
                self.addQuest(quest)
                return True

        if cityPlaner and not cityPlaner.generalPurposeRooms:
            for room in terrain.rooms:
                if room.getPosition() == (7,0,0):
                    continue
                if room.getPosition() in cityPlaner.specialPurposeRooms:
                    continue
                if room.getPosition() in cityPlaner.generalPurposeRooms:
                    continue
                if (len(room.itemsOnFloor) > 13+13+11+11 or room.floorPlan or room.storageSlots or len(room.walkingSpace) > 4 or room.inputSlots or room.buildSites):
                    continue

                quest = src.quests.questMap["DesignateRoom"](roomPosition=room.getPosition(),roomType="generalPurposeRoom",reason="reserve some room for unforeseen needs")
                self.addQuest(quest)
                return True

        foundEnemies = False
        for checkCharacter in terrain.characters:
            if checkCharacter.faction == character.faction:
                continue
            foundEnemies = True

        if not foundEnemies:
            hasTemple = False
            for room in terrain.rooms:
                if room.tag != "temple":
                    continue
                hasTemple = True

            if not hasTemple:
                for room in cityPlaner.getAvailableRooms():
                    quest = src.quests.questMap["AssignFloorPlan"](roomPosition=room.getPosition(),floorPlanType="temple",reason="have a temple to place glass hearts")
                    self.addQuest(quest)
                    return True

        """
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
        """

        # assign basic floor plans
        if cityPlaner and cityPlaner.getAvailableRooms():
            floorPlansToSet = ["gooProcessing","manufacturingHall","weaponProduction","smokingRoom","wallProduction","scrapCompactor","caseProduction","basicRoombuildingItemsProduction","basicMaterialsProduction"]
            for room in terrain.rooms:
                if room.tag in floorPlansToSet:
                    floorPlansToSet.remove(room.tag)
            if floorPlansToSet:
                for room in cityPlaner.getAvailableRooms():
                    quest = src.quests.questMap["AssignFloorPlan"](roomPosition=room.getPosition(),floorPlanType=random.choice(floorPlansToSet),reason="start the process of making the room useful")
                    self.addQuest(quest)
                    return True
                return None
            return None
        return None

    def getRandomPriotisedRooms(self,character,currentRoom):
        prioSortedRooms = {}

        for room in character.getTerrain().rooms:
            try:
                room.alarm
            except:
                room.alarm = False
            if room.alarm:
                continue
            if not room.priority in prioSortedRooms:
                prioSortedRooms[room.priority] = []
            prioSortedRooms[room.priority].append(room)

        for roomList in prioSortedRooms.values():
            random.shuffle(roomList)

        resultList = []
        for key in reversed(sorted(prioSortedRooms.keys())):
            resultList.extend(prioSortedRooms[key])

        return resultList

    def checkTriggerResourceGathering(self,character,currentRoom):
        terrain = character.getTerrain()
        try:
            terrain.alarm
        except:
            terrain.alarm = False
        if terrain.alarm:
            return None

        for room in self.getRandomPriotisedRooms(character,currentRoom):
            emptyInputSlots = room.getEmptyInputslots(itemType="Scrap")
            if emptyInputSlots:
                for inputSlot in emptyInputSlots:
                    if inputSlot[1] != "Scrap":
                        continue

                    source = None
                    if room.sources:
                        for potentialSource in random.sample(list(room.sources),len(room.sources)):
                            if potentialSource[1] == "rawScrap":
                                source = potentialSource
                                break

                    if source is None and not character.getTerrain().scrapFields:
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
        return None

    def checkTriggerMaggotGathering(self,character,currentRoom):
        terrain = character.getTerrain()
        if terrain.alarm:
            return None
        for room in self.getRandomPriotisedRooms(character,currentRoom):
            emptyInputSlots = room.getEmptyInputslots(itemType="VatMaggot")
            if emptyInputSlots:
                for inputSlot in emptyInputSlots:
                    if inputSlot[1] != "VatMaggot":
                        continue

                    source = None
                    if room.sources:
                        for potentialSource in random.sample(list(room.sources),len(room.sources)):
                            if potentialSource[1] == "rawVatMaggots":
                                source = potentialSource
                                break

                    if source is None and not character.getTerrain().forests:
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
        return None

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

    def checkTriggerCleaning(self,character,currentRoom):
        if len(character.inventory):
            quest = src.quests.questMap["ClearInventory"]()
            self.addQuest(quest)
            self.idleCounter = 0
            return True

        for room in self.getRandomPriotisedRooms(character,currentRoom):
            foundEnemy = False
            for otherChar in room.characters:
                if not otherChar.faction == character.faction:
                    foundEnemy = True
                    break
            if foundEnemy:
                continue

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

        for room in self.getRandomPriotisedRooms(character,currentRoom):
            foundEnemy = False
            for otherChar in room.characters:
                if not otherChar.faction == character:
                    foundEnemy = True
                    break
            if foundEnemy:
                continue

            slots = room.inputSlots+room.outputSlots+room.storageSlots
            random.shuffle(slots)
            for slot in slots:
                if not slot[1]:
                    continue
                items = room.getItemByPosition(slot[0])
                if not items:
                    continue

                misplacmentFound = False
                for item in items:
                    if not item.type == slot[1]:
                        misplacmentFound = True

                if not misplacmentFound:
                    continue

                self.addQuest(src.quests.questMap["CleanSpace"](targetPositionBig=room.getPosition(),targetPosition=slot[0]))
                self.idleCounter = 0
                return True

        return None

    def checkTriggerHauling(self,character,currentRoom):
        checkedTypes = set()
        rooms = character.getTerrain().rooms[:]
        random.shuffle(rooms)

        for trueInput in (True,False):
            for room in self.getRandomPriotisedRooms(character,currentRoom):
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
                        if inputSlot[1]:
                            self.addQuest(src.quests.questMap["RestockRoom"](toRestock=inputSlot[1],allowAny=True,reason=reason,targetPosition=inputSlot[0]))
                            if character.container != room:
                                self.addQuest(src.quests.questMap["GoToTile"](targetPosition=room.getPosition()))
                        else:
                            if hasItem:
                                self.addQuest(src.quests.questMap["RestockRoom"](toRestock=character.inventory[-1].type,allowAny=True,reason=reason,targetPosition=inputSlot[0]))
                                if character.container != room:
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
            for room in self.getRandomPriotisedRooms(character,currentRoom):
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

        for room in self.getRandomPriotisedRooms(character,currentRoom):
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

                        self.addQuest(src.quests.questMap["RestockRoom"](targetPositionBig=room.getPosition(),targetPosition=storageSlot[0],allowAny=True,toRestock=items[0].type,reason="fill a storage stockpile designated to be filled"))
                        self.addQuest(src.quests.questMap["CleanSpace"](targetPositionBig=room.getPosition(),targetPosition=checkStorageSlot[0],reason="to get the items to fill a storage stockpile designated to be filled",abortOnfullInventory=True))
                        self.idleCounter = 0
                        return True
        return None

    def checkTriggerResourceFetching(self,character,currentRoom):

        for trueInput in (True,False):
            for room in self.getRandomPriotisedRooms(character,currentRoom):
                checkedTypes = set()
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
                            allowStorage = trueInput
                            if inputSlot[2].get("desiredState") == "filled":
                                allowStorage = True

                            source = None
                            for candidateSource in room.sources:
                                if candidateSource[1] != inputSlot[1]:
                                    continue

                                sourceRoom = room.container.getRoomByPosition(candidateSource[0])
                                if not sourceRoom:
                                    continue

                                sourceRoom = sourceRoom[0]
                                if sourceRoom == character.container:
                                    continue
                                if not sourceRoom.getNonEmptyOutputslots(itemType=inputSlot[1],allowStorage=allowStorage):
                                    continue

                                source = candidateSource
                                break

                            if not source:
                                for otherRoom in random.sample(character.getTerrain().rooms,len(character.getTerrain().rooms)):
                                    if otherRoom == room:
                                        continue

                                    outputSlots = otherRoom.getNonEmptyOutputslots(itemType=inputSlot[1],allowStorage=allowStorage,)
                                    if not outputSlots:
                                        continue

                                    source = (otherRoom.getPosition(),inputSlot[1],outputSlots)
                                    break

                            if not source:
                                continue

                        if not hasItem and self.triggerClearInventory(character,room):
                            self.idleCounter = 0
                            return True

                        if trueInput:
                            self.addQuest(src.quests.questMap["RestockRoom"](toRestock=inputSlot[1],reason="restock the room with the items fetched1",allowAny=True,targetPositionBig=room.getPosition()))
                        else:
                            if hasItem:
                                self.addQuest(src.quests.questMap["RestockRoom"](toRestock=character.inventory[-1].type,reason="restock the room with the items fetched2",allowAny=True,targetPositionBig=room.getPosition()))
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
                                if source[0] != roomPos:
                                    self.addQuest(src.quests.questMap["GoToTile"](targetPosition=roomPos))

                                self.addQuest(src.quests.questMap["FetchItems"](toCollect=inputSlot[1], amount=amountToFetch))
                                if source[0] != roomPos:
                                    self.addQuest(src.quests.questMap["GoToTile"](targetPosition=(source[0])))

                                if character.inventory and (not amountToFetch or amountToFetch > character.getFreeInventorySpace()):
                                    self.addQuest(src.quests.questMap["ClearInventory"](returnToTile=False))
                            else:
                                roomPos = (room.xPosition,room.yPosition,0)
                                if source[0] != roomPos:
                                    self.addQuest(src.quests.questMap["GoToTile"](targetPosition=roomPos))

                                self.addQuest(src.quests.questMap["CleanSpace"](targetPositionBig=source[0],targetPosition=source[2][0][0]))
                                self.idleCounter = 0
                                return True



                        self.idleCounter = 0
                        return True

        for room in self.getRandomPriotisedRooms(character,currentRoom):
            checkedTypes = set()
            for storageSlot in room.storageSlots:
                if storageSlot[2].get("desiredState") != "filled":
                    continue

                items = room.getItemByPosition(storageSlot[0])
                if items and (not items[0].walkable or len(items) >= 20):
                    continue

                for otherRoom in self.getRandomPriotisedRooms(character,currentRoom):
                    if otherRoom == room:
                        continue
                    for checkStorageSlot in otherRoom.storageSlots:
                        if checkStorageSlot[1] == storageSlot[1] or not checkStorageSlot[1]:
                            items = otherRoom.getItemByPosition(checkStorageSlot[0])
                            if checkStorageSlot[2].get("desiredState") == "filled":
                                continue
                            if not items or items[0].type != storageSlot[1]:
                                continue

                            self.addQuest(src.quests.questMap["RestockRoom"](targetPositionBig=room.getPosition(),targetPosition=storageSlot[0],allowAny=True,toRestock=items[0].type,reason="fill a storage stockpile designated to be filled"))
                            self.addQuest(src.quests.questMap["CleanSpace"](targetPositionBig=otherRoom.getPosition(),targetPosition=checkStorageSlot[0],reason="fill a storage stockpile designated to be filled",abortOnfullInventory=True))
                            if character.inventory:
                                self.addQuest(src.quests.questMap["ClearInventory"]())
                            self.idleCounter = 0
                            return True
        return None

    def checkTriggerPainting(self,character,currentRoom):
        for room in self.getRandomPriotisedRooms(character,currentRoom):
            if room.floorPlan:
                self.addQuest(src.quests.questMap["DrawFloorPlan"](targetPosition=room.getPosition()))
                self.idleCounter = 0
                return True

        terrain = character.getTerrain()
        numFreeStorage = 0
        for room in terrain.rooms:
            for storageSlot in room.storageSlots:
                items = room.getItemByPosition(storageSlot[0])
                if items:
                    continue
                if storageSlot[1] is not None:
                    continue
                if storageSlot[2] != {}:
                    continue
                numFreeStorage += 1

        if numFreeStorage < 10:
            cityPlaner = None
            rooms = terrain.getRoomByPosition((7,7,0))
            if rooms:
                room = rooms[0]
                cityPlaner = room.getItemByType("CityPlaner")

            if cityPlaner:
                for generalPurposeRoom in cityPlaner.generalPurposeRooms:

                    terrain = self.character.getTerrain()
                    room = terrain.getRoomByPosition(generalPurposeRoom)[0]
                    counter = 1
                    quests = []
                    for y in (1,3,5,7,9,11):
                        for x in range(1,12):
                            if x == 6:
                                continue
                            if counter > 15:
                                continue

                            if room.getItemByPosition((x,y,0)):
                                continue

                            if (x,y,0) in room.walkingSpace:
                                continue

                            blockedSpot = False
                            for storageSlot in room.storageSlots:
                                if storageSlot[0] == (x,y,0):
                                    blockedSpot = True
                                    break
                            for outputSlot in room.outputSlots:
                                if outputSlot[0] == (x,y,0):
                                    blockedSpot = True
                                    break
                            for inputSlot in room.inputSlots:
                                if inputSlot[0] == (x,y,0):
                                    blockedSpot = True
                                    break
                            for buildSite in room.buildSites:
                                if buildSite[0] == (x,y,0):
                                    blockedSpot = True
                                    break
                            if blockedSpot:
                                continue

                            counter += 1
                            quest = src.quests.questMap["DrawStockpile"](tryHard=True,itemType=None,stockpileType="s",targetPositionBig=generalPurposeRoom,targetPosition=(x,y,0),reason="extend the storage capacity temporarily")
                            quests.append(quest)

                    for quest in reversed(quests):
                        self.addQuest(quest)
                    if quests:
                        return True

        # get storage stockpiles that have the filled tag
        desireFilledStorageSlots = {}
        for room in character.getTerrain().rooms:
            if room.tag != "storage":
                continue
            for storageSlot in room.storageSlots:
                if storageSlot[2].get("desiredState") == "filled":
                    if storageSlot[1] not in desireFilledStorageSlots:
                        desireFilledStorageSlots[storageSlot[1]] = 0
                    desireFilledStorageSlots[storageSlot[1]] += 1


        # check rules to add more to be filled storage slots
        checkDesireFilledStorageSlots = [("Wall",10),("Door",5),("MetalBars",3)]
        for checkDesireFilledStorageSlot in checkDesireFilledStorageSlots:
            if desireFilledStorageSlots.get(checkDesireFilledStorageSlot[0],0) >= checkDesireFilledStorageSlot[1]:
                continue

            for room in self.getRandomPriotisedRooms(character,currentRoom):
                if room.tag != "storage":
                    continue
                storageSlots = room.storageSlots[:]
                random.shuffle(storageSlots)
                for storageSlot in storageSlots:
                    if storageSlot[1] or storageSlot[2]:
                        continue
                    if room.getItemByPosition(storageSlot[0]):
                        continue
                    quest = src.quests.questMap["DrawStockpile"](stockpileType="s",targetPositionBig=room.getPosition(),targetPosition=storageSlot[0],reason="designate special storage for basic items",itemType=checkDesireFilledStorageSlot[0],extraInfo={"desiredState":"filled"})
                    self.addQuest(quest)
                    return True
        return None


    def checkTriggerRoomBuilding(self,character,room):
        #src.gamestate.gamestate.mainChar = character
        terrain = character.getTerrain()
        try:
            terrain.alarm
        except:
            terrain.alarm = False
        if terrain.alarm:
            return None

        for x in range(1,13):
            for y in range(1,13):
                items = terrain.getItemByPosition((x*15+7,y*15+7,0))
                if items and items[0].type == "RoomBuilder":
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
                if (len(room.itemsOnFloor) > 13+13+11+11 or room.floorPlan or room.storageSlots or len(room.walkingSpace) > 4 or room.inputSlots or room.buildSites):
                    continue
                numEmptyRooms += 1

            threashold = 1
            if cityPlaner:
                threashold = cityPlaner.autoExtensionThreashold

            if numEmptyRooms >= threashold:
                return None

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
                if (candidate not in terrain.scrapFields) and (candidate not in terrain.forests):
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
            return None
        return None

    def registerDutyFail(self,extraParam):
        if isinstance(extraParam["quest"],src.quests.questMap["SetUpMachine"]):
            grievance = ("SetUpMachine",extraParam["quest"].itemType,"no machine")
            self.character.addGrievance(grievance)

    def findSource(self,character,currentRoom):
        source = None
        for candidateSource in room.sources:
            if candidateSource[1] != inputSlot[1]:
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

        return source

    def checkTriggerMachinePlacing(self,character,currentRoom):
        terrain = character.getTerrain()
        produceQuest = None
        for room in self.getRandomPriotisedRooms(character,currentRoom):
            if (not room.floorPlan) and room.buildSites:
                checkedMaterial = set()
                for buildSite in random.sample(room.buildSites,len(room.buildSites)):
                    if buildSite[1] in checkedMaterial:
                        continue
                    checkedMaterial.add(buildSite[1])

                    if buildSite[1] == "Machine":
                        lastCheck = character.grievances.get(("SetUpMachine",buildSite[2]["toProduce"],"no machine"),0)
                        if lastCheck+10 > src.gamestate.gamestate.tick:
                            continue

                    neededItem = buildSite[1]
                    if buildSite[1] == "Command":
                        neededItem = "Sheet"
                    hasItem = False
                    source = None
                    if character.inventory and character.inventory[-1].type == neededItem:
                        hasItem = True

                    if buildSite[1] == "Machine":
                        quest = src.quests.questMap["SetUpMachine"](itemType=buildSite[2]["toProduce"],targetPositionBig=room.getPosition(),targetPosition=buildSite[0])
                        self.addQuest(quest)
                        self.startWatching(quest,self.registerDutyFail,"failed")
                        self.idleCounter = 0
                        return True


                    if not hasItem:
                        for candidateSource in room.sources:
                            if candidateSource[1] != neededItem:
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
                            continue
                        """
                        if not source:
                            if buildSite[1] not in ("Machine","Command") and "metal working" in character.duties:
                                self.addQuest(src.quests.questMap["PlaceItem"](itemType=buildSite[1],targetPositionBig=room.getPosition(),targetPosition=buildSite[0],boltDown=True))
                                self.idleCounter = 0
                                return True

                            if buildSite[1] == "Machine":
                                self.addQuest(src.quests.questMap["SetUpMachine"](itemType=buildSite[2]["toProduce"],targetPositionBig=room.getPosition(),targetPosition=buildSite[0]))
                                self.idleCounter = 0
                                return True

                            continue
                        """

                    if buildSite[1] != "Command":
                        self.addQuest(src.quests.questMap["PlaceItem"](itemType=buildSite[1],targetPositionBig=room.getPosition(),targetPosition=buildSite[0],boltDown=True))
                        self.idleCounter = 0
                        return True

                    if hasItem:
                        if buildSite[1] == "Command":
                            if "command" in buildSite[2]:
                                self.addQuest(src.quests.questMap["RunCommand"](command="jjssj%s\n"%(buildSite[2]["command"])))
                            else:
                                self.addQuest(src.quests.questMap["RunCommand"](command="jjssj.\n"))
                        self.addQuest(src.quests.questMap["RunCommand"](command="lcb"))
                        self.addQuest(src.quests.questMap["GoToPosition"](targetPosition=buildSite[0]))
                        buildSite[2]["reservedTill"] = room.timeIndex+100
                        self.addQuest(src.quests.questMap["GoToTile"](targetPosition=room.getPosition()))
                        #self.addQuest(produceQuest)
                        self.idleCounter = 0
                        return True
                    elif source:
                        if not character.getFreeInventorySpace() > 0:
                            quest = src.quests.questMap["ClearInventory"]()
                            self.addQuest(quest)
                            quest.assignToCharacter(character)
                            quest.activate()
                            self.idleCounter = 0
                            return True

                        roomPos = (room.xPosition,room.yPosition)

                        if source[0] != roomPos:
                            self.addQuest(src.quests.questMap["GoToTile"](targetPosition=(roomPos[0],roomPos[1],0)))
                        self.addQuest(src.quests.questMap["FetchItems"](toCollect=neededItem,amount=1))
                        self.idleCounter = 0
                        return True

        # spawn city planer if there is none
        terrain = character.getTerrain()
        cityCore = terrain.getRoomByPosition((7,7,0))[0]
        cityPlaner = cityCore.getItemByType("CityPlaner",needsBolted=True)

        """
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
                quest = src.quests.questMap["PlaceItem"](targetPositionBig=(7,7,0),targetPosition=(4,1,0),itemType="CityPlaner",tryHard=True,boltDown=True,reason="have it to plan the city with")
                self.addQuest(quest)
                return True
        """

        # spawn basic items, if not there
        foundPlacedItems = {}
        foundPlacedMachines = {}
        terrain = character.getTerrain()
        for room in terrain.rooms:
            for item in room.itemsOnFloor:
                if not item.bolted:
                    continue

                if item.type not in foundPlacedItems:
                    foundPlacedItems[item.type] = []
                foundPlacedItems[item.type].append(item)

        if cityPlaner:
            checkItems = ["ScrapCompactor","MaggotFermenter","BioPress","GooProducer"]
            checkItems = ["ScrapCompactor"]
            for checkItem in checkItems:
                if checkItem in foundPlacedItems:
                    continue

                for generalPurposeRoom in cityPlaner.generalPurposeRooms:

                    terrain = self.character.getTerrain()
                    room = terrain.getRoomByPosition(generalPurposeRoom)[0]

                    validTargetPosition = False
                    terrain = character.getTerrain()
                    counter = 0
                    while not validTargetPosition and counter < 10:
                        counter += 1
                        targetPosition = (random.randint(3,9),random.randint(3,9),0)

                        offsetBlocked = False
                        for offset in [(-1,0,0),(1,0,0),(0,-1,0),(0,1,0),(0,0,0)]:
                            checkPos = (targetPosition[0]+offset[0],targetPosition[1]+offset[1],0)
                            if room.getItemByPosition(checkPos) or room.getPaintedByPosition(checkPos):
                                offsetBlocked = True
                                break

                        if offsetBlocked:
                            continue

                        validTargetPosition = True
                        break

                    if validTargetPosition:
                        quest = src.quests.questMap["PlaceItem"](targetPositionBig=room.getPosition(),targetPosition=targetPosition,itemType=checkItem,boltDown=True,reason="have at least one scrpa compactor")
                        self.addQuest(quest)
                        return True
            return None
        return None

    def checkTriggerFillFlask(self,character,room):
        if character.flask and character.flask.uses < 3:
            self.addQuest(src.quests.questMap["RefillPersonalFlask"]())
            self.idleCounter = 0
            return True
        return None

    def checkTriggerScavenging(self,character,room):
        terrain = character.getTerrain()
        try:
            terrain.alarm
        except:
            terrain.alarm = False
        if terrain.alarm:
            return None

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
        return None

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
            if "HOMEx" not in character.registers:
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

    def checkTriggerQuesting(self,character,room):
        if character.rank and character.rank != 1:
            terrainPos = (character.registers["HOMETx"],character.registers["HOMETy"])

            foundMissingHeart = False
            for god in src.gamestate.gamestate.gods.values():
                if god["lastHeartPos"] == terrainPos:
                    continue
                foundMissingHeart = True

            if not foundMissingHeart:
                quest = src.quests.questMap["Ascend"]()
                self.addQuest(quest)
                quest.assignToCharacter(character)
                quest.activate()
                self.idleCounter = 0
                return True

        if not character.weapon or not character.armor:
            quest = src.quests.questMap["Equip2"]()
            self.addQuest(quest)
            quest.assignToCharacter(character)
            quest.activate()
            self.idleCounter = 0
            return True

        if character.health == character.maxHealth:

            terrain = character.getTerrain()
            toCheck = terrain.characters[:]
            for room in terrain.rooms:
                toCheck.extend(room.characters)

            numNPCs = 0
            numNPCsWithSameDuties = {}
            for duty in character.duties:
                numNPCsWithSameDuties[duty] = 0
            foundEnemies = []
            for char in toCheck:
                if char.faction == character.faction:
                    if len(char.duties) > 1:
                        continue
                    if char == character:
                        continue
                    numNPCs += 1
                    for duty in character.duties:
                        if duty in char.duties:
                            numNPCsWithSameDuties[duty] += 1
                else:
                    if not char.dead:
                        foundEnemies.append(char)

            if "questing" not in character.duties:
                for duty in character.duties:
                    if not numNPCsWithSameDuties[duty] > 0:
                        return None

            if numNPCs < 5:
                return None

            if foundEnemies:
                random.shuffle(foundEnemies)
                for enemy in foundEnemies:
                    weight = character.weightAttack(enemy.getBigPosition())

                    quest = src.quests.questMap["ClearInventory"]()
                    self.addQuest(quest)
                    quest.assignToCharacter(character)

                    quest = src.quests.questMap["ScavengeTile"](targetPosition=enemy.getBigPosition(),endOnFullInventory=True)
                    self.addQuest(quest)
                    quest.assignToCharacter(character)

                    quest = src.quests.questMap["SecureTile"](toSecure=enemy.getBigPosition(),endWhenCleared=True)
                    self.addQuest(quest)
                    quest.assignToCharacter(character)

                    quest = src.quests.questMap["Equip2"]()
                    self.addQuest(quest)
                    quest.assignToCharacter(character)
                    quest.activate()
                    self.idleCounter = 0
                    return True

            if foundEnemies:
                grievance = ("fighting","bad equipment")
                self.character.addGrievance(grievance)
                return None

            if numNPCs < 9:
                return None

            hasTemple = False
            for room in terrain.rooms:
                if room.tag != "temple":
                    continue
                hasTemple = True

            if hasTemple:
                target = None
                for (godId,god) in src.gamestate.gamestate.gods.items():
                    if god["home"] != god["lastHeartPos"]:
                        continue
                    target = (godId,god)
                    break

                if target:
                    pos = target[1]["lastHeartPos"]

                    if not (character.registers["HOMETx"] == pos[0] and character.registers["HOMETy"] == pos[1]):
                        quest = src.quests.questMap["DelveDungeon"](targetTerrain=pos)
                        self.addQuest(quest)
                        quest.assignToCharacter(character)

                        quest = src.quests.questMap["Equip2"]()
                        self.addQuest(quest)
                        quest.assignToCharacter(character)
                        quest.activate()
                        self.idleCounter = 0
                        return True
                    return None
                return None
            return None
        return None

    def checkTriggerFlaskFilling(self,character,currentRoom):
        foundGooDispenser = None
        for room in self.getRandomPriotisedRooms(character,currentRoom):
            for gooDispenser in room.getItemsByType("GooDispenser"):
                if not gooDispenser.charges:
                    continue
                foundGooDispenser = gooDispenser
                break
            if foundGooDispenser:
                break

        if foundGooDispenser:
            self.addQuest(src.quests.questMap["ClearInventory"]())
            quest = src.quests.questMap["FillFlask"]()
            self.addQuest(quest)
            if not character.searchInventory("Flask"):
                quest = src.quests.questMap["FetchItems"](toCollect="Flask",amount=1)
                self.addQuest(quest)
            quest.activate()
            quest.assignToCharacter(character)
            self.idleCounter = 0
            return True
        return None

    def checkTriggerPraying(self,character,currentRoom):

        for checkRoom in self.getRandomPriotisedRooms(character,currentRoom):
            glassStatues = checkRoom.getItemsByType("GlassStatue")
            foundStatue = None
            for checkStatue in glassStatues:
                if checkStatue.charges >= 5:
                    continue
                if not checkStatue.handleItemRequirements():
                    continue
                foundStatue = checkStatue

            if not foundStatue:
                continue

            quest = src.quests.questMap["Pray"](targetPosition=foundStatue.getPosition(),targetPositionBig=foundStatue.getBigPosition(),shrine=False)
            self.addQuest(quest)
            quest.activate()
            quest.assignToCharacter(character)
            self.idleCounter = 0
            return True

        for checkRoom in self.getRandomPriotisedRooms(character,currentRoom):
            shrines = checkRoom.getItemsByType("Shrine")
            foundShrine = None
            for checkShrine in shrines:
                if not checkShrine.isChallengeDone():
                    continue
                foundShrine = checkShrine

            if not foundShrine:
                continue

            quest = src.quests.questMap["Pray"](targetPosition=foundShrine.getPosition(),targetPositionBig=foundShrine.getBigPosition())
            self.addQuest(quest)
            quest.activate()
            quest.assignToCharacter(character)
            self.idleCounter = 0
            return True
        return None

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

        if (not len(self.subQuests) or not isinstance(self.subQuests[0],src.quests.questMap["Fight"])) and character.getNearbyEnemies():
            quest = src.quests.questMap["Fight"]()
            self.addQuest(quest)
            quest.activate()
            quest.assignToCharacter(character)
            return

        terrain = character.getTerrain()
        if terrain.xPosition != character.registers["HOMETx"] or terrain.yPosition != character.registers["HOMETy"]:
            quest = src.quests.questMap["GoHome"]()
            self.addQuest(quest)
            quest.activate()
            quest.assignToCharacter(character)
            return

        if not character.container:
            return

        """
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
        """

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
                if item.type != "Vial":
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
                if otherCharacter.faction != character.faction:
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
            if not checkRoom.requiredDuties:
                continue

            for duty in checkRoom.requiredDuties:
                if not duty in character.duties:
                    continue

                checkRoom.requiredDuties.remove(duty)

                quest = src.quests.questMap["GoToTile"](targetPosition=checkRoom.getPosition())
                self.addQuest(quest)
                quest.activate()
                self.idleCounter = 0
                return

        try:
            self.numTasksDone
        except:
            self.numTasksDone = 0
        try:
            self.numTasksToDo
        except:
            self.numTasksToDo = None

        self.numTasksDone += 1
        if self.numTasksToDo and self.numTasksDone > self.numTasksToDo:
            self.postHandler()
            return

        room = character.container
        for duty in character.getRandomProtisedDuties():
            match (duty):
                case "trap setting":
                    if self.checkTriggerTrapSetting(character,room):
                        return
                case "turret loading":
                    if self.checkTriggerTurretLoading(character,room):
                        return
                case "flask filling":
                    if self.checkTriggerFlaskFilling(character,room):
                        return
                case "machine operation":
                    if self.checkTriggerMachineOperation(character,room):
                        return
                case "manufacturing":
                    if self.checkTriggerManufacturing(character,room):
                        return
                case "resource gathering":
                    if self.checkTriggerResourceGathering(character,room):
                        return
                case "maggot gathering":
                    if self.checkTriggerMaggotGathering(character,room):
                        return
                case "scratch checking":
                    if self.checkTriggerScratchChecking(character,room):
                        return
                case "cleaning":
                    if self.checkTriggerCleaning(character,room):
                        return
                case "hauling":
                    if self.checkTriggerHauling(character,room):
                        return
                case "resource fetching":
                    if self.checkTriggerResourceFetching(character,room):
                        return
                case "painting":
                    if self.checkTriggerPainting(character,room):
                        return
                case "machine placing":
                    if self.checkTriggerMachinePlacing(character,room):
                        return
                case "room building":
                    if self.checkTriggerRoomBuilding(character,room):
                        return
                case "scavenging":
                    if self.checkTriggerScavenging(character,room):
                        return
                case "scrap hammering":
                    if self.checkTriggerScrapHammering(character,room):
                        return
                case "metal working":
                    if self.checkTriggerMetalWorking(character,room):
                        return
                case "machining":
                    if self.checkTriggerMachining(character,room):
                        return
                case "city planning":
                    if self.checkTriggerCityPlaning(character,room):
                        return
                case "clone spawning":
                    if self.checkTriggerCloneSpawning(character,room):
                        return
                case "epoch questing":
                    if self.checkTriggerEpochQuesting(character,room):
                        return
                case "questing":
                    if self.checkTriggerQuesting(character,room):
                        return
                case "praying":
                    if self.checkTriggerPraying(character,room):
                        return
                case "tutorial":
                    if character == src.gamestate.gamestate.mainChar and self.specialTutorialLogic(character,room):
                        return
        if self.endOnIdle:
            self.postHandler()
            return

        for room in character.getTerrain().rooms:
            if room.tag == "temple":
                if room != character.container:
                    quest = src.quests.questMap["GoToTile"](targetPosition=room.getPosition(),description="go to temple")
                    self.idleCounter += 1
                    self.addQuest(quest)
                    return
                if self.idleCounter > 15 and self.checkTriggerQuesting(character,room):
                    self.idleCounter = 0
                    return
                quest = src.quests.questMap["GoToPosition"](targetPosition=(random.randint(1,11),random.randint(1,11),0),description="wait for something to happen",reason="ensure nothing exciting will happening")
                self.idleCounter += 1
                self.addQuest(quest)
                character.timeTaken += self.idleCounter
                return

        if 1 == 1:
            room = character.getTerrain().getRoomByPosition((7,7,0))[0]
            if room != character.container:
                quest = src.quests.questMap["GoToTile"](targetPosition=(7,7,0),description="go to meeting hall")
                self.idleCounter += 1
                self.addQuest(quest)
                return
            if self.idleCounter > 15 and self.checkTriggerQuesting(character,room):
                self.idleCounter = 0
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
                    character.runCommandString(f"{self.idleCounter}.")
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
                character.runCommandString(f"{self.idleCounter}.")
                return

            self.checkedRoomPositions = []
            self.idleCounter += 10
            character.runCommandString("20.")
            return

        self.idleCounter += 5
        character.runCommandString("20.")

src.quests.addType(BeUsefull)

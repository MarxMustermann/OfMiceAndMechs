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

    def checkTriggerTurretLoading(self,character,room):
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


    def checkTriggerFillFlask(self,character,room):
        if character.flask and character.flask.uses < 3:
            self.addQuest(src.quests.questMap["RefillPersonalFlask"]())
            self.idleCounter = 0
            return True
        return None


    def checkTriggerEat(self,character,room):
        if character.satiation < 200:
            self.addQuest(src.quests.questMap["Eat"]())
            self.idleCounter = 0
            return True
        return None

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
            quest = src.quests.questMap["Equip"]()
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

                    quest = src.quests.questMap["Equip"]()
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

                        quest = src.quests.questMap["Equip"]()
                        self.addQuest(quest)
                        quest.assignToCharacter(character)
                        quest.activate()
                        self.idleCounter = 0
                        return True
                    return None
                return None
            return None
        return None

    def generateSubquests(self,character):

        for quest in self.subQuests:
            if quest.completed:
                self.subQuests.remove(quest)
                break

        self.triggerCompletionCheck(character)

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
                case "turret loading":
                    pass #TODO create a quest
                case "flask filling":
                    if src.quests.questMap["FillFlask"].generateDutyQuest(self,character,room):
                        return
                case "machine operation":
                    if src.quests.questMap["OperateMachine"].generateDutyQuest(self,character,room):
                        return
                case "manufacturing":
                    if src.quests.questMap["Manufacture"].generateDutyQuest(self,character,room):
                        return
                case "resource gathering":
                    if src.quests.questMap["GatherScrap"].generateDutyQuest(self,character,room):
                        return
                case "maggot gathering":
                    if src.quests.questMap["GatherVatMaggots"].generateDutyQuest(self,character,room):
                        return
                case "scratch checking":
                    if self.checkTriggerScratchChecking(character,room):
                        return
                case "cleaning":
                    if src.quests.questMap["CleanSpace"].generateDutyQuest(self,character,room):
                        return
                case "hauling":
                    if src.quests.questMap["RestockRoom"].generateDutyQuest(self,character,room):
                        return
                case "resource fetching":
                    if src.quests.questMap["FetchItems"].generateDutyQuest(self,character,room):
                        return
                case "painting":
                    if src.quests.questMap["DrawFloorPlan"].generateDutyQuest(self,character,room):
                        return
                case "machine placing":
                    if src.quests.questMap["MachinePlacing"].generateDutyQuest(self,character,room):
                        return
                case "room building":
                    if src.quests.questMap["BuildRoom"].generateDutyQuest(self,character,room):
                        return
                case "scavenging":
                    if src.quests.questMap["Scavenge"].generateDutyQuest(self,character,room):
                        return
                case "scrap hammering":
                    if src.quests.questMap["ScrapHammering"].generateDutyQuest(self,character,room):
                        return
                case "metal working":
                    if src.quests.questMap["MetalWorking"].generateDutyQuest(self,character,room):
                        return
                case "machining":
                    if src.quests.questMap["Machining"].generateDutyQuest(self,character,room):
                        return
                case "city planning":
                    if src.quests.questMap["AssignFloorPlan"].generateDutyQuest(self,character,room):
                        return
                case "clone spawning":
                    if src.quests.questMap["GetEpochReward"].generateDutyQuest(self,character,room):
                        return
                case "questing":
                    if self.checkTriggerQuesting(character,room):
                        return
                case "praying":
                    if src.quests.questMap["Pray"].generateDutyQuest(self,character,room):
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

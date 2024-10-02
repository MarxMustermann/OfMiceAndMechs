import logging
import random

import src

logger = logging.getLogger(__name__)

class BeUsefull(src.quests.MetaQuestSequenceV2):
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


    def getNextStep(self, character=None, ignoreCommands=False, dryRun = True):
        if not self.subQuests:
            submenue = character.macroState.get("submenue")
            if submenue:
                if isinstance(submenue,src.interaction.SelectionMenu):
                    return (None,(["esc"],"exit submenu"))
                return (None,(["esc"],"exit submenu"))

        if character.health > character.maxHealth//5:
            if (not len(self.subQuests) or not isinstance(self.subQuests[0],src.quests.questMap["Fight"])) and character.getNearbyEnemies():
                quest = src.quests.questMap["Fight"]()
                return ([quest],None)
        if (not len(self.subQuests) or not isinstance(self.subQuests[0],src.quests.questMap["Fight"])) and character.getNearbyEnemies():
            quest = src.quests.questMap["Fight"]()
            return ([quest],None)


        terrain = character.getTerrain()
        if terrain.xPosition != character.registers["HOMETx"] or terrain.yPosition != character.registers["HOMETy"]:
            quest = src.quests.questMap["GoHome"]()
            return ([quest],None)

        if not character.container:
            return (None,None)

        if not isinstance(character.container,src.rooms.Room):
            if character.yPosition%15 == 14:
                return (None,("w","enter room"))
            if character.yPosition%15 == 0:
                return (None,("s","enter room"))
            if character.xPosition%15 == 14:
                return (None,("a","enter room"))
            if character.xPosition%15 == 0:
                return (None,("d","enter room"))

        if not isinstance(character.container,src.rooms.Room):
            if self.targetPosition:
                quest = src.quests.questMap["GoToTile"](targetPosition=self.targetPosition)
                return ([quest],None)
            else:
                quest = src.quests.questMap["GoHome"]()
                return ([quest],None)
            
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
                return ([quest],None)

        if "guarding" in character.duties:
            for otherCharacter in room.characters:
                if otherCharacter.faction != character.faction:
                    if not dryRun:
                        self.idleCounter = 0
                    return (None,("gg","guard"))

        if self.targetPosition:
            if not (self.targetPosition[0] == room.xPosition and self.targetPosition[1] == room.yPosition):
                quest = src.quests.questMap["GoToTile"](targetPosition=self.targetPosition)
                return ([quest],None)
        step = src.quests.questMap["RefillPersonalFlask"].generateDutyQuest(self,character,room,dryRun)
        if step != (None,None):
            return step
        step = src.quests.questMap["Eat"].generateDutyQuest(self,character,room,dryRun)
        if step != (None,None):
                        return step

        terrain = character.getTerrain()
        for checkRoom in terrain.rooms:
            if not checkRoom.requiredDuties:
                continue

            for duty in checkRoom.requiredDuties:
                if not duty in character.duties:
                    continue

                checkRoom.requiredDuties.remove(duty)

                quest = src.quests.questMap["GoToTile"](targetPosition=checkRoom.getPosition())
                return ([quest],None)
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
            return (None,None)

        room = character.container
        for duty in character.getRandomProtisedDuties():
            match (duty):
                case "flask filling":
                    step = src.quests.questMap["FillFlask"].generateDutyQuest(self,character,room,dryRun)
                case "machine operation":
                    step = src.quests.questMap["OperateMachine"].generateDutyQuest(self,character,room,dryRun)
                case "manufacturing":
                    step = src.quests.questMap["Manufacture"].generateDutyQuest(self,character,room,dryRun)
                case "resource gathering":
                    step = src.quests.questMap["GatherScrap"].generateDutyQuest(self,character,room,dryRun)
                case "maggot gathering":
                    step = src.quests.questMap["GatherVatMaggots"].generateDutyQuest(self,character,room,dryRun)
                case "cleaning":
                    step = src.quests.questMap["CleanSpace"].generateDutyQuest(self,character,room,dryRun)
                case "hauling":
                    step = src.quests.questMap["RestockRoom"].generateDutyQuest(self,character,room,dryRun)
                case "resource fetching":
                    step = src.quests.questMap["FetchItems"].generateDutyQuest(self,character,room,dryRun)
                case "painting":
                    step = src.quests.questMap["DrawFloorPlan"].generateDutyQuest(self,character,room,dryRun)
                case "machine placing":
                    step = src.quests.questMap["MachinePlacing"].generateDutyQuest(self,character,room,dryRun)
                case "room building":
                    step = src.quests.questMap["BuildRoom"].generateDutyQuest(self,character,room,dryRun)
                case "scavenging":
                    step = src.quests.questMap["Scavenge"].generateDutyQuest(self,character,room,dryRun)
                case "scrap hammering":
                    step = src.quests.questMap["ScrapHammering"].generateDutyQuest(self,character,room,dryRun)
                case "metal working":
                    step = src.quests.questMap["MetalWorking"].generateDutyQuest(self,character,room,dryRun)
                case "machining":
                    step = src.quests.questMap["Machining"].generateDutyQuest(self,character,room,dryRun)
                case "city planning":
                    step = src.quests.questMap["AssignFloorPlan"].generateDutyQuest(self,character,room,dryRun)
                case "clone spawning":
                    step = src.quests.questMap["GetEpochReward"].generateDutyQuest(self,character,room,dryRun)
                case "praying":
                    step = src.quests.questMap["Pray"].generateDutyQuest(self,character,room,dryRun)
            if step != (None,None):
                return step
        if self.endOnIdle:
            self.postHandler()
            return (None,None)

        for room in character.getTerrain().rooms:
            if room.tag == "temple":
                if room != character.container:
                    quest = src.quests.questMap["GoToTile"](targetPosition=room.getPosition(),description="go to temple")
                    if not dryRun:
                        self.idleCounter += 1
                    return ([quest],None)
                quest = src.quests.questMap["GoToPosition"](targetPosition=(random.randint(1,11),random.randint(1,11),0),description="wait for something to happen",reason="ensure nothing exciting will happening")
                if not dryRun:
                    self.idleCounter += 1
                character.timeTaken += self.idleCounter
                return ([quest],None)

        room = character.getTerrain().getRoomByPosition((7,7,0))[0]
        if room != character.container:
            quest = src.quests.questMap["GoToTile"](targetPosition=(7,7,0),description="go to meeting hall")
            if not dryRun:
                self.idleCounter += 1
            return ([quest],None)
        quest = src.quests.questMap["GoToPosition"](targetPosition=(random.randint(1,11),random.randint(1,11),0),description="wait for something to happen",reason="ensure nothing exciting will happening")
        if not dryRun:
            self.idleCounter += 1
        character.timeTaken += self.idleCounter
        return ([quest],None)

src.quests.addType(BeUsefull)

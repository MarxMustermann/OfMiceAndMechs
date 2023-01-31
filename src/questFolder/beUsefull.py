import src
import random

class BeUsefull(src.quests.MetaQuestSequence):
    type = "BeUsefull"

    def __init__(self, description="be useful", creator=None, targetPosition=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description

        self.targetPosition = None
        self.idleCounter = 0
        if targetPosition:
            self.setParameters({"targetPosition":targetPosition})

        self.shortCode = " "

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
            amount = 2*self.character.rank
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
        if not self.character == src.gamestate.gamestate.mainChar:
            return

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
        super().assignToCharacter(character)

    def triggerCompletionCheck(self,character=None):
        return

    def setParameters(self,parameters):
        if "targetPosition" in parameters and "targetPosition" in parameters:
            self.targetPosition = parameters["targetPosition"]
        return super().setParameters(parameters)

    def solver(self, character):
        if not self.subQuests:
            self.generateSubquests(character)
            if self.subQuests:
                return

            command = self.getSolvingCommandString(character)
            if command:
                character.runCommandString(command)
                return

        super().solver(character)

    def generateSubquests(self,character):

        for quest in self.subQuests:
            if quest.completed:
                self.subQuests.remove(quest)
                break

        self.triggerCompletionCheck(character)

        if not character.container:
            return

        if character.rank == 6 and character.reputation >= 300:
            quest = src.quests.questMap["GetPromotion"](5)
            self.addQuest(quest)
            quest.activate()
            quest.assignToCharacter(character)
            return

        if character.rank == 5 and character.reputation >= 500:
            quest = src.quests.questMap["GetPromotion"](4)
            self.addQuest(quest)
            quest.activate()
            quest.assignToCharacter(character)
            return

        if character.rank == 4 and character.reputation >= 750:
            quest = rc.quests.questMap["GetPromotion"](3)
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

        if self.idleCounter > 15 or (character.rank == 6 and len(character.duties) < 1) or (character.rank == 5 and len(character.duties) < 2) or (character.rank == 4 and len(character.duties) < 3) or (character.rank == 3 and len(character.duties) < 4):
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

        def triggerClearIneventory():
            if len(character.inventory) > 9:
                self.addQuest(src.quests.questMap["ClearInventory"]())
                return True
            # clear inventory local
            if len(character.inventory) > 1:
                emptyInputSlots = room.getEmptyInputslots(character.inventory[-1].type, allowAny=True)
                if emptyInputSlots:
                    self.addQuest(src.quests.questMap["RestockRoom"](toRestock=character.inventory[-1].type, allowAny=True))
                    return True

            # go to garbage stockpile and unload
            if len(character.inventory) > 6:
                if not "HOMEx" in character.registers:
                    return True
                homeRoom = room.container.getRoomByPosition((character.registers["HOMEx"],character.registers["HOMEy"]))[0]
                if not hasattr(homeRoom,"storageRooms") or not homeRoom.storageRooms:
                    return True
                quest = src.quests.questMap["GoToTile"](targetPosition=(homeRoom.storageRooms[0].xPosition,homeRoom.storageRooms[0].yPosition,0))
                self.addQuest(quest)
                quest.assignToCharacter(character)
                quest.activate()
                return True
            return False

        if self.targetPosition:
            if not (self.targetPosition[0] == room.xPosition and self.targetPosition[1] == room.yPosition):
                quest = src.quests.questMap["GoToTile"](targetPosition=self.targetPosition)
                self.addQuest(quest)
                quest.assignToCharacter(character)
                quest.activate()
                return

        if "trap setting" in character.duties:
            if hasattr(room,"electricalCharges"):
                if room.electricalCharges < room.maxElectricalCharges:

                    quest = src.quests.questMap["ReloadTraproom"](targetPosition=room.getPosition())
                    self.addQuest(quest)
                    quest.activate()
                    self.idleCounter = 0
                    return

        if "machine operation" in character.duties:
            items = room.itemsOnFloor[:]
            random.shuffle(items)
            for item in items:
                if not item.bolted:
                    continue
                if not item.type in ("Machine","ScrapCompactor",):
                    continue
                if not item.readyToUse():
                    continue
                quest = src.quests.questMap["OperateMachine"](targetPosition=item.getPosition())
                self.addQuest(quest)
                quest.activate()
                self.idleCounter = 0
                return

        if "resource gathering" in character.duties:
            emptyInputSlots = room.getEmptyInputslots(itemType="Scrap")
            if emptyInputSlots:
                for inputSlot in random.sample(list(emptyInputSlots),len(emptyInputSlots)):
                    if not inputSlot[1] == "Scrap":
                        continue

                    if not room.sources:
                        continue

                    source = None
                    for potentialSource in random.sample(list(room.sources),len(room.sources)):
                        if potentialSource[1] == "rawScrap":
                            source = potentialSource
                            break

                    if source == None:
                        continue

                    if triggerClearIneventory():
                        return

                    self.addQuest(src.quests.questMap["RestockRoom"](toRestock="Scrap"))
                    self.addQuest(src.quests.questMap["GoToTile"](targetPosition=(room.xPosition,room.yPosition)))
                    self.addQuest(src.quests.questMap["GatherScrap"](targetPosition=source[0]))
                    self.addQuest(src.quests.questMap["GoToTile"](targetPosition=(source[0])))
                    self.idleCounter = 0
                    return

        if "scratch checking" in character.duties:
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

        if "cleaning" in character.duties:
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
                        return

                    quest = src.quests.questMap["ClearTile"](targetPosition=room.getPosition())
                    self.addQuest(quest)
                    quest.assignToCharacter(character)
                    quest.activate()
                    self.idleCounter = 0
                    return

        if "hauling" in character.duties:
            if hasattr(room,"inputSlots"):
                checkedTypes = set()

                emptyInputSlots = room.getEmptyInputslots()
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
                            if triggerClearIneventory():
                                return

                        self.addQuest(src.quests.questMap["FetchItems"](toCollect=inputSlot[1]))
                        self.idleCounter = 0
                        return

        if "resource fetching" in character.duties:
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
                                character.addMessage("no filled output slots")
                                continue

                        self.addQuest(src.quests.questMap["RestockRoom"](toRestock=inputSlot[1]))
                        self.idleCounter = 0

                        if not hasItem:
                            if triggerClearIneventory():
                                return

                            roomPos = (room.xPosition,room.yPosition,0)
                            if not source[0] == roomPos:
                                self.addQuest(src.quests.questMap["GoToTile"](targetPosition=roomPos))
                            self.addQuest(src.quests.questMap["FetchItems"](toCollect=inputSlot[1]))
                            if not source[0] == roomPos:
                                self.addQuest(src.quests.questMap["GoToTile"](targetPosition=(source[0])))
                        return

                    character.addMessage("no valid input slot found")
                character.addMessage("no empty input slot found")
            character.addMessage("no input slots")

        # officer work
        if "painting" in character.duties:
            # set up machines
            if room.floorPlan:
                self.addQuest(src.quests.questMap["DrawFloorPlan"]())
                self.idleCounter = 0
                return

        if not room.floorPlan and "machine placing" in character.duties:

            if room.buildSites:
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
                            character.addMessage("no filled output slots")
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
                            return

                        roomPos = (room.xPosition,room.yPosition)

                        if not source[0] == roomPos:
                            self.addQuest(src.quests.questMap["GoToTile"](targetPosition=roomPos))
                        self.addQuest(src.quests.questMap["FetchItems"](toCollect=neededItem,amount=1))
                        if not source[0] == roomPos:
                            self.addQuest(src.quests.questMap["GoToTile"](targetPosition=(source[0])))
                    self.idleCounter = 0
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
                    return

        self.idleCounter += 5
        character.runCommandString("20.")

src.quests.addType(BeUsefull)

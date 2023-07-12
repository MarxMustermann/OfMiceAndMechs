import src
import random
import copy
import json

class EpochArtwork(src.items.Item):
    """
    """


    type = "EpochArtwork"

    def __init__(self, epochLength, name="EpochArtwork", noId=False, rewardSet=None):
        """
        set up the initial state
        """

        super().__init__(display="EA", name=name)

        self.epochSurvivedRewardAmount = 30
        self.applyOptions.extend(
                        [
                                                                ("getEpochChallenge", "get epoch challenge"),
                                                                ("getEpochRewards", "get epoch rewards (0)"),
                                                                ("getEpochEvaluation", "get epoch evaluation"),
                        ]
                        )
        self.applyMap = {
                            "getEpochChallenge":self.getEpochChallenge,
                            "getEpochRewards":self.getEpochRewards,
                            "getEpochEvaluation":self.getEpochEvaluation,
                        }
        self.firstUse = True
        self.epochLength = epochLength
        self.lastEpochSurvivedReward = 0
        self.lastNumSpawners = 0
        self.shadowCharges = 1000
        self.rewardSet = rewardSet

        self.charges = 0
        self.leader = None

        self.registeredWon = False

        self.description = """
This is a one of its kind machine. It cannot be reproduced and was created by an artisan.
This artwork manages the flow of the epochs.
It generates missions and hands out rewards."""
        self.usageInfo = """
Use it by activating it. You will recieve further instructions."""

        self.lastRoomReward = 1

    def setSpecialItemMap(self,specialItemMap):
        self.specialItemMap = specialItemMap

    def changeCharges(self,delta):
        delta = min(self.shadowCharges,delta)

        if delta > 0:
            self.shadowCharges -= delta

        self.charges += delta
        self.applyOptions[1] = ("getEpochRewards", "get epoch rewards (%s)"%(self.charges,))

    def getEpochEvaluation(self,character):
        self.recalculateGlasstears(character)

    def getEpochRewards(self,character):

        options = []
        options.append(("None","(0) None"))
        if not self.rewardSet:
            options.append(("autoSpend","(?) auto spend rewards"))
            options.append(("HealingOnce","(1) healing (once)"))
            amount = character.maxHealth-character.health
            amount = min(amount,self.charges*10)
            cost = amount//10
            if amount%10:
                cost += 1
            options.append(("Healing","(%s) healing"%(cost,)))
            options.append(("weaponUpgradeOnce","(1) weapon upgrade (once)"))
            options.append(("weaponUpgrade","(?) weapon upgrade"))
            options.append(("armorUpgradeOnce","(5) armor upgrade (once)"))
            options.append(("armorUpgrade","(?) armor upgrade"))
            options.append(("rank 4","(20) rank 4 NPCs"))
            options.append(("rank 5","(15) rank 5 NPCs"))
            options.append(("rank 6","(10) rank 6 NPCs"))
            options.append(("chargePersonel","(10) charge personel artwork"))
            options.append(("repairCommandCentre","(100) repair command centre"))
            options.append(("recharge trap rooms once","(10) recharge trap roomsby 10 charges (once)"))
            options.append(("recharge trap rooms","(?) recharge trap rooms"))
            options.append(("respawn scrapfield","(30) respawn scrap field"))
            options.append(("spawn lightning rods","(10) spawn 25 ligthning rods"))
            options.append(("spawn new clone","(15) spawn new clone"))
        else:
            options.append(("spawn gatherer","(10) spawn gatherer"))
            options.append(("spawn operator","(10) spawn operator"))
            options.append(("spawn fetcher","(10) spawn fetcher"))
            options.append(("spawn hauler","(10) spawn hauler"))
            options.append(("spawn painter","(10) spawn painter"))
            options.append(("spawn machine placer","(10) spawn machine placer"))
            options.append(("spawn room builder","(10) spawn room builder"))
            options.append(("spawn maggot gatherer","(10) spawn maggot gatherer"))
            options.append(("spawn scavenger","(10) spawn scavenger"))
            options.append(("spawn food item","(5) spawn food item"))
            options.append(("spawn scrap","(20) spawn scrap"))
            options.append(("spawn personnel tracker","(5) spawn personnel tracker"))
        submenue = src.interaction.SelectionMenu("what reward do you desire? You currently have %s glass tears"%(self.charges,),options,targetParamName="rewardType")
        character.macroState["submenue"] = submenue
        character.macroState["submenue"].followUp = {"container":self,"method":"dispenseEpochRewards","params":{"character":character}}

    def getEpochRewardsProxy(self,extraInfo):
        self.getEpochRewards(extraInfo["character"])

    def dispenseEpochRewards(self,extraInfo):
        character = extraInfo.get("character")

        if not "rewardType" in extraInfo:
            return
        
        if extraInfo["rewardType"] == "None":
            return

        text = "NIY"
        if extraInfo["rewardType"] == "autoSpend":
            self.autoSpendRewards(character)
            return
        if extraInfo["rewardType"] == "HealingOnce":
            if not self.charges > 0:
                text = "not enough glass tears"
            elif not character.health < character.maxHealth:
                text = "no healing needed"
            else:
                character.heal(10)
                text = "you got healed for 10 health for the cost of 1 glass tear"
                self.changeCharges(-1)
        elif extraInfo["rewardType"] == "Healing":
            self.heal(character)
        elif extraInfo["rewardType"] == "weaponUpgradeOnce":
            if not self.charges > 0:
                text = "not enough glass tears"
            elif not character.weapon:
                text = "you have no weapon"
            elif character.weapon.baseDamage >= 25:
                text = "you cant upgrade your weapon further"
            else:
                character.weapon.baseDamage += 1
                text = "weapon upgraded to %s"%(character.weapon.baseDamage,)
                self.changeCharges(-1)
        elif extraInfo["rewardType"] == "weaponUpgrade":
            self.weaponUpgrade(character)
        elif extraInfo["rewardType"] == "armorUpgradeOnce":
            if not self.charges > 4:
                text = "not enough glass tears"
            elif not character.armor:
                text = "you have no armor"
            elif character.armor.armorValue >= 5:
                text = "you cant upgrade your armor further"
            else:
                character.armor.armorValue += 1
                text = "armor upgraded to %s"%(character.armor.armorValue,)
                self.changeCharges(-5)
        elif extraInfo["rewardType"] == "armorUpgrade":
            self.armorUpgrade(character)
        elif extraInfo["rewardType"] == "rank 6":
            if not self.charges > 9:
                text = "not enough glass tears"
            else:
                personnelArtwork = self.container.getItemByType("PersonnelArtwork")
                char = personnelArtwork.spawnRank6(character)
                if char:
                    text = "NPC spawned"
                    self.changeCharges(-10)
                else:
                    text = "Something went wrong. No NPC spawned. see your message log (x) for what went wrong"
        elif extraInfo["rewardType"] == "rank 5":
            if not self.charges > 14:
                text = "not enough glass tears"
            else:
                personnelArtwork = self.container.getItemByType("PersonnelArtwork")
                char = personnelArtwork.spawnRank5(character)
                if char:
                    text = "NPC spawned"
                    self.changeCharges(-15)
                else:
                    text = "Something went wrong. No NPC spawned. see your message log (x) for what went wrong"
        elif extraInfo["rewardType"] == "rank 4":
            if not self.charges > 19:
                text = "not enough glass tears"
            else:
                personnelArtwork = self.container.getItemByType("PersonnelArtwork")
                char = personnelArtwork.spawnRank4(character)
                if char:
                    text = "NPC spawned"
                    self.changeCharges(-20)
                else:
                    text = "Something went wrong. No NPC spawned. see your message log (x) for what went wrong"
        elif extraInfo["rewardType"] == "chargePersonel":
            if not self.charges > 10:
                text = "not enough glass tears"
            else:
                personnelArtwork = self.container.getItemByType("PersonnelArtwork")
                if personnelArtwork:
                    personnelArtwork.changeCharges(1)
                    self.changeCharges(-10)
                    text = "personal artwork charged up"
                else:
                    text = "Something went wrong. No Personel artwork found"
        elif extraInfo["rewardType"] == "repairCommandCentre":
            if not self.charges > 100:
                text = "not enough glass tears"
            else:
                self.changeCharges(-100)
                neededitemTypes = ["PersonnelArtwork","QuestArtwork","DutyArtwork","StaffArtwork","Assimilator","BasicTrainer","OrderArtwork","ArchitectArtwork","CityBuilder2"]
                for itemType in neededitemTypes:
                    item = self.container.getItemByType(itemType)
                    if item:
                        continue
                    candidates = [(1,1,0),(3,1,0),(5,1,0),(7,1,0),(9,1,0),(11,1,0),(11,3,0),(11,5,0),(11,7,0),(11,9,0),(11,11,0),(1,3,0),(1,5,0),(1,7,0),(1,9,0),(1,11,0)]
                    random.shuffle(candidates)

                    item = src.items.itemMap[itemType]()

                    for candidate in candidates:
                        if self.container.getItemByPosition(candidate):
                            continue
                        self.container.addItem(item,candidate)
                        break

                text = "command centre repaired"
        elif extraInfo["rewardType"] == "recharge trap rooms once":
            if not self.charges > 10:
                text = "not enough glass tears"
            else:
                self.changeCharges(-10)
                text = "no trap room to charge"
                for room in character.getTerrain().rooms:
                    if not isinstance(room,src.rooms.TrapRoom):
                        continue
                    if not room.needsCharges():
                        continue

                    room.changeCharges(10)
                    text = "trap room recharged"
                    break
        elif extraInfo["rewardType"] == "recharge trap rooms":
            self.rechargeTrapRooms(character)
        elif extraInfo["rewardType"] == "respawn scrapfield":
            if not self.charges > 30:
                text = "not enough glass tears"
            else:
                self.changeCharges(-30)
                cityBuilder = self.container.getItemByType("CityBuilder2")
                cityBuilder.addScrapFieldFromMap({"coordinate":(8,5,0)})
                text = "respawned scrap field"
        elif extraInfo["rewardType"] == "spawn lightning rods":
            if not self.charges > 10:
                text = "not enough glass tears"
            else:
                homeRoom = character.getHomeRoom()
                storageRoom = homeRoom.storageRooms[0]
                for inputSlot in storageRoom.getEmptyInputslots("invalid",allowAny=True):
                    text = "spawned lighning rods into storage"
                    for i in range(1,25):
                        item = src.items.itemMap["LightningRod"]()
                        storageRoom.addItem(item,inputSlot[0])
                    self.changeCharges(-10)
                    break
        elif extraInfo["rewardType"] == "spawn new clone":
            text = "spawning new clone"
            self.spawnNewClone(character)
        elif extraInfo["rewardType"] == "spawn gatherer":
            text = "spawning gatherer"
            self.spawnBurnedInNPC(character,"resource gathering")
        elif extraInfo["rewardType"] == "spawn operator":
            text = "spawning operator"
            self.spawnBurnedInNPC(character,"machine operation")
        elif extraInfo["rewardType"] == "spawn fetcher":
            text = "spawning fetcher"
            self.spawnBurnedInNPC(character,"resource fetching")
        elif extraInfo["rewardType"] == "spawn hauler":
            text = "spawning hauler"
            self.spawnBurnedInNPC(character,"hauling")
        elif extraInfo["rewardType"] == "spawn painter":
            text = "spawning painter"
            self.spawnBurnedInNPC(character,"painting")
        elif extraInfo["rewardType"] == "spawn machine placer":
            text = "spawning machine placer"
            self.spawnBurnedInNPC(character,"machine placing")
        elif extraInfo["rewardType"] == "spawn room builder":
            text = "spawning room builder"
            self.spawnBurnedInNPC(character,"room building")
        elif extraInfo["rewardType"] == "spawn maggot gatherer":
            text = "spawning maggot gatherer"
            self.spawnBurnedInNPC(character,"maggot gathering")
        elif extraInfo["rewardType"] == "spawn scavenger":
            text = "spawning scavenger"
            self.spawnBurnedInNPC(character,"scavenging")
        elif extraInfo["rewardType"] == "spawn scavenger":
            text = "spawning scavenger"
            self.spawnBurnedInNPC(character,"scavenging")
        elif extraInfo["rewardType"] == "spawn food item":
            text = "spawning food"
            self.spawnResource(character,"food")
        elif extraInfo["rewardType"] == "spawn scrap":
            text = "spawning scrap"
            self.spawnScrap(character)
        elif extraInfo["rewardType"] == "spawn personnel tracker":
            text = "spawning personnel tracker"
            self.spawnArtwork(character,"PersonnelTracker",5)

        submenue = src.interaction.TextMenu(text)
        character.macroState["submenue"] = submenue
        character.macroState["submenue"].followUp = {"container":self,"method":"getEpochRewardsProxy","params":{"character":character}}
        return
    
    def spawnArtwork(self, character,itemType, cost):
        text = ""
        if not self.charges >= cost:
            text = "not enough glass tears"
        else:
            self.changeCharges(-cost)

            item = src.items.itemMap[itemType]()
            character.inventory.append(item)

    def spawnScrap(self, character):
        text = ""
        if not self.charges >= 20:
            text = "not enough glass tears"
        else:
            self.changeCharges(-20)

            text = "spawning scrap field"
            terrain = self.getTerrain()
            items = []
            for scrapField in terrain.scrapFields:
                for i in range(0,30):
                    pos = (scrapField[0]*15+random.randint(1,13),scrapField[1]*15+random.randint(1,13),0)
                    scrap = src.items.itemMap["Scrap"](amount=random.randint(15,20))
                    terrain.addItem(scrap,pos)

            text = "spawing food into your inventory"

        if character:
            character.addMessage(text)

    def spawnResource(self, character, resourceType):
        text = ""
        if not self.charges >= 5:
            text = "not enough glass tears"
        else:
            self.changeCharges(-5)

            text = "spawning food"
            flask = src.items.itemMap["GooFlask"]()
            flask.uses = 10
            character.inventory.append(flask)

            text = "spawing food into your inventory"

        if character:
            character.addMessage(text)

    def spawnBurnedInNPC(self, character, duty):
        text = ""
        if not self.charges >= 10:
            text = "not enough glass tears"
        else:
            self.changeCharges(-10)

            npc = src.characters.Character()
            npc.questsDone = [
                "NaiveMoveQuest",
                "MoveQuestMeta",
                "NaiveActivateQuest",
                "ActivateQuestMeta",
                "NaivePickupQuest",
                "PickupQuestMeta",
                "DrinkQuest",
                "CollectQuestMeta",
                "FireFurnaceMeta",
                "ExamineQuest",
                "NaiveDropQuest",
                "DropQuestMeta",
                "LeaveRoomQuest",
            ]

            npc.solvers = [
                "SurviveQuest",
                "Serve",
                "NaiveMoveQuest",
                "MoveQuestMeta",
                "NaiveActivateQuest",
                "ActivateQuestMeta",
                "NaivePickupQuest",
                "PickupQuestMeta",
                "DrinkQuest",
                "ExamineQuest",
                "FireFurnaceMeta",
                "CollectQuestMeta",
                "WaitQuest" "NaiveDropQuest",
                "NaiveDropQuest",
                "DropQuestMeta",
            ]

            room = self.container
            terrain = self.container.container

            npc.faction = character.faction
            #npc.rank = 6
            room.addCharacter(npc,self.xPosition,self.yPosition)
            npc.flask = src.items.itemMap["GooFlask"]()
            npc.flask.uses = 10

            npc.duties = []
            #duty = random.choice(("hauling","resource fetching","maggot gathering","resource gathering","machine operation","hauling","resource fetching","cleaning","machine placing","maggot gathering"))
            #duty = random.choice(("maggot gathering",))
            npc.duties.append(duty)
            npc.registers["HOMEx"] = 7
            npc.registers["HOMEy"] = 7
            npc.registers["HOMETx"] = terrain.xPosition
            npc.registers["HOMETy"] = terrain.yPosition

            npc.personality["autoFlee"] = False
            npc.personality["abortMacrosOnAttack"] = False
            npc.personality["autoCounterAttack"] = False

            quest = src.quests.questMap["BeUsefull"](strict=True)
            quest.autoSolve = True
            quest.assignToCharacter(npc)
            quest.activate()
            npc.assignQuest(quest,active=True)
            npc.foodPerRound = 1

            '''
            numNewRooms = len(terrain.rooms)-state.get("lastNumRooms",1)
            while numNewRooms > 0:
                itemType = random.choice([("personelArtwork","DutyArtwork","OrderArtwork")])
                item = itemMap
                item = src.items.
                text = """
You have build a new room. you are rewarded with an extra item:

The item will appear in your inventory.

press enter to continue"""%(npc.name,duty,terrain)
                src.interaction.showInterruptText(text)
            '''
            text = "spawning burned in NPC"

        if character:
            character.addMessage(text)

    def rechargeTrapRooms(self, character):
        text = ""
        if not self.charges > 10:
            text = "not enough glass tears"
        else:
            while self.charges > 10:
                for room in self.getTerrain().rooms:
                    if not isinstance(room,src.rooms.TrapRoom):
                        continue
                    if not room.needsCharges():
                        continue

                    amount = (room.maxElectricalCharges - room.electricalCharges)//10+1
                    amount = min(amount,self.charges//10)

                    self.changeCharges(-10*amount)
                    room.changeCharges(10*amount)
                    text += "\ntrap room %s recharged"%(room.getPosition(),)
                    break
                text = "no trap room to charge"
                break
        if character:
            character.addMessage(text)

    def armorUpgrade(self,character):
        if not self.charges > 4:
            text = "not enough glass tears"
        elif not character.armor:
            text = "you have no armor"
        elif character.armor.armorValue >= 5:
            text = "you cant upgrade your armor further"
        else:
            amount = 5-character.armor.armorValue
            amount = min(amount,self.charges//5)

            character.armor.armorValue += amount
            text = "armor upgraded to %s"%(character.armor.armorValue,)
            self.changeCharges(-amount*5)
        if character:
            character.addMessage(text)

    def weaponUpgrade(self,character):
        if not self.charges > 0:
            text = "not enough glass tears"
        elif not character.weapon:
            text = "you have no weapon"
        elif character.weapon.baseDamage >= 25:
            text = "you cant upgrade your weapon further"
        else:
            amount = 25-character.weapon.baseDamage
            amount = min(amount,self.charges*1)

            character.weapon.baseDamage += amount
            text = "weapon upgraded to %s"%(character.weapon.baseDamage,)
            self.changeCharges(-amount*1)
        if character:
            character.addMessage(text)

    def heal(self,character):
        if not self.charges > 0:
            text = "not enough glass tears"
        elif not character.health < character.maxHealth:
            text = "no healing needed"
        else:
            amount = character.maxHealth-character.health
            amount = min(amount,self.charges*10)
            character.heal(amount)

            cost = amount//10
            if amount%10:
                cost += 1

            text = "you got healed for %s health for the cost of %s glass tears"%(amount,cost,)
            self.changeCharges(-cost)
        if character:
            character.addMessage(text)

    def spawnNewClone(self,character):
        cost = 15
        if not self.charges > cost:
            text = "not enough glass tears"
        else:
            personnelArtwork = self.container.getItemByType("PersonnelArtwork")
            if personnelArtwork:
                personnelArtwork.changeCharges(1)
                npc = personnelArtwork.spawnIndependentClone(character)
                self.changeCharges(-15)
                text = "spawned new clone"
            else:
                text = "Something went wrong. No Personel artwork found"

        if character:
            character.addMessage(text)

    def getEpochChallenge(self,character):
        epochQuest = None
        for quest in character.quests:
            if not isinstance(quest,src.quests.questMap["EpochQuest"]):
                continue
            epochQuest = quest

        if not epochQuest:
            character.addMessage("no epoch quest found")
            return

        text = ""
        foundSpawner = False
        terrain = character.getTerrain()
        for room in terrain.rooms:
            items = room.getItemByPosition((6,6,0))
            for item in items:
                if isinstance(item, src.items.itemMap["MonsterSpawner"]):
                    foundSpawner = True
                    break

        if foundSpawner:
            text += """
Destroy the spawners.

The waves of enemies are spawned by spawners.

Destroy one of the spawners to stop enemies from coming in.

Once you destroy a spawner nearby enemies will rush the base.
Prepare your base to brace the impact before you destroy the spawner.

"""

            character.addMessage(text)
            submenue = src.interaction.TextMenu(text)
            character.macroState["submenue"] = submenue

            quest = src.quests.questMap["DestroySpawners"]()
            quest.active = True
            quest.assignToCharacter(character)

            epochQuest.addQuest(quest)
            return

        print(len(terrain.rooms))
        if len(terrain.rooms) < 6:
            text += """
set up base

Extend the base to have at least 6 rooms

"""

            character.addMessage(text)
            submenue = src.interaction.TextMenu(text)
            character.macroState["submenue"] = submenue

            quest = src.quests.questMap["ExtendBase"]()
            quest.active = True
            quest.assignToCharacter(character)

            epochQuest.addQuest(quest)
            return


        foundEnemy = None
        for otherChar in terrain.characters:
            if otherChar.faction == "invader":
                foundEnemy = otherChar
                break

        for room in terrain.rooms:
            for otherChar in room.characters:
                if otherChar.faction == "invader":
                    foundEnemy = otherChar
                    break

        if foundEnemy:
            text += """
Clear the remaining enemies.

Kill all remaining enemies to end the siege.

"""

            character.addMessage(text)
            submenue = src.interaction.TextMenu(text)
            character.macroState["submenue"] = submenue

            quest = src.quests.questMap["ClearTerrain"]()
            quest.active = True
            quest.assignToCharacter(character)

            epochQuest.addQuest(quest)
            return

        foundToChargeRoom = False
        for room in terrain.getRoomsByType(src.rooms.TrapRoom):
            if room.electricalCharges < room.maxElectricalCharges-30:
                foundToChargeRoom = True

        if foundToChargeRoom:
            text += """
Recharge the trap rooms.

The bases defence should be fully charged

"""

            character.addMessage(text)
            submenue = src.interaction.TextMenu(text)
            character.macroState["submenue"] = submenue

            quest = src.quests.questMap["ReloadTraps"]()
            quest.active = True
            quest.assignToCharacter(character)

            epochQuest.addQuest(quest)
            return

        foundSpecialItems = []
        for room in terrain.rooms:
            if not isinstance(room, src.rooms.TempleRoom):
                continue
            for item in room.itemsOnFloor:
                if not isinstance(item, src.items.itemMap["SpecialItemSlot"]):
                    continue
                if item.hasItem:
                    foundSpecialItems.append(item)

        if len(foundSpecialItems) < 4:
            text += """
NIY
"""

            character.addMessage(text)
            submenue = src.interaction.TextMenu(text)
            character.macroState["submenue"] = submenue

            while True:
                itemId = random.choice(list(self.specialItemMap.keys()))
                if self.getTerrain().getPosition() == self.specialItemMap[itemId]:
                    continue
                break
            quest = src.quests.questMap["ObtainSpecialItem"](targetTerrain=self.specialItemMap[itemId],itemId=itemId)
            quest.active = True
            quest.assignToCharacter(character)

            epochQuest.addQuest(quest)
            return

        if not self.registeredWon:
            text += """
you won the game!


Have fun and remember to give me some feedback.
If you want to dicuss things you are very welcome to join my discord and talk to me.

That is actually the best way to support the games development for now.
Feeling a bit lonely with it.

"""

            character.addMessage(text)
            submenue = src.interaction.TextMenu(text)
            character.macroState["submenue"] = submenue

            character.clearCommandString()

            self.registeredWon = True
            self.changeCharges(self.shadowCharges)
            return

        text += """
you won the game!

That is it content wise for now.
The game will continue to run so you can use it as a sandbox for a bit.

While you can be useful and repair the base.
The quest you get will try to guide you, but that is WIP and may require guesswork.

"""
        character.addMessage(text)
        submenue = src.interaction.TextMenu(text)
        character.macroState["submenue"] = submenue

        quest = src.quests.questMap["BeUsefull"]()
        quest.active = True
        quest.assignToCharacter(character)

        epochQuest.addQuest(quest)
        return

    def getEnemiesWithTag(self,tag):
        enemies = []
        currentTerrain = self.container.container

        foundEnemy = False
        for enemy in currentTerrain.characters:
            if enemy.tag == tag:
                enemies.append(enemy)
        for room in currentTerrain.rooms:
            for enemy in room.characters:
                if enemy.tag == tag:
                    enemies.append(enemy)

        return enemies

    def apply(self,character):
        self.changed("epoch artwork used",(character,))
        character.registers["baseCommander"] = "No"
        if character.rank == None:
            self.getInitialReward1(character)
            return

        if character.rank > 3:
            self.showLocked(character)
            return
            
        if not self.leader or self.leader.dead:
            self.leader = character

            text = """
you hereby take control over the base and are commander now.

Use the artworks to manage your quest and complete your epoch quests to get extra resources."""
            character.addMessage(text)
            submenue = src.interaction.TextMenu(text)
            character.macroState["submenue"] = submenue
            self.recalculateGlasstears(character)
            return

        super().apply(character)

    def showLocked(self,character):
        text = """
No commander was found. Operations are halted, please wait.
You have insufficent rank to take over as commander.
Be useful until commander is available.

To help you with that you got the universal leaders blessing.
(base damage +2 max health +20)
---

You were assiged the quest "be useful". 
You can decide freely how to be useful.

It is recommendet to press the "+" key to break down the quest into steps.

Completing quests at the quest artwork (QA) is a way to be usefull.
You are free to equip yourself from the bases stocks.
"""
        submenue = src.interaction.TextMenu(text)
        character.macroState["submenue"] = submenue

    def getInitialReward1(self,character):
        text = """
This base has no commander.
Activity reduced to maintenance.
"""
        character.addMessage("----------------"+text+"-----------------")

        submenue = src.interaction.TextMenu(text)
        character.macroState["submenue"] = submenue

    def getInitialReward2(self,extraParams):
        character = extraParams["character"]

        text = """
Use the assimilator to integrate into the base system.

You will recieve your duties and instructions later.
"""

        character.addMessage("----------------"+text+"-----------------")

        submenue = src.interaction.TextMenu(text)
        character.macroState["submenue"] = submenue

        for quest in character.quests:
            quest.postHandler()
        character.quests = []
        quest = src.quests.questMap["Assimilate"]()
        character.quests.append(quest)
        quest.assignToCharacter(character)
        quest.activate()
        quest.generateSubquests(character)

    def recalculateGlasstears(self,character = None):
        amount = 0
        printedMessage = False

        newRooms = len(self.container.container.rooms)-self.lastRoomReward
        if newRooms:
            stepAmount = 10*newRooms
            amount += stepAmount
            self.lastRoomReward = len(self.container.container.rooms)

            if character:
                character.addMessage("you got %s glass tears for building %s rooms"%(stepAmount,newRooms,))
                printedMessage = True

        epochsSurvived = ((src.gamestate.gamestate.tick//self.epochLength)-self.lastEpochSurvivedReward)
        self.lastEpochSurvivedReward = src.gamestate.gamestate.tick//self.epochLength
        stepAmount = epochsSurvived*self.epochSurvivedRewardAmount
        amount += stepAmount

        if character and epochsSurvived:
            character.addMessage("you got %s glass tears for surviving %s epochs"%(stepAmount,epochsSurvived,))
            printedMessage = True

        numSpawners = 0
        terrain = self.getTerrain()
        for room in terrain.rooms:
            items = room.getItemByPosition((6,6,0))
            for item in items:
                if item == self:
                    continue
                if isinstance(item, src.items.itemMap["MonsterSpawner"]):
                    numSpawners += 1
                break

        numSpawnersDestroyed = (self.lastNumSpawners-numSpawners)
        self.lastNumSpawners = numSpawners
        stepAmount = numSpawnersDestroyed*100
        amount += stepAmount

        if character and numSpawnersDestroyed:
            character.addMessage("you got %s glass tears for destroying %s hives"%(stepAmount,numSpawnersDestroyed,))
            printedMessage = True

        if character:
            character.changed(tag="got epoch evaluation")

        if not printedMessage:
            character.addMessage("you got no glass tears because you did nothing of note")

        self.changeCharges(amount)

    def autoSpendRewards(self,character = None):
        self.recalculateGlasstears()

        if character:
            self.heal(character)
            self.weaponUpgrade(character)
            self.armorUpgrade(character)
            pass
        self.spawnNewClone(character)
        self.spawnNewClone(character)
        self.rechargeTrapRooms(character)

src.items.addType(EpochArtwork)

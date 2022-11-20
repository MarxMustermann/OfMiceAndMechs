import src
import random
import copy
import json

class EpochArtwork(src.items.Item):
    """
    """


    type = "EpochArtwork"

    def __init__(self, epochLength, name="EpochArtwork", noId=False):
        """
        set up the initial state
        """

        super().__init__(display="EA", name=name)

        self.applyOptions.extend(
                        [
                                                                ("showEpochQuests", "show available epoch quests"),
                                                                ("getEpochRewards", "get epoch rewards (0)"),
                        ]
                        )
        self.applyMap = {
                            "showEpochQuests":self.showEpochQuests,
                            "getEpochRewards":self.getEpochRewards,
                        }
        self.firstUse = True
        self.epochLength = epochLength
        self.lastEpochSurvivedReward = 0

        self.charges = 0

        self.description = """
This is a one of its kind machine. It cannot be reproduced and was created by an artisan.
This artwork manages the flow of the epochs.
It generates missions and hands out rewards."""
        self.usageInfo = """
Use it by activating it. You will recieve further instructions."""

    def changeCharges(self,delta):
        self.charges += delta
        self.applyOptions[1] = ("getEpochRewards", "get epoch rewards (%s)"%(self.charges,))

    def getEpochRewards(self,character):

            options = []
            options.append(("None","(0) None"))
            options.append(("HealingOnce","(1) healing (once)"))
            amount = character.maxHealth-character.health
            amount = min(amount,self.charges*10)
            cost = amount//10
            if amount%10:
                cost += 1
            options.append(("Healing","(%s) healing"%(cost,)))
            options.append(("weapon","(1) weapon upgrade"))
            options.append(("armor","(5) armor upgrade"))
            options.append(("rank 4","(20) rank 4 NPCs"))
            options.append(("rank 5","(15) rank 5 NPCs"))
            options.append(("rank 6","(10) rank 6 NPCs"))
            options.append(("chargePersonel","(10) charge personel artwork"))
            options.append(("repairCommandCentre","(100) repair command centre"))
            options.append(("recharge trap rooms","(10) recharge trap rooms for 10"))
            options.append(("respawn scrapfield","(100) respawn scrap field"))
            options.append(("spawn lightning rods","(10) spawn 25 ligthning rods"))
            submenue = src.interaction.SelectionMenu("what reward do you desire? You currently have %s glass tears"%(self.charges,),options,targetParamName="rewardType")
            character.macroState["submenue"] = submenue
            character.macroState["submenue"].followUp = {"container":self,"method":"dispenseEpochRewards","params":{"character":character}}

    def getEpochRewardsProxy(self,extraInfo):
        self.getEpochRewards(extraInfo["character"])

    def dispenseEpochRewards(self,extraInfo):
        character = extraInfo["character"]

        if not "rewardType" in extraInfo:
            return
        
        if extraInfo["rewardType"] == "None":
            return

        text = "NIY"
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
        elif extraInfo["rewardType"] == "weapon":
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
        elif extraInfo["rewardType"] == "armor":
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
        elif extraInfo["rewardType"] == "recharge trap rooms":
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
        elif extraInfo["rewardType"] == "respawn scrapfield":
            if not self.charges > 100:
                text = "not enough glass tears"
            else:
                self.changeCharges(-100)
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

        submenue = src.interaction.TextMenu(text)
        character.macroState["submenue"] = submenue
        character.macroState["submenue"].followUp = {"container":self,"method":"getEpochRewardsProxy","params":{"character":character}}
        return

    def showEpochQuests(self,character):
        text = ""
        text += """
1. Survive this epoch.

Each epoch a wave of enemies is spawned that you need to defend against.
Survive this epoch and you get some extra resources.

The current epoch is still running for %s ticks.
You are in epoch %s.
"""%(self.epochLength-(src.gamestate.gamestate.tick%self.epochLength),src.gamestate.gamestate.tick//self.epochLength,)

        text += """
2. Destroy the spawners

The waves of enemies are spawned by spawners.

Destroy them and end the siege now

"""

        character.addMessage(text)
        submenue = src.interaction.TextMenu(text)
        character.macroState["submenue"] = submenue
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
        if character.rank == None:
            self.getInitialReward1(character)
            return

        if character.rank > 3:
            self.showLocked(character)
            return
            
        if src.gamestate.gamestate.tick//self.epochLength > self.lastEpochSurvivedReward:

            self.getEpochSurvivedReward(character)
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
The commander has fallen.
Siege ongoing.
No specific instructions available.

You have no rank.
Follow emergency protocol by integrating into the base.
"""
        character.addMessage("----------------"+text+"-----------------")

        submenue = src.interaction.TextMenu(text)
        character.macroState["submenue"] = submenue
        character.macroState["submenue"].followUp = {"container":self,"method":"getInitialReward2","params":{"character":character}}

    def getInitialReward2(self,extraParams):
        character = extraParams["character"]

        text = """
Use the assimilator to integrate into the base system.

You will recieve your duties and instructions later.
"""

        character.addMessage("----------------"+text+"-----------------")

        submenue = src.interaction.TextMenu(text)
        character.macroState["submenue"] = submenue

        character.quests = []
        quest = src.quests.Assimilate()
        character.quests.append(quest)
        quest.assignToCharacter(character)
        quest.activate()
        quest.generateSubquests(character)

    def getEpochSurvivedReward(self,character):
        amount = ((src.gamestate.gamestate.tick//self.epochLength)-self.lastEpochSurvivedReward)*30
        text = """
You survived the siege so far and a new epoch has started with the invaders dead.

For surviving and eliminating the invaders you get an additional %s glass tears.
"""%(amount,)
        self.lastEpochSurvivedReward = src.gamestate.gamestate.tick//self.epochLength
        self.changeCharges(amount)

        submenue = src.interaction.TextMenu(text)
        character.macroState["submenue"] = submenue

src.items.addType(EpochArtwork)

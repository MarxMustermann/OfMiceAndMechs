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
        self.eliminateGuardsInProgess = False
        self.eliminateGuardsDone = False
        self.eliminatePatrolsInProgess = False
        self.eliminatePatrolsDone = False
        self.eliminateLurkersInProgess = False
        self.eliminateLurkersDone = False
        self.lastEpochChargeReward = 0

        self.charges = 0

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
            options.append(("rank 3","(25) rank 3 NPCs"))
            options.append(("rank 4","(20) rank 4 NPCs"))
            options.append(("rank 5","(15) rank 5 NPCs"))
            options.append(("rank 6","(10) rank 6 NPCs"))
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
                else:
                    text = "Something went wrong. No NPC spawned. see your message log (x) for what went wrong"
                self.changeCharges(-10)
        elif extraInfo["rewardType"] == "rank 5":
            if not self.charges > 14:
                text = "not enough glass tears"
            else:
                personnelArtwork = self.container.getItemByType("PersonnelArtwork")
                char = personnelArtwork.spawnRank5(character)
                if char:
                    text = "NPC spawned"
                else:
                    text = "Something went wrong. No NPC spawned. see your message log (x) for what went wrong"
                self.changeCharges(-15)
        elif extraInfo["rewardType"] == "rank 4":
            if not self.charges > 19:
                text = "not enough glass tears"
            else:
                personnelArtwork = se5f.container.getItemByType("PersonnelArtwork")
                char = personnelArtwork.spawnRank5(character)
                if char:
                    text = "NPC spawned"
                else:
                    text = "Something went wrong. No NPC spawned. see your message log (x) for what went wrong"
                self.changeCharges(-20)
        elif extraInfo["rewardType"] == "rank 3":
            if not self.charges > 19:
                text = "not enough glass tears"
            else:
                personnelArtwork = self.container.getItemByType("PersonnelArtwork")
                char = personnelArtwork.spawnRank5(character)
                if char:
                    text = "NPC spawned"
                else:
                    text = "Something went wrong. No NPC spawned. see your message log (x) for what went wrong"
                self.changeCharges(-25)

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
"""%(self.epochLength-(src.gamestate.gamestate.tick%self.epochLength),)
        if not self.eliminateGuardsDone:
            text += """

2. Eliminate the siege guard.

There is a group of enemies near entry of the base.
They guard the entrance of the base against outbreak or resupplies.
The guards are shown as white <-

Eliminate them to start breaking up the innermost siege ring.

This will get you access to some extra resources.
"""

        elif not self.eliminatePatrolsDone:
            text += """
2. Eliminate the siege patrols.

There are groups of enemies patroling around the base.
They make movement around the base harder and hinder operations outside the base.
The patrols are shown as white X-

Eliminate them to break up the second siege ring.

This will get you access to some extra ressources.
"""

        elif not self.eliminateLurkersDone:
            text += """
2. Eliminate the lurkers.

There are groups of enemies guarding fields in this area.
They make movement around the base harder and hinder operations outside the base.
The lurkers are shown as white ss

Eliminate them to break up the second siege ring.

This will get you access to some extra ressources.
Rewards will be given even for partially completing the task.
"""


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
        if self.eliminateGuardsInProgess and not self.eliminateGuardsDone:
            enemies = self.getEnemiesWithTag("blocker")

            if not enemies:
                self.eliminateGuardsInProgess = False
                self.eliminateGuardsDone = True
                self.changeCharges(5)

                self.getSecondEpochReward(character)
                return

        if self.eliminatePatrolsInProgess and not self.eliminatePatrolsDone:
            enemies = self.getEnemiesWithTag("patrol")

            if not enemies:
                self.changeCharges(5)
                self.eliminatePatrolsInProgess = False
                self.eliminatePatrolsDone = True

                self.getThirdEpochReward(character)
                return

        if self.eliminateLurkersInProgess and not self.eliminateLurkersDone:
            enemies = self.getEnemiesWithTag("lurker")

        if self.firstUse:
            self.getFirstEpochReward(character)
            self.firstUse = False

            self.changed("first use")

            quest = src.quests.DummyQuest("defend against the siege")
            character.assignQuest(quest)
            character.registers["HOMEx"] = 7
            character.registers["HOMEy"] = 7
            return
        super().apply(character)

    def getThirdEpochReward(self,character):
        text = """
You eliminated the patrols, that breaks the second siege ring.

Next threat to remove are the enemies that are spread around in the area.
The lurkers are not partiulary agressive, but make movement harder by attacking when somebody enters the field they are guarding.

Kill them all.
To help you with that you got the universal leaders blessing.

Use this item to get further instructions and to claim your rewards.
"""
        character.baseDamage += 2
        character.addMessage("your base damage increased by 2")
        character.maxHealth += 20
        character.heal(50)
        character.addMessage("your max health increased by 20")

        submenue = src.interaction.TextMenu(text)
        character.macroState["submenue"] = submenue

        self.changeCharges(10)

        self.eliminateLurkersInProgess = True

        return


    def getSecondEpochReward(self,character):
        text = """
You eliminated the siege guards, that breaks the innermost siege ring.

Break the second siege ring now by eliminating the patrols around the base.
To help you with that you got the universal leaders blessing.

Use this item to get further instructions and to claim your rewards.
"""

        character.baseDamage += 2
        character.addMessage("your base damage increased by 2")
        character.maxHealth += 20
        character.heal(50)
        character.addMessage("your max heath increased by 20")

        submenue = src.interaction.TextMenu(text)
        character.macroState["submenue"] = submenue

        self.changeCharges(10)

        self.eliminatePatrolsInProgess = True

        return

    def getFirstEpochReward(self,character):
        text = """
* Authorisation accepted *

You are now the commander of this outpost. Your task is to lead the defence of this outpost.

You are beeing sieged and your command is to hold the position and go down in glory.

Waves will appear every %s ticks. Each wave will be stronger than the last.

Defend yourself and surive as long as possible. To help you with that you got the universal leaders blessing.

Use the artworks in this room to coordinate the bases defences and use this item again to get more instructions.
"""%(self.epochLength,)

        character.baseDamage += 2
        character.addMessage("your base damage increased by 2")
        character.maxHealth += 20
        character.addMessage("your max health increased by 20")
        character.heal(50)

        submenue = src.interaction.TextMenu(text)
        character.macroState["submenue"] = submenue

        self.changeCharges(10)

        self.eliminateGuardsInProgess = True

        return

src.items.addType(EpochArtwork)

import src


class ArenaArtwork(src.items.Item):
    """
    """


    type = "ArenaArtwork"

    def __init__(self, name="ArenaArtwork"):
        """
        set up the initial state
        """

        super().__init__(display="AA", name=name)

        self.applyOptions.extend(
                        [
                                                                ("changeBasicStats", "change basic stats"),
                                                                ("changeCombatSettings", "change combat settings"),
                                                                ("changeArenaSetting", "change arena settings"),
                        ]
                        )
        self.applyMap = {
                            "changeArenaSetting":self.changeArenaSetting,
                            "changeBasicStats":self.changeBasicStats,
                            "changeCombatSettings":self.changeCombatSettings,
                        }

        self.enemyAttackSpeed = 1
        self.enemyMovementSpeed = 1.0
        self.enemyHP = 100
        self.enemyDamage = 10

        self.playerAttackSpeed = 1
        self.playerMovementSpeed = 0.8
        self.playerHP = 100
        self.playerDamage = 10

        self.addExhaustionOnHurt = True
        self.removeExhaustionOnHeal = True
        self.reduceExhaustionOnHeal = False
        self.doubleDamageOnZeroExhaustion = True
        self.bonusDamageOnLowerExhaustion = True
        self.reduceDamageOnAttackerExhausted = True
        self.increaseDamageOnTargetExhausted = True
        self.addRandomExhaustionOnAttack = True

    def changeArenaSetting(self,character):

        text = """
"""


        options = []
        options.append(("None","leave"))
        options.append(("basic stats","basic stats"))
        options.append(("combat settings","combat settings"))
        options.append(("heavy attack settings","heavy attack settings"))

        submenue = src.interaction.SelectionMenu(text,options,targetParamName="settingCategory")
        character.macroState["submenue"] = submenue
        character.macroState["submenue"].followUp = {"container":self,"method":"changeArenaSettingSwitch","params":{"character":character}}

    def changeArenaSettingSwitch(self,extraParam):
        if not "settingCategory" in extraParam:
            return

        if extraParam["settingCategory"] == "basic stats":
            self.changeBasicStats(extraParam["character"])
            return

        if extraParam["settingCategory"] == "combat settings":
            self.changeCombatSettings(extraParam["character"])
            return

        if extraParam["settingCategory"] == "heavy attack settings":
            self.changeHeavyAttackSettings(extraParam["character"])
            return

    def changeCombatSettings(self,character):
        text = f"""
current settings:

addExhaustionOnHurt               = {self.addExhaustionOnHurt}  self.exhaustion += damage//10+1
removeExhaustionOnHeal            = {self.removeExhaustionOnHeal}  self.exhaustion = 0
reduceExhaustionOnHeal            = {self.reduceExhaustionOnHeal}  self.exhaustion = max(0,self.exhaustion-(amount//10+1))
doubleDamageOnZeroExhaustion      = {self.doubleDamageOnZeroExhaustion}  damage = damage * 2
bonusDamageOnLowerExhaustion      = {self.bonusDamageOnLowerExhaustion}  damage = damage + damage//2
reduceDamageOnAttackerExhausted   = {self.reduceDamageOnAttackerExhausted}  damage = damage//(self.exhaustion//10+1)
increaseDamageOnTargetExhausted   = {self.increaseDamageOnTargetExhausted}  damage = damage * (target.exhaustion//10+1)
addRandomExhaustionOnAttack       = {self.addRandomExhaustionOnAttack}  self.exhaustion += random.randint(1,4)
flatExhaustionAttackCost          = s  self.exhaustion += self.flatExhaustionAttackCost

"""

        options = []
        options.append(("None","back"))
        options.append(("addExhaustionOnHurt","addExhaustionOnHurt"))
        options.append(("removeExhaustionOnHeal","removeExhaustionOnHeal"))
        options.append(("reduceExhaustionOnHeal","reduceExhaustionOnHeal"))
        options.append(("doubleDamageOnZeroExhaustion","doubleDamageOnZeroExhaustion"))
        options.append(("bonusDamageOnLowerExhaustion","bonusDamageOnLowerExhaustion"))
        options.append(("reduceDamageOnAttackerExhausted","reduceDamageOnAttackerExhausted"))
        options.append(("increaseDamageOnTargetExhausted","increaseDamageOnTargetExhausted"))
        options.append(("addRandomExhaustionOnAttack","addRandomExhaustionOnAttack"))

        submenue = src.interaction.SelectionMenu(text,options,targetParamName="settingType")
        character.macroState["submenue"] = submenue
        character.macroState["submenue"].followUp = {"container":self,"method":"setSetting","params":{"character":character}}

    def changeBasicStats(self,character):

        text = f"""
current settings:

enemyAttackSpeed     = {self.enemyAttackSpeed}
enemyMovementSpeed   = {self.enemyMovementSpeed}
enemyHP              = {self.enemyHP}
enemyDamage          = {self.enemyDamage}

playerAttackSpeed    = {self.playerAttackSpeed}
playerMovementSpeed  = {self.playerMovementSpeed}
playerHP             = {self.playerHP}
playerDamage         = {self.playerDamage}


"""


        options = []
        options.append(("None","back"))
        options.append(("setEnemyAttackSpeed","setEnemyAttackSpeed"))
        options.append(("setEnemyMovementSpeed","setEnemyMovementSpeed"))
        options.append(("setEnemyHP","setEnemyHP"))
        options.append(("setEnemyDamage","setEnemyDamage"))
        options.append(("setPlayerAttackSpeed","setPlayerAttackSpeed"))
        options.append(("setPlayerMovementSpeed","setPlayerMovementSpeed"))
        options.append(("setPlayerHP","setPlayerHP"))
        options.append(("setPlayerDamage","setPlayerDamage"))

        submenue = src.interaction.SelectionMenu(text,options,targetParamName="settingType")
        character.macroState["submenue"] = submenue
        character.macroState["submenue"].followUp = {"container":self,"method":"setSetting","params":{"character":character}}

    def setSetting(self,extraParam):
        if not "settingType" in extraParam or extraParam["settingType"] == "None":
            self.changeArenaSetting(extraParam["character"])
            return

        character = extraParam["character"]
        settingType = extraParam["settingType"]

        if settingType == "addExhaustionOnHurt":
            self.addExhaustionOnHurt = not self.addExhaustionOnHurt
            for otherCharacter in self.getTerrain().characters:
                otherCharacter.addExhaustionOnHurt = self.addExhaustionOnHurt
            self.changeCombatSettings(extraParam["character"])
            return

        if settingType == "removeExhaustionOnHeal":
            self.removeExhaustionOnHeal = not self.removeExhaustionOnHeal
            for otherCharacter in self.getTerrain().characters:
                otherCharacter.removeExhaustionOnHeal = self.removeExhaustionOnHeal
            self.changeCombatSettings(extraParam["character"])
            return

        if settingType == "reduceExhaustionOnHeal":
            self.reduceExhaustionOnHeal = not self.reduceExhaustionOnHeal
            for otherCharacter in self.getTerrain().characters:
                otherCharacter.reduceExhaustionOnHeal = self.reduceExhaustionOnHeal
            self.changeCombatSettings(extraParam["character"])
            return

        if settingType == "doubleDamageOnZeroExhaustion":
            self.doubleDamageOnZeroExhaustion = not self.doubleDamageOnZeroExhaustion
            for otherCharacter in self.getTerrain().characters:
                otherCharacter.doubleDamageOnZeroExhaustion = self.doubleDamageOnZeroExhaustion
            self.changeCombatSettings(extraParam["character"])
            return

        if settingType == "bonusDamageOnLowerExhaustion":
            self.bonusDamageOnLowerExhaustion = not self.bonusDamageOnLowerExhaustion
            for otherCharacter in self.getTerrain().characters:
                otherCharacter.bonusDamageOnLowerExhaustion = self.bonusDamageOnLowerExhaustion
            self.changeCombatSettings(extraParam["character"])
            return

        if settingType == "reduceDamageOnAttackerExhausted":
            self.reduceDamageOnAttackerExhausted = not self.reduceDamageOnAttackerExhausted
            for otherCharacter in self.getTerrain().characters:
                otherCharacter.reduceDamageOnAttackerExhausted = self.reduceDamageOnAttackerExhausted
            self.changeCombatSettings(extraParam["character"])
            return

        if settingType == "increaseDamageOnTargetExhausted":
            self.increaseDamageOnTargetExhausted = not self.increaseDamageOnTargetExhausted
            for otherCharacter in self.getTerrain().characters:
                otherCharacter.increaseDamageOnTargetExhausted = self.increaseDamageOnTargetExhausted
            self.changeCombatSettings(extraParam["character"])
            return

        if settingType == "addRandomExhaustionOnAttack":
            self.addRandomExhaustionOnAttack = not self.addRandomExhaustionOnAttack
            for otherCharacter in self.getTerrain().characters:
                otherCharacter.addRandomExhaustionOnAttack = self.addRandomExhaustionOnAttack
            self.changeCombatSettings(extraParam["character"])
            return

        if not "value" in extraParam:
            submenue = src.interaction.InputMenu("input the value you want to set for %s."%(extraParam["settingType"]),targetParamName="value")
            character.macroState["submenue"] = submenue
            character.macroState["submenue"].followUp = {"container":self,"method":"setSetting","params":extraParam}
            return

        value = extraParam["value"]

        if settingType == "setEnemyAttackSpeed":
            self.enemyAttackSpeed = float(value)
            for otherCharacter in self.getTerrain().characters:
                if otherCharacter == character:
                    continue
                otherCharacter.attackSpeed = float(value)
        if settingType == "setEnemyMovementSpeed":
            self.enemyMovementSpeed = float(value)
            for otherCharacter in self.getTerrain().characters:
                if otherCharacter == character:
                    continue
                otherCharacter.movementSpeed = float(value)
        if settingType == "setEnemyHP":
            self.enemyHP = int(value)
            for otherCharacter in self.getTerrain().characters:
                if otherCharacter == character:
                    continue
                otherCharacter.health = int(value)
                otherCharacter.maxHealth = int(value)
        if settingType == "setEnemyDamage":
            self.enemyDamage = int(value)
            for otherCharacter in self.getTerrain().characters:
                if otherCharacter == character:
                    continue
                otherCharacter.baseDamage = int(value)

        if settingType == "setPlayerAttackSpeed":
            self.playerAttackSpeed = float(value)
            character.attackSpeed = float(value)

        if settingType == "setPlayerMovementSpeed":
            self.playerMovementSpeed = float(value)
            character.movementSpeed = float(value)

        if settingType == "setPlayerHP":
            self.playerHP = int(value)
            character.health = int(value)
            character.maxHealth = int(value)

        if settingType == "setPlayerDamage":
            self.playerDamage = int(value)
            character.baseDamage = int(value)

src.items.addType(ArenaArtwork)

import src


class IncreaseHealthRegen(src.statusEffects.HealthRegenBuff):
    type = "IncreaseHealthRegen"

    def __init__(self, healthBonus=2, duration=500, inventoryItem=None, reason=None):
        self.healthBonus = healthBonus
        super().__init__(duration=duration, inventoryItem=inventoryItem, reason=reason)

    def modHealthRegen(self, health):
        return health + self.healthBonus

    def getShortCode(self):
        return "frsh"

    def getLoreDescription(self):
        text = ""
        text += f"You feel you are recovering better than usual, for a time."
        return text

    def getLoreDescription(self):
        text = ""
        text += f"you feel fresh and heal better"
        return text

    def buildStatListDescription(self,description = ""):
        description = super().buildStatListDescription(description=description)
        description += f"health bonus: {self.healthBonus} extra HP per heal\n"
        return description

src.statusEffects.addType(IncreaseHealthRegen)

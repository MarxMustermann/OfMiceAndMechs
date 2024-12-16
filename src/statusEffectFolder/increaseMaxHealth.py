import src


class IncreaseMaxHealth(src.statusEffects.HealthBuff):
    type = "IncreaseMaxHealth"

    def __init__(self, healthBonus=25, duration=30, inventoryItem=None):
        self.healthBonus = healthBonus
        super().__init__(duration=duration, inventoryItem=inventoryItem)

    def modHealth(self, health):
        return health + self.healthBonus

    def getShortCode(self):
        return "maxHP"

src.statusEffects.addType(IncreaseMaxHealth)
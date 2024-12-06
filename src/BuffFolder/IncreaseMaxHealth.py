import src


class IncreaseMaxHealth(src.Buff.buffMap["HealthBuff"]):
    type = "IncreaseMaxHealth"

    def __init__(self, healthBonus=25, duration=30):
        self.healthBonus = healthBonus
        super().__init__(duration)

    def ModHealth(self, health):
        return health + self.healthBonus

    def getShortCode(self):
        return "maxHP"

src.Buff.addType(IncreaseMaxHealth)

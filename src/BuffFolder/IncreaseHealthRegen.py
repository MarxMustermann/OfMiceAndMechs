import src


class IncreaseHealthRegen(src.Buff.buffMap["HealthRegenBuff"]):
    type = "IncreaseHealthRegen"

    def __init__(self, healthBonus=2, duration=500):
        self.healthBonus = healthBonus
        super().__init__(duration)

    def ModHealthRegen(self, health):
        return health + self.healthBonus

    def getShortCode(self):
        return "regeneration"

src.Buff.addType(IncreaseHealthRegen)

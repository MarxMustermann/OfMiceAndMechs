import src


class IncreaseMaxHealth(src.Buff.buffMap["HealthBuff"]):
    type = "IncreaseMaxHealth"

    def __init__(self, HealthBonus=25, ticks=30):
        self.HealthBonus = HealthBonus
        super().__init__(ticks)

    def ModHealth(self, health):
        return health + self.HealthBonus


src.Buff.addType(IncreaseMaxHealth)

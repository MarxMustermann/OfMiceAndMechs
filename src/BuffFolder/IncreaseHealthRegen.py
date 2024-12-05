import src


class IncreaseHealthRegen(src.Buff.buffMap["HealthRegenBuff"]):
    type = "IncreaseHealthRegen"

    def __init__(self, HealthBonus=2, ticks=50):
        self.HealthBonus = HealthBonus
        super().__init__(ticks)

    def ModHealthRegen(self, health):
        return health + self.HealthBonus


src.Buff.addType(IncreaseHealthRegen)

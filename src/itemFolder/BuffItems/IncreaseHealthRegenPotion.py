import src


class IncreaseHealthRegenPotion(src.items.itemMap["BuffPotion"]):
    type = "IncreaseHealthRegenPotion"
    description = "Increases health regeneration"
    name = "refreshing Potion"

    @property
    def BuffToAdd(self):
        return src.Buff.buffMap["IncreaseHealthRegen"](healthBonus=self.healthBonus,duration=self.duration)

    def __init__(self,healthBonus=2,duration=500):
        super().__init__()

        self.healthBonus = healthBonus
        self.duration = duration
        self.walkable = True
        self.bolted = False

    def getLongInfo(self):
        return f"This Potion increases the amount you regenerate {self.healthBonus} for {self.duration} ticks"

src.items.addType(IncreaseHealthRegenPotion)

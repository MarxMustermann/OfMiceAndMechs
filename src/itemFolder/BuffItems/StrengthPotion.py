import src


class StrengthPotion(src.items.itemMap["BuffPotion"]):
    type = "StrengthPotion"
    description = "Increases damage dealt"
    name = "Potion of violent impact"

    @property
    def BuffToAdd(self):
        return src.Buff.buffMap["AddDamageOverTicks"](damageBonus=self.damageBonus,duration=self.duration)

    def __init__(self, damageBonus=10, duration=200):
        self.damageBonus = damageBonus
        self.duration = duration
        self.walkable = True
        self.bolted = False

    def getLongInfo(self):
        return f"This Potion increases your damage dealt by {self.damageBomus} for {self.duration} ticks"

src.items.addType(StrengthPotion)

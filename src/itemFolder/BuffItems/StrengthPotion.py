import src


class StrengthPotion(src.items.itemMap["BuffPotion"]):
    type = "StrengthPotion"

    @property
    def BuffToAdd(self):
        return src.Buff.buffMap["AddDamageOverTicks"]()

    def __init__(self):
        self.name = "Strength Potion"


src.items.addType(StrengthPotion)

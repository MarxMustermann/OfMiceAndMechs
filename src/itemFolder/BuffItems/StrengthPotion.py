import src


class StrengthPotion(src.items.itemMap["BuffPotion"]):
    type = "StrengthPotion"
    def __init__(self):
        self.name = "Strength Potion"

    def addBuff(self, character):
        character.buffs[src.Buff.buffMap["DamageBuff"]].append(src.Buff.buffMap["AddDamageOverTicks"]())

src.items.addType(StrengthPotion)

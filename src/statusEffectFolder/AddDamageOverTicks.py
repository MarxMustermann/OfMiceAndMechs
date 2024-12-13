import src


class AddDamageOverTicks(src.statusEffects.DamageBuff):
    type = "AddDamageOverTicks"

    def __init__(self, damageBonus=10, duration=200):
        self.damageBonus = damageBonus
        super().__init__(duration)

    def modDamage(self, attacker, attacked, bonus, damage):
        damage += self.damageBonus
        return (damage, bonus + "with added strength")

    def getShortCode(self):
        return "+mDmg"

src.statusEffects.addType(AddDamageOverTicks)

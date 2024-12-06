import src


class AddDamageOverTicks(src.statusEffects.DamageBuff):
    type = "AddDamageOverTicks"

    def __init__(self, damageBonus=10, duration=200):
        self.damageBonus = damageBonus
        super().__init__(duration)

    def ModDamage(self, attacker, attacked, bonus, damage):
        damage += self.damageBonus
        return (damage, bonus + "with added strength")

    def getShortCode(self):
        return "meleeDamage"

src.statusEffects.addType(AddDamageOverTicks)

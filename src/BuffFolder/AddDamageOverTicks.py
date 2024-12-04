import src


class AddDamageOverTicks(src.Buff.buffMap["DamageBuff"]):
    type = "AddDamageOverTicks"

    def __init__(self, DamageBonus=10, ticks=200):
        self.DamageBonus = DamageBonus
        super().__init__(ticks)

    def ModDamage(self, attacker, attacked, bonus, damage):
        damage += self.DamageBonus
        return (damage, bonus + "with added strength")


src.Buff.addType(AddDamageOverTicks)

import src


class Berserk(src.Buff.buffMap["DamageBuff"],src.Buff.buffMap["MovementBuff"]):
    type = "Berserk"

    def __init__(self, DamageBonus=5, ticks=10):
        self.DamageBonus = DamageBonus
        super().__init__(ticks)

    def ModDamage(self, attacker, attacked, bonus:str, damage):
        damage += self.DamageBonus
        if "and you gone Berserk" not in bonus:
            return (damage, bonus + "and you gone Berserk ")

        return (damage, bonus)

    def ModMovement(self, speed):
        return speed + 2
src.Buff.addType(Berserk)

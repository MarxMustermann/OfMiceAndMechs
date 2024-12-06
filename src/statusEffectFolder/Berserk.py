import src


class Berserk(src.statusEffects.DamageBuff,src.statusEffects.MovementBuff):
    type = "Berserk"

    def __init__(self, DamageBonus=2, ticks=10):
        self.DamageBonus = DamageBonus
        super().__init__(ticks)

    def ModDamage(self, attacker, attacked, bonus:str, damage):
        damage += self.DamageBonus
        if "and you gone Berserk" not in bonus:
            return (damage, bonus + "and you gone Berserk ")

        return (damage, bonus)

    def ModMovement(self, speed):
        return speed * 0.9

    def getShortCode(self):
        return "beserk"

src.statusEffects.addType(Berserk)
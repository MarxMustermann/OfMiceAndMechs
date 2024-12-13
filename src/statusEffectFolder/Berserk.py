import src


class Berserk(src.statusEffects.DamageBuff,src.statusEffects.MovementBuff):
    type = "Berserk"

    def __init__(self, damageBonus=2, ticks=10, speedUp=0.1):
        self.damageBonus = damageBonus
        self.speedUp = speedUp
        super().__init__(ticks)

    def modDamage(self, attacker, attacked, bonus:str, damage):
        damage += self.damageBonus
        if "and you gone Berserk" not in bonus:
            return (damage, bonus + "and you gone Berserk ")

        return (damage, bonus)

    def ModMovement(self, speed):
        try:
            self.speedUp
        except:
            self.speedUp = 0.1

        return speed * (1-self.speedUp)

    def getShortCode(self):
        return "BSRK"

    def getDescription(self):
        text = ""
        text += f"You are in a beserk rage and are ready to kill.\nYou chase your victims faster and hurt them harder.\n\nYou need to hurry and move fast or your rage runs out"
        text += f"\n\nReason: You killed somebody\ndamage bonus: {self.damageBonus}\nduration: {self.ticks}"
        return text

src.statusEffects.addType(Berserk)

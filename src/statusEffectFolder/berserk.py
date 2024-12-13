import src


class Berserk(src.statusEffects.DamageBuff,src.statusEffects.MovementBuff):
    type = "Berserk"

    def __init__(self, damageBonus=2, duration=10, speedUp=0.1,reason=None):
        self.damageBonus = damageBonus
        self.speedUp = speedUp
        super().__init__(duration=duration,reason=reason)

    def modDamage(self, attacker, attacked, bonus:str, damage):
        damage += self.damageBonus
        if "and you gone Berserk" not in bonus:
            return (damage, bonus + "and you gone Berserk ")

        return (damage, bonus)

    def modMovement(self, speed):
        try:
            self.speedUp
        except:
            self.speedUp = 0.1

        return speed * (1-self.speedUp)

    def getShortCode(self):
        return "BSRK"

    def getLoreDescription(self):
        text = ""
        text += f"You are in a beserk rage and are ready to kill.\nYou chase your victims faster and hurt them harder.\n\nYou need to hurry and move fast or your rage runs out"
        return text

    def buildStatListDescription(self,description = ""):
        description = super().buildStatListDescription(description=description)
        description += f"damage bonus: {self.damageBonus} damage\n"
        description += f"speed up: {self.speedUp*100}%\n"
        return description

src.statusEffects.addType(Berserk)

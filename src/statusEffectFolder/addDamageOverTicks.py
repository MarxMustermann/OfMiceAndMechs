import src


class AddDamageOverTicks(src.statusEffects.DamageBuff):
    type = "AddDamageOverTicks"

    def __init__(self, damageBonus=10, duration=200, reason=None, inventoryItem=None):
        self.damageBonus = damageBonus
        super().__init__(duration=duration,reason=reason,inventoryItem=inventoryItem)

    def modDamage(self, attacker, attacked, bonus, damage):
        damage += self.damageBonus
        return (damage, bonus + "with added strength")

    def getShortCode(self):
        return "+mDmg"

    def getLoreDescription(self):
        text = ""
        text += f"Increases the damage you deal for some time."
        return text

    def buildStatListDescription(self,description = ""):
        description = super().buildStatListDescription(description=description)
        description += f"damage bonus: {self.damageBonus} damage\n"
        return description

src.statusEffects.addType(AddDamageOverTicks)

import src

class Frenzy(src.statusEffects.AttackSpeedEffect):
    type = "Frenzy"

    def __init__(self, speedUp=0.2, duration=100, reason=None,inventoryItem=None):
        self.speedUp = speedUp
        super().__init__(duration,reason=reason,inventoryItem=inventoryItem)

    def modAttackSpeed(self, speed):
        return speed * (1-self.speedUp)

    def getShortCode(self):
        return "FRZY"

    def getLoreDescription(self):
        text = ""
        text += f"Increases the damage you deal for some time."
        return text

    def buildStatListDescription(self,description = ""):
        description = super().buildStatListDescription(description=description)
        description += f"damage bonus: {self.damageBonus} damage\n"
        return description

src.statusEffects.addType(Frenzy)

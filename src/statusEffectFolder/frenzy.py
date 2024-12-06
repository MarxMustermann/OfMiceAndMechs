import src

class Frenzy(src.statusEffects.AttackSpeedEffect):
    type = "Frenzy"

    def __init__(self, speedUp=0.8, duration=100):
        self.speedUp = speedUp
        super().__init__(duration)

    def modAttackSpeed(self, speed):
        return speed * self.speedUp

    def getShortCode(self):
        return "FRZY"

src.statusEffects.addType(Frenzy)

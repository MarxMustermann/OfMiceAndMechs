import src


class Haste(src.statusEffects.MovementBuff):
    type = "Haste"

    def __init__(self, speedUp=0.8, duration=100):
        self.speedUp = speedUp
        super().__init__(duration)

    def modMovement(self, speed):
        return speed * self.speedUp

    def getShortCode(self):
        return "HST"

src.statusEffects.addType(Haste)

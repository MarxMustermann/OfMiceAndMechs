import src


class Slowed(src.statusEffects.MovementBuff):
    type = "Slowed"

    def __init__(self, slowDown=1.1, duration=100):
        self.slowDown = slowDown
        super().__init__(duration)

    def ModMovement(self, speed):
        return speed * self.slowDown

    def getShortCode(self):
        return "SLW"

src.statusEffects.addType(Slowed)

import src


class Slowed(src.statusEffects.MovementBuff):
    type = "Slowed"

    def __init__(self, slowDown=0.1, duration=100, reason=None):
        self.slowDown = slowDown
        self.reason = reason
        super().__init__(duration)

    def modMovement(self, speed):
        return speed * (1+self.slowDown)

    def getShortCode(self):
        return "SLW"

    def getDescription(self):
        text = ""
        text += f"You were slowed and cannot move as fast any more"
        text += f"\n"
        if self.reason:
            text += f"\nreason: {self.reason}"
        text += f"\nslowDown: {self.slowDown}"
        if self.ticks:
            text += f"\nduration: {self.ticks}"
        return text

src.statusEffects.addType(Slowed)

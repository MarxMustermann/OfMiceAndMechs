import src


class Slowed(src.statusEffects.MovementBuff):
    type = "Slowed"

    def __init__(self, slowDown=0.1, duration=100, reason=None):
        self.slowDown = slowDown
        super().__init__(duration, reason=reason)

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
        text += f"\nslow down: {self.slowDown*100}%"
        if self.duration:
            text += f"\nduration: {self.duration} ticks"
        return text

src.statusEffects.addType(Slowed)

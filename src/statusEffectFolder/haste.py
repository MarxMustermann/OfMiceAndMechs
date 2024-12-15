import src


class Haste(src.statusEffects.MovementBuff):
    type = "Haste"

    def __init__(self, speedUp=0.2, duration=100, reason=None, inventoryItem=None):
        self.speedUp = speedUp
        super().__init__(duration,reason=reason,inventoryItem=inventoryItem)

    def modMovement(self, speed):
        return speed * (1-self.speedUp)

    def getShortCode(self):
        return "HST"

src.statusEffects.addType(Haste)

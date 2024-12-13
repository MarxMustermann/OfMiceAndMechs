import src


class PotionOfSpeed(src.items.itemMap["BuffPotion"]):
    type = "PotionOfSpeed"
    description = "Increases movement and combat speed"
    name = "Potion of speed"

    def getBuffsToAdd(self):
        return [
                   src.statusEffects.statusEffectMap["Haste"](speedUp=self.speedUp,duration=self.duration),
                   src.statusEffects.statusEffectMap["Frenzy"](speedUp=self.speedUp,duration=self.duration),
               ]

    def __init__(self, speedUp=0.2, duration=200):
        self.speedUp = speedUp
        self.duration = duration
        self.walkable = True
        self.bolted = False
        super().__init__()

    def getLongInfo(self):
        return f"This Potion increases your the time you need to move by {(1-self.speedUp)*100}%"

src.items.addType(PotionOfSpeed,potion=True)

import src


class IncreaseMaxHealthPotion(src.items.itemMap["BuffPotion"]):
    type = "IncreaseMaxHealthPotion"
    description = "Increases max HP"
    name = "Potion of temporary vitality"

    def __init__(self,healthBonus=25,duration=30):
        super().__init__()
        self.healthBonus = healthBonus
        self.duration = duration
        self.walkable = True
        self.bolted = False

    def getBuffsToAdd(self):
        return [src.statusEffects.statusEffectMap["IncreaseMaxHealth"](healthBonus=self.healthBonus,duration=self.duration)]

    def getLongInfo(self, character=None):
        return f"This Potion increases you max HP by {self.healthBonus} for {self.duration} ticks"

    @staticmethod
    def ingredients():
        return [src.items.itemMap["SpiderEye"]]

src.items.addType(IncreaseMaxHealthPotion,potion=True)

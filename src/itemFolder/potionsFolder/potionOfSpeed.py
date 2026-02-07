import src

class PotionOfSpeed(src.items.itemMap["BuffPotion"]):
    '''
    ingame item to get a speed buff from. single use
    '''
    type = "PotionOfSpeed"
    description = "temporarily increases movement and combat speed"
    name = "Potion of temporary speed"
    def __init__(self, speedUp=0.2, duration=200):
        self.speedUp = speedUp
        self.duration = duration
        self.walkable = True
        self.bolted = False
        super().__init__()

    def getBuffsToAdd(self):
        '''
        return the buffs to add
        '''
        return [
                   src.statusEffects.statusEffectMap["Haste"](speedUp=self.speedUp,duration=self.duration),
                   src.statusEffects.statusEffectMap["Frenzy"](speedUp=self.speedUp,duration=self.duration),
               ]

    def getLongInfo(self, character=None):
        '''
        generate a description of this item to be shown on the UI
        '''
        return f"This Potion decreases your the time you need to move by {(1-self.speedUp)*100}% for {self.duration} ticks"

    def ingredients():
        '''
        generate a list of ingredients
        '''
        return [src.items.itemMap["SpiderEye"]]

# register the item class
src.items.addType(PotionOfSpeed,potion=True)

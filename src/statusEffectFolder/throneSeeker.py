import src

class ThroneSeeker(src.statusEffects.StatusEffect):
    type = "ThroneSeeker"

    def __init__(self, damageBonus=10, duration=10, speedUp=0.1,reason=None,inventoryItem=None):
        super().__init__(duration=duration,reason=reason,inventoryItem=inventoryItem)

    def getShortCode(self):
        return "SEEK"

    def getLoreDescription(self):
        text = ""
        text += f"you are on the quest to seek and ascend the glass throne."
        return text

    def buildStatListDescription(self,description = ""):
        description = super().buildStatListDescription(description=description)
        return description

src.statusEffects.addType(ThroneSeeker)

import src

class ThroneSeeker(src.statusEffects.StatusEffect):
    type = "ThroneSeeker"

    def __init__(self, reason=None):
        super().__init__(reason=reason)

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

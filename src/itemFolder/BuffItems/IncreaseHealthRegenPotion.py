import src


class IncreaseHealthRegenPotion(src.items.itemMap["BuffPotion"]):
    type = "IncreaseHealthRegenPotion"

    @property
    def BuffToAdd(self):
        return src.Buff.buffMap["IncreaseHealthRegen"]()

    def __init__(self):
        self.name = "Increase Health Regeneration rate"


src.items.addType(IncreaseHealthRegenPotion)

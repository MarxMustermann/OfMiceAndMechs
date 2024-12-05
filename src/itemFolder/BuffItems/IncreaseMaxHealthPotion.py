import src


class IncreaseMaxHealthPotion(src.items.itemMap["BuffPotion"]):
    type = "IncreaseMaxHealthPotion"

    @property
    def BuffToAdd(self):
        return src.Buff.buffMap["IncreaseMaxHealth"]()

    def __init__(self):
        self.name = "Increase Max Health Potion"


src.items.addType(IncreaseMaxHealthPotion)

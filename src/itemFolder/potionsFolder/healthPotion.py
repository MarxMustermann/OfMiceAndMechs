import src


class HealthPotion(src.items.itemMap["Potion"]):
    type = "HealthPotion"
    description = "Increases health"
    name = "Healing Potion"

    def __init__(self, healingamount=25):
        super().__init__()
        self.healingamount = healingamount

    def apply(self, character):
        character.heal(self.healingamount, "Drank Potion")
        super().apply(character)

    def getLongInfo(self, character=None):
        return f"This Potion heals you for {self.healingamount}"

    @staticmethod
    def ingredients():
        return [src.items.itemMap["Bloom"]]

src.items.addType(HealthPotion,potion=True)

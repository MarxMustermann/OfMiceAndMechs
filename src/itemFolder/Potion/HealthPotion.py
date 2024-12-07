import src


class HealthPotion(src.items.itemMap["Potion"]):
    type = "HealthPotion"
    description = "Increases health"
    name = "Healing Potion"

    def __init__(self, healingamount=25):
        self.healingamount = healingamount

    def apply(self, character):
        character.heal(self.healingamount, "Drank Potion")
        super().apply(character)

    def getLongInfo(self):
        return f"This Potion heals you for {self.healingamount}"

src.items.addType(HealthPotion,potion=True)

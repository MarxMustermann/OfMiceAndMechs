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


src.items.addType(HealthPotion)

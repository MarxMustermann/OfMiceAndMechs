import src

class PermaMaxHealthPotion(src.items.itemMap["Potion"]):
    type = "PermaMaxHealthPotion"
    description = "Increases max health permanently"
    name = "Potion of permanent vitality"

    def __init__(self, healingamount=25):
        self.healingamount = healingamount
        super().__init__()

    def apply(self, character):
        if character.maxHealth >= 500:
            character.addMessage("you can't improve your health further.")
            return

        increaseValue = 20
        increaseValue = min(500-character.maxHealth,increaseValue)
        character.maxHealth += increaseValue

        character.addMessage(f"you drink from the flask and feal a lot healthier\nYour max health is increased by {increaseValue} to {character.maxHealth}")

        super().apply(character)

    def getLongInfo(self, character=None):
        return f"This Potion increases your max health by {self.healingamount}"

    def ingredients():
        return [src.items.itemMap["Bloom"],src.items.itemMap["ManaCrystal"]]

src.items.addType(PermaMaxHealthPotion,potion=True)

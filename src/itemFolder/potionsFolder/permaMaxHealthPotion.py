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
            character.addMessage("you can't improve your health further.\nYour ")
            return

        increaseValue = 20
        increaseValue = min(500-character.maxHealth,increaseValue)
        character.maxHealth += increaseValue

        character.addMessage(f"you drink from the flask and feal a lot healthier\nYour max health is increased by {increaseValue}")

        super().apply(character)

    def getLongInfo(self):
        return f"This Potion heals you for {self.healingamount}"

    def Ingredients():
        return [src.items.itemMap["Bloom"],src.items.itemMap["ManaCrystal"]]

src.items.addType(PermaMaxHealthPotion,potion=True)

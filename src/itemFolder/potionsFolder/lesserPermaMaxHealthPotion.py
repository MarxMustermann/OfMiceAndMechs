import src

class LesserPermaMaxHealthPotion(src.items.itemMap["Potion"]):
    type = "LesserPermaMaxHealthPotion"
    description = "Increases max health permanently up to a certain level"
    name = "lesser Potion of permanent vitality"

    def __init__(self, healing_amount=25, healing_cap=200):
        self.healing_amount = healing_amount
        self.healing_cap = healing_cap
        super().__init__()

    def apply(self, character):
        if character.maxHealth >= 200:
            character.addMessage("you can't improve your health further with this potion.\nYou need something stronger")
            return

        increaseValue = 20
        increaseValue = min(200-character.maxHealth,increaseValue)
        character.maxHealth += increaseValue

        character.addMessage(f"you drink from the flask and feal a lot healthier\nYour max health is increased by {increaseValue} to {character.maxHealth}")

        super().apply(character)

    def getLongInfo(self):
        return f"This Potion increases your max health by {self.healing_amount}"

    def ingredients():
        return [src.items.itemMap["Bloom"],src.items.itemMap["LightningRod"]]

src.items.addType(LesserPermaMaxHealthPotion,potion=True)

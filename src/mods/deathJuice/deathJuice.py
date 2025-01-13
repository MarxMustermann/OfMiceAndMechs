import src

class DeathJuicePotion(src.items.itemMap["Potion"]):
    type = "DeathJuicePotion"
    description = "kills you"
    name = "death juice Potion" 

    def __init__(self):
        super().__init__()

    def apply(self, character):
        character.die(reason="drank death juice")
        super().apply(character)

    def getLongInfo(self):
        return f"This Potion kills you"

    def Ingredients():
        return [src.items.itemMap["Scrap"]]

src.items.addType(DeathJuicePotion,potion=True)

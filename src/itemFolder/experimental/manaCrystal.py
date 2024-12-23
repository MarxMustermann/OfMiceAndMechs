import src


class ManaCrystal(src.items.Item):
    type = "ManaCrystal"
    name = "mana crystal"

    def __init__(self):
        super().__init__(display="ma")

        self.name = "mana crystal"
        self.charges = 1
        self.bolted = False
        self.walkable = True

    def apply(self, character):
        terrain = character.getTerrain()
        terrain.add_mana(self.charges)
        character.addMessage(f"The terrains mana is increased by {self.charges}")
        self.destroy()

src.items.addType(ManaCrystal)

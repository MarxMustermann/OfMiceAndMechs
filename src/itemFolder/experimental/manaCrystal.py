import src


class ManaCrystal(src.items.Item):
    '''
    ingame item used to carry mana around
    '''
    type = "ManaCrystal"
    name = "mana crystal"
    def __init__(self):
        super().__init__(display="ma")
        self.name = "mana crystal"
        self.charges = 1
        self.bolted = False
        self.walkable = True

    def apply(self, character):
        '''
        add mana to terrain
        '''
        terrain = character.getTerrain()
        terrain.add_mana(self.charges)
        character.addMessage(f"The terrains mana is increased by {self.charges}")
        self.destroy(generateScrap=False)

# register item type
src.items.addType(ManaCrystal)

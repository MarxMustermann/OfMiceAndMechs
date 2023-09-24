import src

class PoisonBloom(src.items.Item):
    """
    a poisonous plant
    """

    type = "PoisonBloom"
    name = "poison bloom"
    description = "Its spore sacks shriveled and are covered in green slime"
    usageInfo = """
You can eat it to die.
"""
    walkable = True
    dead = False
    bolted = False

    def __init__(self):
        """
        initialise internal state
        """

        super().__init__(display=src.canvas.displayChars.poisonBloom)

    def apply(self, character):
        """
        handle a character trying to use this item
        by killing the character

        Parameters:
            character: the character trying to use the item
        """

        if not self.container:
            self.dead = True

        character.die()

        if not self.dead:
            new = src.items.itemMap["PoisonBush"]()
            self.container.addItem(new,self.getPosition())

        character.addMessage("you eat the poison bloom and die")

        self.destroy(generateScrap=False)

    def pickUp(self, character):
        """
        handle getting picked up by a character

        Parameters:
            character: the character picking up the item
        """

        self.dead = True
        self.charges = 0
        super().pickUp(character)

    def destroy(self, generateScrap=True):
        """
        destroy the item without leaving residue
        """

        super().destroy(generateScrap=False)

src.items.addType(PoisonBloom)

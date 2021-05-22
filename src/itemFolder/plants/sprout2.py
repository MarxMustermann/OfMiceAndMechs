import src

class Sprout2(src.items.Item):
    """
    intermediate plant evolution
    """

    type = "Sprout2"

    def __init__(self):
        """
        set up internal state
        """

        super().__init__(display=src.canvas.displayChars.sprout2)
        self.name = "sprout2"
        self.description = "This is a mold patch that developed a bloom sprout."
        self.usageInfo = """
you can eat it to gain 25 satiation.
"""
        self.walkable = True

    def apply(self, character):
        """
        handle a character trying to use this item

        Parameters:
            character: the character trying to use this item
        """

        if not self.container:
            character.addMessage("this needs to be placed to be used")
            return

        character.satiation += 25
        if character.satiation > 1000:
            character.satiation = 1000
        self.destroy(generateScrap=False)
        character.addMessage("you eat the sprout and gain 25 satiation")

    def destroy(self, generateScrap=True):
        """
        destroy this item

        Parameters:
            generateScrap: flag to leave no residue
        """

        new = src.items.itemMap["Mold"]()
        self.container.addItem(new, self.getPosition())
        new.startSpawn()

        super().destroy(generateScrap=False)

src.items.addType(Sprout2)

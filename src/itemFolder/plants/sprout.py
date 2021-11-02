import src


class Sprout(src.items.Item):
    """
    intermediate plant evolution
    """

    type = "Sprout"
    name = "sprout"
    description = "mold patch that shows the first sign of a bloom"
    usageInfo = """
you can eat it to gain 10 satiation.
"""
    walkable = True


    def __init__(self):
        """
        initialise internal state
        """

        super().__init__(display=src.canvas.displayChars.sprout)

    def apply(self, character):
        """
        handle a character trying to use the item

        Parameters:
            character: character trying to use the item
        """

        if not self.container:
            character.addMessage("this needs to be placed outside to be used")
            return

        character.satiation += 10
        if character.satiation > 1000:
            character.satiation = 1000
        self.destroy(generateScrap=False)
        character.addMessage("you eat the sprout and gain 10 satiation")

    def destroy(self, generateScrap=True):
        """
        detroy the item

        Parameters:
            generateScrap: flag to not leave residue
        """

        new = src.items.itemMap["Mold"]()
        self.container.addItem(new, self.getPosition())
        new.startSpawn()

        super().destroy(generateScrap=False)

src.items.addType(Sprout)

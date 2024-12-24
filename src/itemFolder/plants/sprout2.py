import src


class Sprout2(src.items.Item):
    """
    intermediate plant evolution
    """

    type = "Sprout2"
    name = "sprout2"
    description = "This is a mold patch that developed a bloom sprout."
    usageInfo = """
you can eat it to gain 25 satiation.
"""
    walkable = True

    def __init__(self):
        """
        set up internal state
        """

        super().__init__(display=src.canvas.displayChars.sprout2)

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

    def getConfigurationOptions(self, character):
        """
        register the configuration options with superclass

        Parameters:
            character: the character trying to conigure the machine
        """

        options = super().getConfigurationOptions(character)
        options["b"] = ("destroy", self.destroy)
        return options

src.items.addType(Sprout2)

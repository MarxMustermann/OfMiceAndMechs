import src


class ManaCrystalizer(src.items.Item):
    """
    ingame item to destroy other items
    """

    type = "ManaCrystalizer"

    def __init__(self):
        """
        set up internal state
        """

        super().__init__(display=src.canvas.displayChars.scraper)
        self.name = "mana crystalizer"

    def apply(self, character):
        # spawn mana crystal
        new = src.items.itemMap["ManaCrystal"]()
        self.container.addItem(new,(self.xPosition + 1,self.yPosition,self.zPosition))
        character.addMessage("you crystalize some mana")

    def getConfigurationOptions(self, character):
        '''
        register the configuration options with superclass

        Parameters:
            character: the character trying to conigure the machine
        '''

        options = super().getConfigurationOptions(character)
        if self.bolted:
            options["b"] = ("unbolt", self.unboltAction)
        else:
            options["b"] = ("bolt down", self.boltAction)
        return options

src.items.addType(ManaCrystalizer)

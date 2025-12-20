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
        terrain = character.getTerrain()
        if terrain.mana > 1:
            terrain.mana -= 1
            params = {"character":character,"delayTime":1000,"action":"produce_crystal"}
            self.delayedAction(params)
        else:
            character.addMessage("no mana")

    def produce_crystal(self,params):
        character = params["character"]
        terrain = self.getTerrain()
        new = src.items.itemMap["ManaCrystal"]()
        self.container.addItem(new,(self.xPosition + 1,self.yPosition,self.zPosition))
        character.addMessage(f"you crystalize some mana\nthere is {terrain.mana} mana left")

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

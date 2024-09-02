import src


class Wall(src.items.Item):
    '''
    basic item with different appearance
    '''

    type = "Wall"
    description = "Used to build rooms."
    name = "wall"

    def __init__(self):
        '''
        set up internal state
        '''
        super().__init__(display=src.canvas.displayChars.wall)

    def getConfigurationOptions(self, character):
        """
        register the configuration options with superclass

        Parameters:
            character: the character trying to conigure the machine
        """

        options = super().getConfigurationOptions(character)
        if self.bolted:
            options["b"] = ("unbolt", self.unboltAction)
        else:
            options["b"] = ("bolt down", self.boltAction)
        return options

    def boltAction(self,character):
        self.bolted = True
        character.addMessage("you bolt down the Wall")
        character.changed("boltedItem",{"character":character,"item":self})

    def unboltAction(self,character):
        self.bolted = False
        character.addMessage("you unbolt the Wall")
        character.changed("unboltedItem",{"character":character,"item":self})

src.items.addType(Wall)

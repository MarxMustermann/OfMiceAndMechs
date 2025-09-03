import src


class Paving(src.items.Item):
    """
    ingame item used as ressource. basically does nothing
    """

    type = "Paving"
    name = "floor plate"
    description = "Used as building material for roads"
    bolted = False
    walkable = True

    def __init__(self):
        """
        set up internal state
        """

        super().__init__(display=(src.interaction.urwid.AttrSpec("#d84", "black"),"::"))

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

    def boltAction(self,character):
        '''
        bolt the item down
        '''
        self.bolted = True
        character.addMessage("you bolt down the Paving")
        character.changed("boltedItem",{"character":character,"item":self})

    def unboltAction(self,character):
        '''
        unbolt the item
        '''
        self.bolted = False
        character.addMessage("you unbolt the Paving")
        character.changed("unboltedItem",{"character":character,"item":self})

src.items.addType(Paving)

import src

class Statue(src.items.Item):
    '''
    basic item with different appearance
    '''

    type = "Statue"
    description = "Used to build rooms."
    name = "statue"

    def __init__(self):
        '''
        set up internal state
        '''
        super().__init__("@@")

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
        options["p"] = ("pray", self.pray)
        return options

    def pray(self,character):
        new = src.items.itemMap["GlassStatue"]()
        self.container.addItem(new,self.getPosition())
        self.container.removeItem(self)

    def boltAction(self,character):
        self.bolted = True
        character.addMessage("you bolt down the Statue")
        character.changed("boltedItem",{"character":character,"item":self})

    def unboltAction(self,character):
        self.bolted = False
        character.addMessage("you unbolt the Statue")
        character.changed("unboltedItem",{"character":character,"item":self})

src.items.addType(Statue)

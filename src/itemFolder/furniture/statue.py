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
            options["p"] = ("pray", self.pray)
        else:
            options["b"] = ("bolt down", self.boltAction)
        return options

    def pray(self,character):
        itemID = None
        if self.getPosition() == (2,2,0):
            itemID = 1
        if self.getPosition() == (4,2,0):
            itemID = 2
        if self.getPosition() == (7,2,0):
            itemID = 3
        if self.getPosition() == (10,2,0):
            itemID = 4
        if self.getPosition() == (10,5,0):
            itemID = 5
        if self.getPosition() == (8,5,0):
            itemID = 6
        if self.getPosition() == (7,4,0):
            itemID = 7
        new = src.items.itemMap["GlassStatue"](itemID=itemID)
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

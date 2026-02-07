import src


class FloorPlate(src.items.Item):
    """
    ingame item used as ressource for construction
    """

    type = "FloorPlate"
    bolted = False
    walkable = True
    name = "floor plate"
    description = "Used as building material and can be used to mark paths"

    def __init__(self):
        """
        set up internal state
        """

        super().__init__(display="::")

    # bad code: hacky way for bolting the item
    def apply(self, character):
        """
        handle a character trying to use the item

        Parameters:
            character: the character trying to use the item
        """

        self.character = character
        # self.addText()
        if not self.bolted:
            character.addMessage("you fix the floor plate int the ground")
            self.bolted = True

    def addText(self):
        """
        get a text from a character to set as name for this item
        """

        self.submenue = src.menuFolder.inputMenu.InputMenu("Enter the name")
        self.character.macroState["submenue"] = self.submenue
        self.character.macroState["submenue"].followUp = self.setName

    # bad code: misuse of the item
    def setName(self):
        """
        set the entered name for this floorplate
        """

        self.name = self.character.macroState["submenue"].text

    def getLongInfo(self, character=None):
        """
        return a longer than normal description text

        Returns:
            the description text
        """

        text = super().getLongInfo(character)
        text += """
item: FloorPlate

description:
%s

""" % (
            self.name
        )
        return text

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
        character.addMessage("you bolt down the FloorPlate")
        character.changed("boltedItem",{"character":character,"item":self})

    def unboltAction(self,character):
        '''
        unbolt the item
        '''
        self.bolted = False
        character.addMessage("you unbolt the FloorPlate")
        character.changed("unboltedItem",{"character":character,"item":self})

src.items.addType(FloorPlate)

import src

class FloorPlate(src.items.Item):
    """
    ingame item used as ressource for construction
    """

    type = "FloorPlate"

    def __init__(self):
        """
        set up internal state
        """

        super().__init__(display="::")

        self.bolted = False
        self.walkable = True
        self.name = "floor plate"
        self.description = "Used as building material and can be used to mark paths"

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

        self.submenue = src.interaction.InputMenu("Enter the name")
        self.character.macroState["submenue"] = self.submenue
        self.character.macroState["submenue"].followUp = self.setName

    # bad code: misuse of the item
    def setName(self):
        """
        set the entered name for this floorplate
        """

        self.name = self.character.macroState["submenue"].text

    def getLongInfo(self):
        """
        return a longer than normal description text

        Returns:
            the description text
        """
        
        text = super().getLongInfo()
        text += """
item: FloorPlate

description:
%s

""" % (
            self.name
        )
        return text

src.items.addType(FloorPlate)

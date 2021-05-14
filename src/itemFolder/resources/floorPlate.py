import src

"""
"""


class FloorPlate(src.items.Item):
    type = "FloorPlate"

    """
    call superclass constructor with modified parameters
    """

    def __init__(self):
        super().__init__(display="::")

        self.bolted = False
        self.walkable = True
        self.name = "floor plate"

    def getLongInfo(self):
        text = """
item: FloorPlate

description:
Used as building material and can be used to mark paths

"""
        return text

    def apply(self, character):
        self.character = character
        # self.addText()
        if not self.bolted:
            character.addMessage("you fix the floor plate int the ground")
            self.bolted = True

    def addText(self):
        self.submenue = src.interaction.InputMenu("Enter the name")
        self.character.macroState["submenue"] = self.submenue
        self.character.macroState["submenue"].followUp = self.setName

    def setName(self):
        self.name = self.character.macroState["submenue"].text

    def getLongInfo(self):
        text = """
item: FloorPlate

description:
%s

""" % (
            self.name
        )
        return text


src.items.addType(FloorPlate)

import src

"""
"""


class Engraver(src.items.Item):
    type = "Engraver"

    """
    call superclass constructor with modified parameters
    """

    def __init__(self):
        super().__init__(display=src.canvas.displayChars.engraver)
        self.name = "engraver"
        self.submenue = None
        self.text = None

    def apply(self, character):
        super().apply(character)

        self.character = character

        if not self.text:
            character.addMessage("starting interaction")
            self.submenue = src.interaction.InputMenu("Set the text to engrave")
            character.macroState["submenue"] = self.submenue
            character.macroState["submenue"].followUp = self.setText
        else:
            if (self.xPosition + 1, self.yPosition) in self.container.itemByCoordinates:
                self.container.itemByCoordinates[(self.xPosition + 1, self.yPosition)][
                    0
                ].customDescription = self.text

    """
    trigger production of the selected item
    """

    def setText(self):
        self.character.addMessage("stopping interaction")
        self.text = self.submenue.text
        self.submenue = None


src.items.addType(Engraver)

import src

class VatMaggot(src.items.Item):
    """
    ingame item that is a basic ressource for food production
    it also is a recreational drug
    """


    type = "VatMaggot"

    def __init__(self):
        """
        configure the super class
        """

        super().__init__(display=src.canvas.displayChars.vatMaggot)
        self.name = "vat maggot"
        self.description = "A vat maggot is the basis for food"
        self.usageInfo = """
Can be processed into bio mass by a maggot fermenter.

Activate it to eat it. Effect may vary.
"""

        self.bolted = False
        self.walkable = True

    def apply(self, character, resultType=None):
        """
        handle a character trying to eat the item

        Parameters:
            character: the character trying to eat the item
        """

        # remove resources
        character.addMessage("you consume the vat maggot")
        character.addSatiation(10,reason="eating a vat maggot")
        character.removeFrustration(25,reason="eating a vat maggot")
        if self.xPosition and self.yPosition:
            self.container.removeItem(self)
        else:
            if self in character.inventory:
                character.inventory.remove(self)
        if src.gamestate.gamestate.tick % 5 == 0:
            character.addMessage("you wretch from eating a vat magot")
            character.removeSatiation(25,reason="wretching")
            character.addFrustration(75,reason="wretching")

src.items.addType(VatMaggot)

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
        character.addSatiation(100,reason="eating a vat maggot")
        if character.maxHealth > 10:
            character.maxHealth -= 1
            character.addMessage("you loose 1 max HP for eating a vat maggot")
            if character.health > character.maxHealth:
                character.health = character.maxHealth
        if self.xPosition and self.yPosition:
            self.container.removeItem(self)
        else:
            if self in character.inventory:
                character.inventory.remove(self)

src.items.addType(VatMaggot)

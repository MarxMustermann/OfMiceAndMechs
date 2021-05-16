import src

class PressCake(src.items.Item):
    """
    ingame item that is a ressource in food production
    """

    type = "PressCake"

    def __init__(self):
        """
        configure super class
        """

        super().__init__(display=src.canvas.displayChars.pressCake)

        self.name = "press cake"
        self.description = "basic material for in food production"
        self.usageInfo = """
Can be processed into goo by a goo producer.

activate it to eat it
"""

        self.bolted = False
        self.walkable = True

    def apply(self, character):
        """
        handle a character trying to eat the press cake

        Parameters:
            character: the character trying to use the item
        """

        super().apply(character, silent=True)

        # change state
        character.addSatiation(1000,reason="ate the press cake")
        self.destroy(generateSrcap=False)

src.items.addType(PressCake)

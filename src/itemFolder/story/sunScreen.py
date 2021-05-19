import src


# bad style: silly name
class SunScreen(src.items.Item):
    """
    ingame item offering protaction against the environment
    """

    type = "SunScreen"

    def __init__(self):
        """
        set up the initial state
        """

        super().__init__(display=src.canvas.displayChars.sunScreen)

        self.name = "sun screen"

        self.walkable = True
        self.bolted = False

    def apply(self, character):
        """
        handle a character trying to use this item
        by adding the environmental protection

        Parameters:
            character: the character trying to use the item
        """

        character.addMessage("you apply the sunscreen and gain +1 heat resistance")
        character.heatResistance += 1
        self.destroy()

    def getLongInfo(self):
        """
        returns a description text

        Returns:
            the description text

        """

        return """
item: SunScreen

description:
protects from solar radiation

"""

src.items.addType(SunScreen)

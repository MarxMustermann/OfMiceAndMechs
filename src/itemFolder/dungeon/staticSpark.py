import src


class StaticSpark(src.items.Item):
    """
    ingame item acting as a key for some locks
    """

    type = "StaticSpark"

    def __init__(self):
        """
        configure super class
        """

        super().__init__(display=src.canvas.displayChars.staticSpark)

        self.name = "static spark"

        self.walkable = True
        self.bolted = False
        self.strength = 1

    # abstraction: should use the same abstractacted logic as all other food
    def apply(self, character):
        """
        handle a character trying to eat the spark

        Parameters:
            character: the character trying to eat the spark
        """

        character.addSatiation(self.strength * 50, reason="consuming a static spark")
        self.destroy(generateSrcap=False)


src.items.addType(StaticSpark)

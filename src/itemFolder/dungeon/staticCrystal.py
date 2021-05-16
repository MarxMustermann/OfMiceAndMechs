import src


class StaticCrystal(src.items.Item):
    """
    ingame item representing the "amulet of yendor" of my game
    the player is expected tp retrieve this item to exchange it for a reward
    """

    type = "StaticCrystal"

    def __init__(self):
        """
        configure the super class
        """

        super().__init__(display=src.canvas.displayChars.staticCrystal)
        self.name = "static spark"

        self.walkable = False
        self.bolted = False

src.items.addType(StaticCrystal)

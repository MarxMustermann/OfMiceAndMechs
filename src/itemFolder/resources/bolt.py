import src


class Bolt(src.items.Item):
    """
    ingame item that is a ressource and basically does nothing
    """

    type = "Bolt"

    def __init__(self):
        """
        initialise internal state
        """

        super().__init__(src.canvas.displayChars.bolt)

        self.name = "bolt"
        self.description = "Simple building material"""

        self.bolted = False
        self.walkable = True

src.items.addType(Bolt)

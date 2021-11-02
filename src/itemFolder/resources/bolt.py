import src


class Bolt(src.items.Item):
    """
    ingame item that is a ressource and basically does nothing
    """

    type = "Bolt"
    name = "bolt"
    description = "Simple building material"""

    bolted = False
    walkable = True

    def __init__(self):
        """
        initialise internal state
        """

        super().__init__(src.canvas.displayChars.bolt)

src.items.addType(Bolt)

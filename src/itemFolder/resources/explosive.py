import src


class Explosive(src.items.Item):
    """
    ingame item used as ressource to build bombs and stuff
    """

    type = "Explosive"

    def __init__(self):
        """
        initialise own state
        """

        super().__init__(display=src.canvas.displayChars.bomb)

        self.name = "explosive"
        self.description = "simple building material. Used to build bombs."

        self.bolted = False
        self.walkable = True

src.items.addType(Explosive)

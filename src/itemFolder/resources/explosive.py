import src


class Explosive(src.items.Item):
    """
    ingame item used as ressource to build bombs and stuff
    """

    type = "Explosive"

    name = "explosive"
    description = "simple building material. Used to build bombs."

    bolted = False
    walkable = True

    def __init__(self):
        """
        initialise own state
        """

        super().__init__(display=src.canvas.displayChars.bomb)


src.items.addType(Explosive)

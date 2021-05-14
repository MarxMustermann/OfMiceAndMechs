import src


class Explosive(src.items.Item):
    type = "Explosive"

    """
    almost straightforward state initialization
    """

    def __init__(self):

        super().__init__(display=src.canvas.displayChars.bomb)

        self.name = "explosive"
        self.description = "A Explosive. Simple building material. Used to build bombs."

        self.bolted = False
        self.walkable = True


src.items.addType(Explosive)

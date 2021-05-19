import src

class Radiator(src.items.Item):
    """
    ingame item used as ressource. basically does nothing
    """

    type = "Radiator"

    def __init__(self):
        """
        set up initial state
        """

        super().__init__(display = src.canvas.displayChars.coil)
        self.name = "radiator"
        self.description = "used to build items"
        self.bolted = False
        self.walkable = True

src.items.addType(Radiator)

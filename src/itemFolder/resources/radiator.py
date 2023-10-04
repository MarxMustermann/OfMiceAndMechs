import src


class Radiator(src.items.Item):
    """
    ingame item used as ressource. basically does nothing
    """

    type = "Radiator"

    name = "radiator"
    description = "used to build items"
    bolted = False
    walkable = True

    def __init__(self):
        """
        set up initial state
        """

        super().__init__(display = src.canvas.displayChars.coil)

src.items.addType(Radiator)

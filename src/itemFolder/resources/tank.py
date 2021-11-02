import src

class Tank(src.items.Item):
    """
    ingame item serving as a ressource. basically does nothing
    """

    type = "Tank"

    name = "tank"
    description = "used to build items"

    bolted = False
    walkable = True

    def __init__(self):
        """
        set up internal state
        """

        super().__init__(display=src.canvas.displayChars.tank)

src.items.addType(Tank)

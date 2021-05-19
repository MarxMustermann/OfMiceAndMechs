import src

class Tank(src.items.Item):
    """
    ingame item serving as a ressource. basically does nothing
    """

    type = "Tank"

    def __init__(self):
        """
        set up internal state
        """

        super().__init__(display=src.canvas.displayChars.tank)

        self.name = "tank"
        self.description = "used to build items"

        self.bolted = False
        self.walkable = True

src.items.addType(Tank)

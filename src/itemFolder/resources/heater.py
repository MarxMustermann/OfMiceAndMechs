import src

class Heater(src.items.Item):
    """
    ingame item used as ressource. basically does nothing
    """

    type = "Heater"

    def __init__(self):
        """
        set up internal state 
        """

        super().__init__()

        self.display = src.canvas.displayChars.heater

        self.name = "heater"
        self.description = "used to build items"

        self.bolted = False
        self.walkable = True

src.items.addType(Heater)

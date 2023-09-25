import src

class Heater(src.items.Item):
    """
    ingame item used as ressource. basically does nothing
    """

    type = "Heater"
    name = "heater"
    description = "used to build items"

    bolted = False
    walkable = True

    def __init__(self):
        """
        set up internal state
        """

        super().__init__()

        self.display = src.canvas.displayChars.heater

src.items.addType(Heater)

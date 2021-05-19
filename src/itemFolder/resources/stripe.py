import src

class Stripe(src.items.Item):
    """
    ingame item serving as a ressource. basically does nothing
    """

    type = "Stripe"

    def __init__(self, name="stripe"):
        """
        set up internal state
        """

        super().__init__(display=src.canvas.displayChars.stripe)

        self.name = "stripe"
        self.description = "used to build items"

        self.bolted = False
        self.walkable = True

src.items.addType(Stripe)

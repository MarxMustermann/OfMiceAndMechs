import src

class Stripe(src.items.Item):
    """
    ingame item serving as a ressource. basically does nothing
    """

    type = "Stripe"
    name = "stripe"
    description = "used to build items"

    bolted = False
    walkable = True

    def __init__(self, name="stripe"):
        """
        set up internal state
        """

        super().__init__(display=src.canvas.displayChars.stripe)

src.items.addType(Stripe)

import src


class Paving(src.items.Item):
    """
    ingame item used as ressource. basically does nothing
    """

    type = "Paving"
    name = "floor plate"
    description = "Used as building material for roads"
    bolted = False
    walkable = True

    def __init__(self):
        """
        set up internal state
        """

        super().__init__(display=";;")

src.items.addType(Paving)

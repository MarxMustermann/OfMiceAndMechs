import src

class Paving(src.items.Item):
    """
    ingame item used as ressource. basically does nothing
    """

    type = "Paving"

    def __init__(self):
        """
        set up internal state
        """

        super().__init__(display=";;")

        self.name = "floor plate"
        self.description = "Used as building material for roads"
        self.bolted = False
        self.walkable = True

src.items.addType(Paving)

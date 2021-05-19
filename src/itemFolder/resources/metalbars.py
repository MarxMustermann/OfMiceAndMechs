import src

class MetalBars(src.items.Item):
    """
    ingame item used as ressource. basically does nothing
    """

    type = "MetalBars"

    def __init__(self):
        """
        set up internal state 
        """

        super().__init__(display = src.canvas.displayChars.metalBars)
        self.name = "metal bar"
        self.description = "It is used by most machines and produced by a scrap compactor"
        self.walkable = True
        self.bolted = False

src.items.addType(MetalBars)

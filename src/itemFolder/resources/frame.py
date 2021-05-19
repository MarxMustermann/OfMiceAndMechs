import src

class Frame(src.items.Item):
    """
    ingame item used as ressource. basically does nothing
    """

    type = "Frame"

    def __init__(self):
        """
        set up internal state
        """

        super().__init__(display=src.canvas.displayChars.frame)

        self.name = "frame"
        self.description = "used to build items"

        self.bolted = False
        self.walkable = True

src.items.addType(Frame)

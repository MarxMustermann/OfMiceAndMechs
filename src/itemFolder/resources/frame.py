import src

class Frame(src.items.Item):
    """
    ingame item used as ressource. basically does nothing
    """

    type = "Frame"
    name = "frame"
    description = "used to build items"

    bolted = False
    walkable = True

    def __init__(self):
        """
        set up internal state
        """

        super().__init__(display=src.canvas.displayChars.frame)

src.items.addType(Frame)

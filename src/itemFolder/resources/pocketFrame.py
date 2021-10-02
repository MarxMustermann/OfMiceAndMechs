import src

class PocketFrame(src.items.Item):
    """
    ingame item used as ressource. basically does nothing
    """

    type = "PocketFrame"

    def __init__(self):
        """
        set up internal state
        """

        super().__init__(display=src.canvas.displayChars.pocketFrame)

        self.name = "pocket frame"
        self.description = "Is complex building item. It is used to build smaller things"
        self.walkable = True

src.items.addType(PocketFrame)

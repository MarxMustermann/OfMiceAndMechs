import src


class PocketFrame(src.items.Item):
    """
    ingame item used as ressource. basically does nothing
    """

    type = "PocketFrame"
    name = "pocket frame"
    description = "Is complex building item. It is used to build smaller things"
    walkable = True

    def __init__(self):
        """
        set up internal state
        """

        super().__init__(display=src.canvas.displayChars.pocketFrame)

src.items.addType(PocketFrame)

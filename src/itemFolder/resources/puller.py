import src

class Puller(src.items.Item):
    """
    ingame item used as ressource. basically does nothing
    """

    type = "puller"

    def __init__(self, name="puller", noId=False):
        """
        set up internal state
        """
        super().__init__(display=src.canvas.displayChars.puller, name=name)

        self.name = "puller"
        self.description = "used to build items"

        self.bolted = False
        self.walkable = True

src.items.addType(Puller)
src.items.itemMap["Puller"] = Puller

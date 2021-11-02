import src

class Puller(src.items.Item):
    """
    ingame item used as ressource. basically does nothing
    """

    type = "puller"

    name = "puller"
    description = "used to build items"

    bolted = False
    walkable = True

    def __init__(self, name="puller", noId=False):
        """
        set up internal state
        """
        super().__init__(display=src.canvas.displayChars.puller, name=name)

src.items.addType(Puller)
src.items.itemMap["Puller"] = Puller

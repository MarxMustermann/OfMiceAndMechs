import src

class Pusher(src.items.Item):
    """
    ingame item used as ressource. basically does nothing
    """

    type = "pusher"

    def __init__(self):
        """
        set up internal state
        """

        super().__init__(display=src.canvas.displayChars.pusher)

        self.name = "pusher"
        self.description = "used to build items"

        self.bolted = False
        self.walkable = True

src.items.addType(Pusher)
src.items.itemMap["Pusher"] = Pusher

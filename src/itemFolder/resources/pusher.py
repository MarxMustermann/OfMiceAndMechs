import src

class Pusher(src.items.Item):
    """
    ingame item used as ressource. basically does nothing
    """

    type = "pusher"

    name = "pusher"
    description = "used to build items"

    bolted = False
    walkable = True

    def __init__(self):
        """
        set up internal state
        """

        super().__init__(display=src.canvas.displayChars.pusher)

src.items.addType(Pusher)
src.items.itemMap["Pusher"] = Pusher

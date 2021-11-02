import src

# abstraction: could be very easy to replace with a json defined thing since it actually does nothing
class Mount(src.items.Item):
    """
    ingame item that is used as a ressource
    """

    type = "Mount"

    name = "mount"
    description = "a simple building material"
    bolted = False
    walkable = True

    def __init__(self):
        """
        configure super class
        """

        super().__init__(display=src.canvas.displayChars.nook)

src.items.addType(Mount)

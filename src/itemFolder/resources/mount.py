import src

# abstraction: could be very easy to replace with a json defined thing since it actually does nothing
class Mount(src.items.Item):
    """
    ingame item that is used as a ressource
    """

    type = "Mount"


    def __init__(self):
        """
        configure super class
        """

        super().__init__(display=src.canvas.displayChars.nook)

        self.name = "mount"
        self.description = "a simple building material"
        self.bolted = False
        self.walkable = True

src.items.addType(Mount)

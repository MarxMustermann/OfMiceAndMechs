import src

class Connector(src.items.Item):
    """
    ingame item that is a ressource and basically does nothing
    """

    type = "Connector"

    """
    call superclass constructor with modified parameters
    """

    def __init__(self):
        super().__init__(display=src.canvas.displayChars.connector)

        self.bolted = False
        self.name = "connector"
        self.description = "building material"
        self.walkable = True

src.items.addType(Connector)

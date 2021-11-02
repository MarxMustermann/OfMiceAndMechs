import src

class Connector(src.items.Item):
    """
    ingame item that is a ressource and basically does nothing
    """

    type = "Connector"
    bolted = False
    name = "connector"
    description = "building material"
    walkable = True


    """
    call superclass constructor with modified parameters
    """

    def __init__(self):
        super().__init__(display=src.canvas.displayChars.connector)

src.items.addType(Connector)

import src

class Case(src.items.Item):
    """
    ingame item that is a ressource and basically does nothing
    """

    type = "Case"

    def __init__(self):
        """
        set up internal state
        """

        super().__init__()
        self.display = src.canvas.displayChars.case
        self.name = "case"
        self.description = "a complex building item"

src.items.addType(Case)

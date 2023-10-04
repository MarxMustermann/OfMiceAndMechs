import src


class Case(src.items.Item):
    """
    ingame item that is a ressource and basically does nothing
    """

    type = "Case"
    name = "case"
    description = "a complex building item"

    def __init__(self):
        """
        set up internal state
        """

        super().__init__()
        self.display = src.canvas.displayChars.case

src.items.addType(Case)

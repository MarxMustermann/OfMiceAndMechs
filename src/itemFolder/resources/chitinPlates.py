import src


class ChitinPlates(src.items.Item):
    type = "ChitinPlates"
    name = "chitin plates"
    description = "item dropped from golems that can be used to improve armors"
    walkable = True
    bolted = False

    def __init__(self):
        """
        set up internal state
        """

        super().__init__(display=">")


src.items.addType(ChitinPlates)

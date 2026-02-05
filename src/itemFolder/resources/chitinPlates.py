import src


class ChitinPlates(src.items.Item):
    type = "ChitinPlates"
    name = "chitin plates"
    description = "a solid chitin plate, it can be used to improve Armor"
    walkable = True
    bolted = False

    def __init__(self):
        """
        set up internal state
        """

        super().__init__(display="> ")


src.items.addType(ChitinPlates)

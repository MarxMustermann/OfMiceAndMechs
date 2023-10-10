import src


class SpecialItem(src.items.Item):
    """
    ingame item transforming into a rip in reality when using a key
    """

    type = "SpecialItem"

    def __init__(self,epoch=0):
        """
        configure the superclass
        """

        super().__init__(display="!!")
        self.name = "special item"

        self.walkable = True
        self.bolted = False
        self.itemID = None
        self.epoch = epoch

    def getLongInfo(self):
        return f"{self.itemID}"


src.items.addType(SpecialItem)

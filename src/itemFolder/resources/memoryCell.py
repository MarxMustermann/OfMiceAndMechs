import src


class MemoryCell(src.items.Item):
    """
    ingame item used as ressource. basically does nothing
    """
    type = "MemoryCell"
    name = "memory cell"
    description = "a complex building item. It is used to build logic items"
    walkable = True

    def __init__(self):
        """
        set up internal state
        """
        super().__init__("mc")

src.items.addType(MemoryCell)

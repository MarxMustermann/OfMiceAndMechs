import src

class MemoryCell(src.items.Item):
    """
    ingame item used as ressource. basically does nothing
    """
    type = "MemoryCell"

    def __init__(self):
        """
        set up internal state
        """
        super().__init__()
        self.name = "memory cell"
        self.description = "a complex building item. It is used to build logic items"
        self.display = src.canvas.displayChars.memoryCell
        self.walkable = True

src.items.addType(MemoryCell)

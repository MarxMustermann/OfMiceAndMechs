import src

"""
"""


class MemoryCell(src.items.Item):
    type = "MemoryCell"

    """
    call superclass constructor with modified parameters
    """

    def __init__(self):
        super().__init__()
        self.name = "memory cell"
        self.display = src.canvas.displayChars.memoryCell
        self.walkable = True

    def getLongInfo(self):
        text = """

A memory cell. Is complex building item. It is used to build logic items.

"""
        return text


src.items.addType(MemoryCell)

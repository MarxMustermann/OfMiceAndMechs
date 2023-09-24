import src


class CommandBook(src.items.Item):
    type = "CommandBook"

    """
    call superclass constructor with modified parameters
    """

    def __init__(self):
        super().__init__(display="cb")

        self.name = "command book"

        self.bolted = False
        self.walkable = True
        totalCommands = 0

        self.contents = []

src.items.addType(CommandBook)

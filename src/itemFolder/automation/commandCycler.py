import src


class CommandCycler(src.items.Item):
    type = "CommandCycler"

    """
    call superclass constructor with modified parameters
    """

    def __init__(self):
        super().__init__(
            display=src.canvas.displayChars.simpleRunner,
        )
        self.name = "command cycler"
        self.commands = []
        self.commandIndex = 0

    def apply(self, character):
        super().apply(character)

        if not self.commands:
            character.addMessage(
                "no task found"
            )
        else:
            character.runCommandString(self.commands[self.commandIndex])
            self.commandIndex += 1
            if self.commandIndex >= len(self.commands):
                self.commandIndex = 0

src.items.addType(CommandCycler)

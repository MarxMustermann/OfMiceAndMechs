import src


class CommandCycler(src.items.Item):
    type = "CommandCycler"
    attributesToStore = []

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

        if not self.attributesToStore:
            self.attributesToStore.extend(super().attributesToStore)
            self.attributesToStore.extend(["command","commandIndex"])

    def apply(self, character):
        super().apply(character)

        if self.commands is None:
            character.addMessage(
                "no task found"
            )
        else:
            character.runCommandString(self.commands[self.commandIndex])
            self.commandIndex += 1
            if self.commandIndex >= len(self.commands):
                self.commandIndex = 0

src.items.addType(CommandCycler)

import src


class MemoryDump(src.items.Item):
    type = "MemoryDump"

    """
    call superclass constructor with modified parameters
    """

    def __init__(self):

        self.macros = None

        super().__init__(display=src.canvas.displayChars.memoryDump)

        self.name = "memory dump"
        self.baseName = self.name

        self.attributesToStore.extend(["macros"])

        self.setDescription()

    def setDescription(self):
        addition = ""
        if self.macros:
            addition = " (imprinted)"
        self.description = self.baseName + addition

    def setToProduce(self, toProduce):
        self.setDescription()

    """
    trigger production of a player selected item
    """

    def apply(self, character):
        super().apply(character)

        import copy

        if not self.macros is None:
            character.addMessage(
                "you overwrite your macros with the ones in your memory dump"
            )
            character.macroState["macros"] = copy.deepcopy(self.macros)
            self.macros = None
        else:
            character.addMessage("you dump your macros in the memory dump")
            self.macros = copy.deepcopy(character.macroState["macros"])

        self.setDescription()

    """
    set state from dict
    """

    def setState(self, state):
        super().setState(state)

        self.setDescription()


src.items.addType(MemoryDump)

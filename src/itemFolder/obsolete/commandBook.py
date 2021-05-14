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

        self.attributesToStore.extend(["contents"])

    def getState(self):
        state = super().getState()
        try:
            state["contents"] = self.availableChallenges
            state["knownBlueprints"] = self.knownBlueprints
        except:
            pass
        return state


src.items.addType(CommandBook)

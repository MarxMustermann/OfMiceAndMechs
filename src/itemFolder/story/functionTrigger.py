import src

#NIY: half done
class FunctionTrigger(src.items.Item):

    """
    ingame item to complete challenges outside
    """

    type = "FunctionTrigger"

    def __init__(self):
        """
        set up internal state
        """

        super().__init__(display=src.canvas.displayChars.portableChallenger)

        self.name = "story "
        self.function = None

    def apply(self, character):
        """
        handle a character tryin to use the item
        by running the challenge set

        Parameters:
            character: the character trying to use the item
        """

        self.callIndirect(self.function)

src.items.addType(FunctionTrigger)

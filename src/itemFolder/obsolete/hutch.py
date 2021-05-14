import src

"""
basically a bed with a activatable cover
"""


class Hutch(src.items.Item):
    type = "Hutch"

    def __init__(self, activated=False):
        self.activated = activated
        super().__init__()

        self.name = "Hutch"

        # bad code: set metadata for saving
        self.attributesToStore.extend(["activated"])

    def render(self):
        """
        render the hutch
        """
        if self.activated:
            return src.canvas.displayChars.hutch_occupied
        else:
            return src.canvas.displayChars.hutch_free

    """
    open/close cover
    bad code: open close methods would be nice
    """

    def apply(self, character):

        if not self.room:
            character.addMessage("this machine can only be used within rooms")
            return

        super().apply(character, silent=True)
        if not self.activated:
            self.activated = True
        else:
            self.activated = False

    """
    set state from dict
    """

    def setState(self, state):
        super().setState(state)

    def getLongInfo(self):
        text = """
item: Hutch

description:
A hutch. It is not useful.

"""
        return text


src.items.addType(Hutch)

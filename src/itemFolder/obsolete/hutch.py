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

        super().apply(character)
        if not self.activated:
            self.activated = True
        else:
            self.activated = False

    def getLongInfo(self):
        text = """
item: Hutch

description:
A hutch. It is not useful.

"""
        return text


src.items.addType(Hutch)

import src

"""
basic item with different appearance
"""


class Winch(src.items.Item):
    type = "Winch"

    """
    call superclass constructor with modified paramters
    """

    def __init__(self):
        super().__init__(
            display=src.canvas.displayChars.winch_inactive,
        )

        self.name = "winch"

    def getLongInfo(self):
        text = """
item: Winch

description:
A Winch. It is useless.

"""
        return text

src.items.addType(Winch)

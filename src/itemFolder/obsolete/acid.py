import src

"""
basic item with different appearance
"""


class Acid(src.items.Item):
    type = "Acid"

    """
    call superclass constructor with modified paramters and set some state
    """

    def __init__(self):
        self.canBurn = True
        self.type = "Acid"
        super().__init__(
            display=src.canvas.displayChars.acid,
        )

        self.name = "acid"

    def getLongInfo(self):
        text = """
item: Acid

description:
It is completely useless

"""
        return text

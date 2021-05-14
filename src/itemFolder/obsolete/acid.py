import src

"""
basic item with different appearance
"""


class Acid(src.items.Item):
    type = "Acid"

    """
    call superclass constructor with modified paramters and set some state
    """

    def __init__(self, xPosition=0, yPosition=0, name="acid", creator=None, noId=False):
        self.canBurn = True
        self.type = "Acid"
        super().__init__(
            src.canvas.displayChars.acid,
            xPosition,
            yPosition,
            name=name,
            creator=creator,
        )

    def getLongInfo(self):
        text = """
item: Acid

description:
It is completely useless

"""
        return text

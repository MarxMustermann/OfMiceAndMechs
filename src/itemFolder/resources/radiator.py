import src

"""
"""


class Radiator(src.items.Item):
    type = "Radiator"

    """
    call superclass constructor with modified parameters
    """

    def __init__(self):
        super().__init__()

        self.display = src.canvas.displayChars.coil
        self.name = "radiator"
        self.bolted = False
        self.walkable = True

    def getLongInfo(self):
        text = """
item: Radiator

description:
A radiator. Simple building material.

"""
        return text


src.items.addType(Radiator)

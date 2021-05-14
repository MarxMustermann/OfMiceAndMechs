import src

"""
"""


class Heater(src.items.Item):
    type = "Heater"

    """
    call superclass constructor with modified parameters
    """

    def __init__(self):
        super().__init__()

        self.display = src.canvas.displayChars.heater

        self.name = "heater"

        self.bolted = False
        self.walkable = True

    def getLongInfo(self):
        text = """
item: Heater

description:
A heater. Building material.

"""
        return text


src.items.addType(Heater)

import src

"""
"""


class Tank(src.items.Item):
    type = "Tank"

    """
    call superclass constructor with modified parameters
    """

    def __init__(self, name="tank", noId=False):
        super().__init__(display=src.canvas.displayChars.tank, name=name)

        self.bolted = False
        self.walkable = True

    def getLongInfo(self):
        text = """
item: Tank

description:
A tank. Building material.

"""
        return text


src.items.addType(Tank)

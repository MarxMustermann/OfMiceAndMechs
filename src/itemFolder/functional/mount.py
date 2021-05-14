import src

"""
"""


class Mount(src.items.Item):
    type = "Mount"

    """
    call superclass constructor with modified parameters
    """

    def __init__(self, name="mount", noId=False):
        super().__init__(display=src.canvas.displayChars.nook, name=name)

        self.bolted = False
        self.walkable = True

    def getLongInfo(self):
        text = """
A mount. Simple building material.

"""
        return text


src.items.addType(Mount)

import src

"""
"""


class Paving(src.items.Item):
    type = "Paving"

    """
    call superclass constructor with modified parameters
    """

    def __init__(self, name="floor plate", noId=False):
        super().__init__(display=";;", name=name)

        self.bolted = False
        self.walkable = True

    def getLongInfo(self):
        text = """
item: Paving

description:
Used as building material for roads

"""
        return text


src.items.addType(Paving)

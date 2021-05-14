import src


class TrailHead(src.items.Item):
    type = "TrailHead"

    def __init__(self):
        super().__init__(display=src.canvas.displayChars.floor_node)

        self.name = "trail head"
        self.walkable = False
        targets = []

    def getLongInfo(self):
        return """
item: TrailHead

description:
You can use it to create paths
"""


src.items.addType(TrailHead)

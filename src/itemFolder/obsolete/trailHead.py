import src

class TrailHead(src.items.Item):
    type = "TrailHead"

    def __init__(self,xPosition=0,yPosition=0,creator=None,noId=False):
        super().__init__(src.canvas.displayChars.floor_node,xPosition,yPosition,creator=creator,name="encrusted bush")
        self.walkable = False
        targets = []

    def getLongInfo(self):
        return """
item: TrailHead

description:
You can use it to create paths
"""

src.items.addType(TrailHead)

import src

class StaticShard(src.items.Item):
    type = "StaticShard"

    def __init__(self,xPosition=0,yPosition=0,creator=None,noId=False):
        super().__init__(src.canvas.displayChars.staticCrystal,xPosition,yPosition,creator=creator,name="static spark")

        self.walkable = False
        self.bolted = False

    def apply(self,character):
        new = RipInReality(creator=self)
        new.xPosition = self.xPosition
        new.yPosition = self.yPosition
        new.stable = True
        self.container.addItems([new])
        self.container.removeItem(self)

src.items.addType(StaticShard)

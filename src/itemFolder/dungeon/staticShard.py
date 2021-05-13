import src

class StaticShard(src.items.Item):
    type = "StaticShard"

    def __init__(self):
        super().__init__(display=src.canvas.displayChars.staticCrystal)
        
        self.name = "static spark"

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

import src


class StaticShard(src.items.Item):
    type = "StaticShard"

    def __init__(self):
        super().__init__(display=src.canvas.displayChars.staticCrystal)

        self.name = "static spark"

        self.walkable = False
        self.bolted = False

    def apply(self, character):
        new = src.items.itemMap["RipInReality"]()
        new.stable = True
        self.container.addItem(new,self.getPosition())
        self.container.removeItem(self)


src.items.addType(StaticShard)

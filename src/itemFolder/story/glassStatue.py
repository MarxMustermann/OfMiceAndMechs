import src


class GlassStatue(src.items.Item):
    """
    """

    type = "GlassStatue"

    def __init__(self):
        super().__init__(display="SS")
        self.name = "glass statue"

        self.walkable = False
        self.bolted = True
        self.charges = 0

    def apply(self,character):
        enemy = src.characters.Monster()
        self.container.addCharacter(enemy,self.xPosition,self.yPosition)

    def render(self):
        return "&&"

src.items.addType(GlassStatue)

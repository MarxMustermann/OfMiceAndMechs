import src

class StaticCrystal(src.items.Item):
    type = "StaticCrystal"

    def __init__(self,xPosition=0,yPosition=0,creator=None,noId=False):
        super().__init__(src.canvas.displayChars.staticCrystal,xPosition,yPosition,creator=creator,name="static spark")

        self.walkable = False
        self.bolted = False

    def apply(self,character):
        self.character.addMessage("you break reality")
        1/0

src.items.addType(StaticCrystal)

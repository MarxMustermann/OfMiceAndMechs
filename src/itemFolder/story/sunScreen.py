import src

class SunScreen(src.items.Item):
    type = "SunScreen"

    def __init__(self):
        super().__init__(display=src.canvas.displayChars.sunScreen)
        
        self.name = "sun screen"

        self.walkable = True
        self.bolted = False

    def apply(self,character):
        character.addMessage("you apply the sunscreen and gain +1 heat resistance")
        character.heatResistance += 1
        self.destroy()

    def getLongInfo(self):
        return """
item: SunScreen

description:
protects from solar radiation

"""

src.items.addType(SunScreen)

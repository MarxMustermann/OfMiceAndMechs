import src


class StaticCrystal(src.items.Item):
    type = "StaticCrystal"

    def __init__(self):
        super().__init__(display=src.canvas.displayChars.staticCrystal)
        self.name = "static spark"

        self.walkable = False
        self.bolted = False

    def apply(self, character):
        self.character.addMessage("you break reality")
        1 / 0


src.items.addType(StaticCrystal)

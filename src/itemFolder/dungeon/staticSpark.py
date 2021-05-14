import src


class StaticSpark(src.items.Item):
    type = "StaticSpark"

    def __init__(self):
        super().__init__(display=src.canvas.displayChars.staticSpark)

        self.name = "static spark"

        self.walkable = True
        self.bolted = False
        self.strength = 1

    def apply(self, character):
        character.addSatiation(self.strength * 50)
        character.addMessage(
            "you gained "
            + str(self.strength * 50)
            + " satiation from consuming the spark"
        )
        self.destroy(generateSrcap=False)


src.items.addType(StaticSpark)

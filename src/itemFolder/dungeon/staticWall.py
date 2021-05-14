import src


class StaticWall(src.items.Item):
    type = "StaticWall"

    def __init__(self):
        super().__init__(display=src.canvas.displayChars.forceField)
        self.name = "static spark"

        self.walkable = False
        self.bolted = True
        self.strength = 1

    def apply(self, character):
        staticSpark = None
        for item in character.inventory:
            if isinstance(item, StaticSpark) and item.strength >= self.strength:
                if not staticSpark or staticSpark.strength > item.strength:
                    staticSpark = item

        if not staticSpark:
            self.submenue = None
            character.addMessage("no suitable static spark")
            return

        character.inventory.remove(item)
        self.container.removeItem(self)
        character.addMessage(
            "you use a static spark on the static wall and it dissapears"
        )


src.items.addType(StaticWall)

import src

class PoisonBloom(src.items.Item):
    type = "PoisonBloom"

    def __init__(self):
        super().__init__(display=src.canvas.displayChars.poisonBloom)

        self.name = "poison bloom"
        self.walkable = True
        self.dead = False
        self.bolted = False
        self.attributesToStore.extend([
               "dead"])

    def apply(self,character):

        if not self.terrain:
            self.dead = True

        character.die()

        if not self.dead:
            new = itemMap["PoisonBush"](creator=self)
            new.xPosition = self.xPosition
            new.yPosition = self.yPosition
            self.container.addItems([new])

        character.addMessage("you eat the poison bloom and die")

        self.destroy(generateSrcap=False)

    def pickUp(self,character):
        self.dead = True
        self.charges = 0
        super().pickUp(character)

    def getLongInfo(self):
        return """
name: poison bloom

description:
This is a mold bloom. Its spore sacks shriveled and are covered in green slime.

You can eat it to die.
"""

    def destroy(self, generateSrcap=True):
        super().destroy(generateSrcap=False)

src.items.addType(PoisonBloom)

import src


class Sprout2(src.items.Item):
    type = "Sprout2"

    def __init__(self):
        super().__init__(display=src.canvas.displayChars.sprout2)
        self.name = "sprout2"
        self.walkable = True

    def apply(self, character):
        if not self.container:
            character.addMessage("this needs to be placed to be used")
            return

        character.satiation += 25
        if character.satiation > 1000:
            character.satiation = 1000
        self.destroy(generateSrcap=False)
        character.addMessage("you eat the sprout and gain 25 satiation")

    def getLongInfo(self):
        return """
item: Sprout2

description:
This is a mold patch that developed a bloom sprout.

you can eat it to gain 25 satiation.
"""

    def destroy(self, generateSrcap=True):

        new = src.items.itemMap["Mold"]()
        self.container.addItem(new, self.getPosition())
        new.startSpawn()

        super().destroy(generateSrcap=False)


src.items.addType(Sprout2)

import src

class Sprout(src.items.Item):
    type = "Sprout"

    def __init__(self):
        super().__init__(display=src.canvas.displayChars.sprout)
        
        self.name = "sprout"
        self.walkable = True

    def apply(self,character):
        if not self.container:
            character.addMessage("this needs to be placed outside to be used")
            return

        character.satiation += 10
        if character.satiation > 1000:
            character.satiation = 1000
        self.destroy(generateSrcap=False)
        character.addMessage("you eat the sprout and gain 10 satiation")

    def getLongInfo(self):
        return """
item: Sprout

description:
This is a mold patch that shows the first sign of a bloom.

you can eat it to gain 10 satiation.
"""

    def destroy(self, generateSrcap=True):

        new = src.items.itemMap["Mold"]()
        self.container.addItem(new,self.getPosition())
        new.startSpawn()

        super().destroy(generateSrcap=False)

src.items.addType(Sprout)

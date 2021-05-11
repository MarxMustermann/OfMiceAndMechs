import src

class Sprout(src.items.Item):
    type = "Sprout"

    def __init__(self,xPosition=0,yPosition=0,creator=None,noId=False):
        super().__init__(src.canvas.displayChars.sprout,xPosition,yPosition,creator=creator,name="sprout")
        self.walkable = True

    def apply(self,character):
        if not self.terrain:
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

        new = src.items.itemMap["Mold"](creator=self)
        new.xPosition = self.xPosition
        new.yPosition = self.yPosition
        self.container.addItems([new])
        new.startSpawn()

        super().destroy(generateSrcap=False)

src.items.addType(Sprout)

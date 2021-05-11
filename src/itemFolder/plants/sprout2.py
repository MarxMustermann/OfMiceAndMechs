import src

class Sprout2(src.items.Item):
    type = "Sprout2"

    def __init__(self,xPosition=0,yPosition=0,creator=None,noId=False):
        super().__init__(src.canvas.displayChars.sprout2,xPosition,yPosition,creator=creator,name="sprout2")
        self.walkable = True

    def apply(self,character):
        if not self.terrain:
            character.addMessage("this needs to be placed outside to be used")
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

        new = itemMap["Mold"](creator=self)
        new.xPosition = self.xPosition
        new.yPosition = self.yPosition
        self.container.addItems([new])
        new.startSpawn()

        super().destroy(generateSrcap=False)

src.items.addType(Sprout2)

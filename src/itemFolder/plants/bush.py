import src

class Bush(src.items.Item):
    type = "Bush"

    def __init__(self):
        super().__init__(display=src.canvas.displayChars.bush)

        self.name = "bush"

        self.walkable = False
        self.charges = 10
        self.attributesToStore.extend([
               "charges"])

    def apply(self,character):
        if self.charges > 10:
            new = itemMap["EncrustedBush"](creator=self)
            new.xPosition = self.xPosition
            new.yPosition = self.yPosition
            self.container.addItems([new])

            self.container.removeItem(self)

            character.addMessage("the bush encrusts")

        if self.charges:
            character.satiation += 5
            self.charges -= 1
            character.addMessage("you eat from the bush and gain 5 satiation")
        else:
            self.destroy()

    def getLongInfo(self):
        return "charges: %s"%(self.charges)

    def getLongInfo(self):
        return """
item: Bush

description:
This a patch of mold with multiple blooms and a network vains connecting them.

actions:
If you can eat it to gain 5 satiation.
"""

    def destroy(self, generateSrcap=True):
        new = itemMap["Coal"](creator=self)
        new.xPosition = self.xPosition
        new.yPosition = self.yPosition
        self.container.addItems([new])
        super().destroy(generateSrcap=False)

src.items.addType(Bush)

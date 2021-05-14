import src


class ReactionChamber_2(src.items.Item):
    type = "ReactionChamber_2"

    def __init__(self):

        super().__init__(display=src.canvas.displayChars.reactionChamber)
        self.name = "reactionChamber_2"

    def apply(self, character):

        coalFound = None
        flaskFound = None

        if (self.xPosition - 1, self.yPosition) in self.room.itemByCoordinates:
            for item in self.room.itemByCoordinates[
                (self.xPosition - 1, self.yPosition)
            ]:
                if item.type in "Coal":
                    coalFound = item
                if item.type in "GooFlask" and item.uses == 100:
                    flaskFound = item

        if not coalFound or not flaskFound:
            character.addMessage(
                "reagents not found. place coal and a full goo flask to the left/west"
            )
            return

        self.container.removeItem(coalFound)
        self.container.removeItem(flaskFound)

        explosive = src.items.itemMap["Explosive"]()
        explosive.xPosition = self.xPosition + 1
        explosive.yPosition = self.yPosition
        explosive.bolted = False

        byProduct = src.items.itemMap["FireCrystals"]()
        byProduct.xPosition = self.xPosition
        byProduct.yPosition = self.yPosition + 1
        byProduct.bolted = False

        self.room.addItems([
                        (byProduct,(self.xPosition + 1,self.yPosition,self.zPosition)), 
                        (explosive,(self.xPosition,self.yPosition + 1,self.zPosition)),
                        ])

    def getLongInfo(self):

        text = """

A raction chamber. It is used to mix chemicals together.

"""
        return text


src.items.addType(ReactionChamber_2)

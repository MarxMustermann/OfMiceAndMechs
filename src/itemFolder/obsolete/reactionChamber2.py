import src

class ReactionChamber_2(src.items.Item):
    type = "ReactionChamber_2"

    def __init__(self,xPosition=0,yPosition=0,amount=1,name="reactionChamber_2",creator=None,noId=False):

        super().__init__(src.canvas.displayChars.reactionChamber,xPosition,yPosition,creator=creator,name=name)

    def apply(self,character):

        coalFound = None
        flaskFound = None

        if (self.xPosition-1,self.yPosition) in self.room.itemByCoordinates:
            for item in self.room.itemByCoordinates[(self.xPosition-1,self.yPosition)]:
                if item.type in "Coal":
                    coalFound = item
                if item.type in "GooFlask" and item.uses == 100:
                    flaskFound = item

        if not coalFound or not flaskFound:
            character.addMessage("reagents not found. place coal and a full goo flask to the left/west")
            return

        self.room.removeItem(coalFound)
        self.room.removeItem(flaskFound)

        explosive = Explosive(creator=self)
        explosive.xPosition = self.xPosition+1
        explosive.yPosition = self.yPosition
        explosive.bolted = False

        byProduct = FireCrystals(creator=self)
        byProduct.xPosition = self.xPosition
        byProduct.yPosition = self.yPosition+1
        byProduct.bolted = False

        self.room.addItems([byProduct,explosive])

    def getLongInfo(self):

        text = """

A raction chamber. It is used to mix chemicals together.

"""
        return text

src.items.addType(ReactionChamber_2)

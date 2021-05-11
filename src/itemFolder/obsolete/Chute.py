import src

class Chute(src.items.Item):
    type = "Chute"

    def __init__(self,xPosition=0,yPosition=0,amount=1,name="chute",creator=None,noId=False):

        super().__init__(src.canvas.displayChars.fireCrystals,xPosition,yPosition,creator=creator,name=name)

    def apply(self,character):
        if self.xPosition == None or not self.container:
            character.addMessage("This has to be placed in order to be used")
            return

        if character.inventory:
            item = character.inventory[-1]
            character.inventory.remove(item)
            item.xPosition = self.xPosition+1
            item.yPosition = self.yPosition

            self.container.addItems([item])

src.items.addType(Chute)

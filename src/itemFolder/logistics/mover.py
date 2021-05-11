import src

class Mover(src.items.Item):
    type = "Mover"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="mover",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.sorter,xPosition,yPosition,name=name,creator=creator)

    '''
    '''
    def apply(self,character,resultType=None):
        if self.xPosition == None:
            character.addMessage("this machine needs to be placed to be used")
            return

        super().apply(character,silent=True)

        # fetch input scrap
        itemFound = None
        for item in self.container.getItemByPosition((self.xPosition-1,self.yPosition)):
            itemFound = item
            break

        if not itemFound:
            character.addMessage("nothing to be moved")
            return

        # remove resources
        self.container.removeItem(itemFound)

        targetPos = (self.xPosition+1,self.yPosition)

        itemFound.xPosition = targetPos[0]
        itemFound.yPosition = targetPos[1]


        targetFull = False
        new = itemFound
        items = self.container.getItemByPosition((self.xPosition+1,self.yPosition))
        if new.walkable:
            if len(items) > 15:
                targetFull = True
            for item in items:
                if item.walkable == False:
                    targetFull = True
        else:
            if len(items) > 1:
                targetFull = True

        if targetFull:
            character.addMessage("the target area is full, the machine does not produce anything")
            return

        self.container.addItems([itemFound])

    def getLongInfo(self):
        text = """
item: Mover

description:
A mover moves items

Place the item or items to the west of the mover.
activate the mover to move one item to the east of the mover.

"""
        return text

src.items.addType(Mover)

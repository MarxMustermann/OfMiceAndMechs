import src

class ItemDowngrader(src.items.Item):
    type = "ItemDowngrader"

    def __init__(self,xPosition=0,yPosition=0,name="item downgrader",creator=None,noId=False):
        super().__init__(xPosition,yPosition,name=name,creator=creator)

    def apply(self,character):
        if not self.room:
            character.addMessage("this machine can only be used within rooms")
            return
        if self.xPosition == None:
            character.addMessage("this machine has to be placed to be used")
            return

        inputItem = None
        if (self.xPosition-1,self.yPosition) in self.room.itemByCoordinates:
            inputItem = self.room.itemByCoordinates[(self.xPosition-1,self.yPosition)][0]

        if not inputItem:
            character.addMessage("place item to downgrade on the left")
            return

        if not hasattr(inputItem,"level"):
            character.addMessage("cannot downgrade %s"%(inputItem.type))
            return

        if inputItem.level == 1:
            character.addMessage("cannot downgrade item further")
            return

        targetFull = False
        if (self.xPosition+1,self.yPosition) in self.room.itemByCoordinates:
            if inputItem.walkable:
                if len(self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]) > 15:
                    targetFull = True
                for item in self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]:
                    if item.walkable == False:
                        targetFull = True
            else:
                if len(self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]) > 1:
                    targetFull = True

        if targetFull:
            character.addMessage("the target area is full, the machine does not produce anything")
            return

        self.room.removeItem(inputItem)

        inputItem.level -= 1
        character.addMessage("%s downgraded"%(inputItem.type,))
        inputItem.xPosition = self.xPosition+1
        inputItem.yPosition = self.yPosition
        self.room.addItems([inputItem])

    def getLongInfo(self):
        text = """
item: ItemDowngrader

description:

the item downgrader downgrades items

Place item to upgrade to the west and the downgraded item will be placed to the east.

"""
        return text


src.items.addType(ItemDowngrader)

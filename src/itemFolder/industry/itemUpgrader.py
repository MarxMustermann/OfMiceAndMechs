import src

class ItemUpgrader(src.items.Item):
    type = "ItemUpgrader"

    def __init__(self,xPosition=0,yPosition=0,name="item upgrader",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.itemUpgrader,xPosition,yPosition,name=name,creator=creator)
        self.charges = 3
        self.level = 1

        self.attributesToStore.extend([
               "charges","level"])

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
            character.addMessage("place item to upgrade on the left")
            return

        if not hasattr(inputItem,"level"):
            character.addMessage("cannot upgrade %s"%(inputItem.type))
            return

        if inputItem.level > self.level:
            character.addMessage("item upgrader needs to be upgraded to upgrade this item further")
            return

        if inputItem.level == 1:
            chance = -1
        elif inputItem.level == 2:
            chance = 0
        elif inputItem.level == 3:
            chance = 1
        elif inputItem.level == 4:
            chance = 2
        else:
            chance = 100

        success = False
        if src.gamestate.gamestate.tick % (self.charges+1) > chance:
            success = True

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

        if success:
            inputItem.upgrade()
            character.addMessage("%s upgraded"%(inputItem.type,))
            self.charges = 0
            inputItem.xPosition = self.xPosition+1
            inputItem.yPosition = self.yPosition
            self.room.addItems([inputItem])
        else:
            self.charges += 1
            character.addMessage("failed to upgrade %s - has %s charges now"%(inputItem.type,self.charges))
            inputItem.xPosition = self.xPosition
            inputItem.yPosition = self.yPosition+1
            self.room.addItems([inputItem])
            inputItem.destroy()

    def getLongInfo(self):
        text = """
item: ItemUpgrader

description:
An upgrader works from time to time. A failed upgrade will destroy the item but increase the chances of success
Place item to upgrade to the west and the upgraded item will be placed to the east.
If the upgrade fails the remains of the item will be placed to the south.

it has %s charges.

"""%(self.charges)
        return text

src.items.addType(ItemUpgrader)

import src

class Sorter(src.items.Item):
    type = "Sorter"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="sorter",creator=None,noId=False):
        self.coolDown = 10
        self.coolDownTimer = -self.coolDown

        super().__init__(src.canvas.displayChars.sorter,xPosition,yPosition,name=name,creator=creator)

        self.attributesToStore.extend([
               "coolDown","coolDownTimer"])

    '''
    '''
    def apply(self,character,resultType=None):
        super().apply(character,silent=True)

        if not self.room:
            character.addMessage("this machine can only be used within rooms")
            return

        # fetch input scrap
        itemFound = None
        if (self.xPosition-1,self.yPosition) in self.room.itemByCoordinates:
            for item in self.room.itemByCoordinates[(self.xPosition-1,self.yPosition)]:
                itemFound = item
                break

        compareItemFound = None
        if (self.xPosition,self.yPosition-1) in self.room.itemByCoordinates:
            for item in self.room.itemByCoordinates[(self.xPosition,self.yPosition-1)]:
                compareItemFound = item
                break

        if src.gamestate.gamestate.tick < self.coolDownTimer+self.coolDown:
            character.addMessage("cooldown not reached. Wait %s ticks"%(self.coolDown-(src.gamestate.gamestate.tick-self.coolDownTimer),))
            return
        self.coolDownTimer = src.gamestate.gamestate.tick

        # refuse to produce without resources
        if not itemFound:
            character.addMessage("no items available")
            return
        if not compareItemFound:
            character.addMessage("no compare items available")
            return

        # remove resources
        self.room.removeItem(itemFound)

        if itemFound.type == compareItemFound.type:
            targetPos = (self.xPosition,self.yPosition+1)
        else:
            targetPos = (self.xPosition+1,self.yPosition)

        itemFound.xPosition = targetPos[0]
        itemFound.yPosition = targetPos[1]


        targetFull = False
        new = itemFound
        if (self.xPosition+1,self.yPosition) in self.room.itemByCoordinates:
            if new.walkable:
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

        self.room.addItems([itemFound])

    def getLongInfo(self):
        text = """
item: Sorter

description:
A sorter can sort items.

To sort item with a sorter place the item you want to compare against on the north.
Place the item or items to be sorted on the west of the sorter.
Activate the sorter to sort an item.
Matching items will be moved to the south and non matching items will be moved to the east.

"""
        return text

src.items.addType(Sorter)

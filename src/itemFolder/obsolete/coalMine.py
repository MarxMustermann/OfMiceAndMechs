import src

'''
'''
class CoalMine(src.items.Item):
    type = "CoalMine"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self):
        super().__init__(display=src.canvas.displayChars.coalMine)

        self.name = "coal mine"

        self.bolted = True
        self.walkable = False

    def apply(self,character):
        if self.room:
            character.addMessage("this item cannot be used within rooms")
            return

        if not self.xPosition:
            character.addMessage("this machine has to be placed to be used")
            return

        targetFull = False
        if (self.xPosition+1,self.yPosition) in self.terrain.itemByCoordinates:
            if len(self.terrain.itemByCoordinates[(self.xPosition+1,self.yPosition)]) > 15:
                targetFull = True
            for item in self.terrain.itemByCoordinates[(self.xPosition+1,self.yPosition)]:
                if item.walkable == False:
                    targetFull = True

        if targetFull:
            character.addMessage("the target area is full, the machine does not produce anything")
            return

        character.addMessage("you mine a piece of coal")

        # spawn new item
        new = Coal(creator=self)
        new.xPosition = self.xPosition+1
        new.yPosition = self.yPosition
        new.bolted = False
        self.terrain.addItems([new])

    def getLongInfo(self):
        text = """
item: CoalMine

description:
Use it to mine coal. The coal will be dropped to the east/rigth.

"""
        return text

src.items.addType(CoalMine)

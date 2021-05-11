import src

'''
'''
class BloomShredder(src.items.Item):
    type = "BloomShredder"

    '''
    call superclass constructor with modified paramters and set some state
    '''
    def __init__(self,xPosition=None,yPosition=None,name="bloom shredder",creator=None,noId=False):
        self.activated = False
        super().__init__(src.canvas.displayChars.bloomShredder,xPosition,yPosition,name=name,creator=creator)

    '''
    '''
    def apply(self,character):
        super().apply(character,silent=True)

        if not self.room:
            character.addMessage("this machine can only be used within rooms")
            return

        items = []
        if (self.xPosition-1,self.yPosition) in self.room.itemByCoordinates:
            for item in self.room.itemByCoordinates[(self.xPosition-1,self.yPosition)]:
                if isinstance(item,Bloom):
                    items.append(item)

        # refuse to produce without resources
        if len(items) < 1:
            character.addMessage("not enough blooms")
            return
       
        targetFull = False
        if (self.xPosition+1,self.yPosition) in self.room.itemByCoordinates:
            if len(self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]) > 15:
                targetFull = True
            for item in self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]:
                if item.walkable == False:
                    targetFull = True

        if targetFull:
            character.addMessage("the target area is full, the machine does not produce anything")
            return

        # remove resources
        self.room.removeItem(items[0])

        # spawn the new item
        new = BioMass(creator=self)
        new.xPosition = self.xPosition+1
        new.yPosition = self.yPosition
        self.room.addItems([new])

    def getLongInfo(self):
        text = """
item: BloomShredder

description:
A bloom shredder produces bio mass from blooms.

Place bloom to the left/west of the bloom shredder.
Activate the bloom shredder to produce biomass.

"""
        return text

src.items.addType(BloomShredder)

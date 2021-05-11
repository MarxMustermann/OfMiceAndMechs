import src

'''
'''
class BioPress(src.items.Item):
    type = "BioPress"

    '''
    call superclass constructor with modified paramters and set some state
    '''
    def __init__(self,xPosition=None,yPosition=None,name="bio press",creator=None,noId=False):
        self.activated = False
        super().__init__(src.canvas.displayChars.bioPress,xPosition,yPosition,name=name,creator=creator)

    '''
    '''
    def apply(self,character):
        super().apply(character,silent=True)

        if not self.room:
            character.addMessage("this machine can only be used within rooms")
            return

        # fetch input scrap
        items = []
        if (self.xPosition-1,self.yPosition) in self.room.itemByCoordinates:
            for item in self.room.itemByCoordinates[(self.xPosition-1,self.yPosition)]:
                if isinstance(item,BioMass):
                    items.append(item)

        # refuse to produce without resources
        if len(items) < 10:
            character.addMessage("not enough bio mass")
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
        counter = 0
        for item in items:
            if counter >= 10:
                break
            counter += 1
            self.room.removeItem(item)

        # spawn the new item
        new = PressCake(creator=self)
        new.xPosition = self.xPosition+1
        new.yPosition = self.yPosition
        self.room.addItems([new])

    def getLongInfo(self):
        text = """
item: BioPress

description:
A bio press produces press cake from bio mass.

Place 10 bio mass to the left/west of the bio press.
Activate the bio press to produce biomass.

"""
        return text

src.items.addType(BioPress)

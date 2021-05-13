import src

'''
'''
class GooProducer(src.items.Item):
    type = "GooProducer"

    '''
    call superclass constructor with modified paramters and set some state
    '''
    def __init__(self):
        super().__init__(display=src.canvas.displayChars.gooProducer)
        self.name = "goo producer"
        self.activated = False
        self.level = 1

        # bad code: repetetive and easy to forgett
        self.attributesToStore.extend([
               "level"])
    
    '''
    '''
    def apply(self,character):
        super().apply(character,silent=True)

        if not self.room:
            character.addMessage("this machine can only be used within rooms")
            return

        # fetch input items
        items = []
        if (self.xPosition-1,self.yPosition) in self.room.itemByCoordinates:
            for item in self.room.itemByCoordinates[(self.xPosition-1,self.yPosition)]:
                if isinstance(item,PressCake):
                    items.append(item)

        # refuse to produce without resources
        if len(items) < 10+(self.level-1):
            character.addMessage("not enough press cakes")
            return
       
        # refill goo dispenser
        dispenser = None
        if (self.xPosition+1,self.yPosition) in self.room.itemByCoordinates:
            for item in self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]:
                if isinstance(item,GooDispenser):
                    dispenser = item
        if not dispenser:
            character.addMessage("no goo dispenser attached")
            return 

        if dispenser.level > self.level:
            character.addMessage("the goo producer has to have higher or equal the level as the goo dispenser")
            return 

        if dispenser.charges >= dispenser.maxCharges:
            character.addMessage("the goo dispenser is full")
            return 

        # remove resources
        counter = 0
        for item in items:
            if counter >= 10:
                break
            counter += 1
            self.room.removeItem(item)

        dispenser.addCharge()

    def getLongInfo(self):
        text = """
item: GooProducer

description:
A goo producer produces goo from press cakes.

Place 10 press cakes to the left/west of the goo producer and a goo dispenser to the rigth/east.
Activate the maggot fermenter to add a charge to the goo dispenser.

"""
        return text

src.items.addType(GooProducer)

import src

'''
'''
class Scraper(src.items.Item):
    type = "Scraper"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="scraper",creator=None,noId=False):
        self.coolDown = 10
        self.coolDownTimer = -self.coolDown
        self.charges = 3
        
        super().__init__(src.canvas.displayChars.scraper,xPosition,yPosition,name=name,creator=creator)

        self.attributesToStore.extend([
               "coolDown","coolDownTimer","charges"])

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

        if src.gamestate.gamestate.tick < self.coolDownTimer+self.coolDown and not self.charges:
            character.addMessage("cooldown not reached. Wait %s ticks"%(self.coolDown-(src.gamestate.gamestate.tick-self.coolDownTimer),))
            return

        if self.charges:
            self.charges -= 1
        else:
            self.coolDownTimer = src.gamestate.gamestate.tick

        # refuse to produce without resources
        if not itemFound:
            character.addMessage("no items available")
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
        self.room.removeItem(item)

        # spawn scrap
        new = itemMap["Scrap"](self.xPosition,self.yPosition,1,creator=self)
        new.xPosition = self.xPosition+1
        new.yPosition = self.yPosition
        self.room.addItems([new])

    def getLongInfo(self):
        text = """
item: Scrapper

description:
A scrapper shreds items to scrap.

Place an item to the west and activate the scrapper to shred an item.

"""
        return text

src.items.addType(Scraper)

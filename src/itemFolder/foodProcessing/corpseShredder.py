import src

'''
'''
class CorpseShredder(src.items.Item):
    type = "CorpseShredder"

    '''
    call superclass constructor with modified paramters and set some state
    '''
    def __init__(self,xPosition=None,yPosition=None,name="corpse shredder",creator=None,noId=False):
        self.activated = False
        super().__init__(src.canvas.displayChars.corpseShredder,xPosition,yPosition,name=name,creator=creator)

    '''
    '''
    def apply(self,character):
        super().apply(character,silent=True)

        if not self.room:
            character.addMessage("this machine can only be used within rooms")
            return

        corpse = None
        moldSpores = []
        if (self.xPosition-1,self.yPosition) in self.room.itemByCoordinates:
            for item in self.room.itemByCoordinates[(self.xPosition-1,self.yPosition)]:
                if isinstance(item,Corpse):
                    corpse = item
                if isinstance(item,MoldSpore):
                    moldSpores.append(item)

        # refuse to produce without resources
        if not corpse:
            character.addMessage("no corpse")
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
        self.room.removeItem(corpse)

        for i in range(0,corpse.charges//100):
            if moldSpores:
                self.room.removeItem(moldSpores.pop())
                new = SeededMoldFeed(creator=self)
            else:
                # spawn the new item
                new = MoldFeed(creator=self)
            new.xPosition = self.xPosition+1
            new.yPosition = self.yPosition
            self.room.addItems([new])

    def getLongInfo(self):
        text = """
item: CorpseShredder

description:
A corpse shredder produces mold feed from corpses.
If corpses and MoldSpores are supplied it produces seeded mold feed

Place corpse/mold seed to the west of the bloom shredder.
Activate the corpse shredder to produce mold feed/seeded mold feed.

"""
        return text

src.items.addType(CorpseShredder)
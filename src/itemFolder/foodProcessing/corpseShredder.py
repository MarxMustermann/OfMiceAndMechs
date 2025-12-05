import src
import random


class CorpseShredder(src.items.Item):
    """
    ingame item producing fertilizer components from corpses
    """

    type = "CorpseShredder"


    def __init__(self):
        """
        configure superclass
        """

        self.activated = False
        super().__init__(display=src.canvas.displayChars.corpseShredder)
        self.name = "corpse shredder"
        self.description = """
A corpse shredder produces mold feed from corpses.
If corpses and MoldSpores are supplied it produces seeded mold feed
"""
        self.usageInfo = """
Place corpse/mold seed to the west of the bloom shredder.
Activate the corpse shredder to produce mold feed/seeded mold feed.
"""

    def getConfigurationOptions(self, character):
        """
        register the configuration options with superclass

        Parameters:
            character: the character trying to conigure the machine
        """

        options = super().getConfigurationOptions(character)
        if self.bolted:
            options["b"] = ("unbolt", self.unboltAction)
        else:
            options["b"] = ("bolt down", self.boltAction)
        return options

    def boltAction(self,character):
        self.bolted = True
        character.addMessage("you bolt down the ScrapCompactor")
        character.changed("boltedItem",{"character":character,"item":self})

    def unboltAction(self,character):
        self.bolted = False
        character.addMessage("you unbolt the ScrapCompactor")
        character.changed("unboltedItem",{"character":character,"item":self})

    def apply(self, character):
        """
        handle a character tying to use the item to shred a corpse

        Parameters:
            character: the character using the item
        """

        character.changed("operated machine",{"character":character,"machine":self})

        corpse = None
        moldSpores = []

        # refuse to produce without resources
        corpse,moldSpores = self.checkForInputs()
        if not corpse:
            character.addMessage("no corpse")
            return

        targetFull = self.checkTargetFull()
        if targetFull:
            character.addMessage(
                "the target area is full, the machine does not produce anything"
            )
            return

        # remove resources
        self.container.removeItem(corpse)

        # spawn chunks
        for _i in range(corpse.charges // 100):
            # generate the chunk
            if moldSpores:
                self.container.removeItem(moldSpores.pop())
                new = src.items.itemMap["SeededMoldFeed"]()
            else:
                new = src.items.itemMap["MoldFeed"]()

            # splatter some chunks around
            pos = ( self.xPosition + 1,self.yPosition,self.zPosition)
            if random.random() < 0.3:
                pos = (random.randint(1,12),random.randint(1,12),0) 
                if not self.container.getPositionWalkable(pos):
                    continue
            
            # actually add the item
            self.container.addItem(new,pos)

        # show splatter animation
        center = self.getPosition()
        for tick in range(1,6):
            for offset_x in range(-2,3):
                for offset_y in range(-1,2):
                    offset = (offset_x,offset_y)
                    pos = (center[0]+offset_x,center[1]+offset_y)
                    if tick == 1:
                        if offset == (-1,0):
                            self.container.addAnimation(pos,"splatter",1,{})
                        else:
                            self.container.addAnimation(pos,"showchar",1,{"char":None})
                    elif tick == 2:
                        if offset_x < 1:
                            self.container.addAnimation(pos,"splatter",1,{})
                        else:
                            self.container.addAnimation(pos,"showchar",1,{"char":None})
                    elif tick == 3:
                        if offset_x < 2 and offset_x > -2:
                            self.container.addAnimation(pos,"splatter",1,{})
                        else:
                            self.container.addAnimation(pos,"showchar",1,{"char":None})
                    elif tick == 4:
                        if offset_x > -1:
                            self.container.addAnimation(pos,"splatter",1,{})
                        else:
                            self.container.addAnimation(pos,"showchar",1,{"char":None})
                    elif tick == 5:
                        if offset == (1,0):
                            self.container.addAnimation(pos,"splatter",1,{})
                        else:
                            self.container.addAnimation(pos,"showchar",1,{"char":None})
                    else:
                        self.container.addAnimation(pos,"splatter",1,{})
        for i in range(1,32):
            pos = (random.randint(0,12),random.randint(0,12),0)
            self.container.addAnimation(pos,"showchar",i//5,{"char":None})
            for j in range(i//4,6):
                self.container.addAnimation(pos,"splatter",1,{})

    def checkTargetFull(self):
        targetFull = False
        items = self.container.getItemByPosition((self.xPosition + 1, self.yPosition,0))
        if len(items) > 15:
            targetFull = True
        for item in items:
            if item.walkable is False:
                targetFull = True
        return targetFull

    def render(self):
        if self.readyToUse():
            return "%>"
        else:
            return self.display

    def checkForInputs(self):
        corpse = None
        moldSpores = []
        for item in self.container.getItemByPosition((self.xPosition - 1, self.yPosition, 0)):
            if item.type == "Corpse":
                corpse = item
            if item.type == "MoldSpore":
                moldSpores.append(item)
        return (corpse,moldSpores)

    def readyToUse(self):
        if not self.container:
            return False

        if not self.bolted:
            return False

        targetFull = self.checkTargetFull()
        if targetFull:
            return False

        (corpse, _moldSpores) = self.checkForInputs()
        if not corpse:
            return False

        return True

src.items.addType(CorpseShredder)

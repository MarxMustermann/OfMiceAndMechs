import src

'''
'''
class Tree(src.items.Item):
    type = "Tree"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="tree",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.tree,xPosition,yPosition,name=name,creator=creator)

        import random

        self.bolted = True
        self.walkable = False
        self.maxMaggot = random.randint(75,150)
        self.numMaggots = 0

        try:
            self.lastUse = src.gamestate.gamestate.tick
        except:
            self.lastUse = -100000

        self.attributesToStore.extend([
               "maggot","maxMaggot","lastUse"])

    def regenerateMaggots(self):
        self.numMaggots += (src.gamestate.gamestate.tick-self.lastUse)//100
        self.numMaggots = min(self.numMaggots,self.maxMaggot)

    def apply(self,character):

        if not self.terrain:
            character.addMessage("The tree has to be on the outside to be used")
            return

        self.regenerateMaggots()
        self.lastUse = src.gamestate.gamestate.tick

        character.addMessage("you harvest a vat maggot")
        character.frustration += 1

        targetFull = False
        targetPos = (self.xPosition+1,self.yPosition)
        if targetPos in self.terrain.itemByCoordinates:
            if len(self.terrain.itemByCoordinates[targetPos]) > 15:
                targetFull = True
            for item in self.terrain.itemByCoordinates[targetPos]:
                if item.walkable == False:
                    targetFull = True

        if targetFull:
            character.addMessage("the target area is full, the machine does not work")
            return

        if not self.numMaggots:
            character.addMessage("The tree has no maggots left")
            return

        # spawn new item
        self.numMaggots -= 1
        new = VatMaggot(creator=self)
        new.xPosition = self.xPosition+1
        new.yPosition = self.yPosition
        new.bolted = False
        self.terrain.addItems([new])

    def getLongInfo(self):
        self.regenerateMaggots()
        self.lastUse = src.gamestate.gamestate.tick

        text = """
item: Tree

numMaggots: %s

description:
A tree can be used as a source for vat maggots.

Activate the tree to harvest a vat maggot.

"""%(self.numMaggots,)
        return text

src.items.addType(Tree)

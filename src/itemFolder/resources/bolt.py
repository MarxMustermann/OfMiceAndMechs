import src

class Bolt(Item):
    type = "Bolt"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="bolt",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.bolt,xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True

    def getLongInfo(self):
        text = """
item: Bolt

description:
A Bolt. Simple building material.

"""
        return text

src.items.addType(Bolt)

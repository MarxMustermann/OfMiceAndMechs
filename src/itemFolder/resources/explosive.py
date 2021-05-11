import src

class Explosive(src.items.Item):
    type = "Explosive"

    '''
    almost straightforward state initialization
    '''
    def __init__(self,xPosition=0,yPosition=0,amount=1,name="explosive",creator=None,noId=False):

        super().__init__(src.canvas.displayChars.bomb,xPosition,yPosition,creator=creator,name=name)

        self.bolted = False
        self.walkable = True

    def getLongInfo(self):

        text = """

A Explosive. Simple building material. Used to build bombs.

"""
        return text

src.items.addType(Explosive)

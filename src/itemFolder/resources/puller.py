import src

'''
'''
class Puller(Item):
    type = "puller"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="puller",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.puller,xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True

    def getLongInfo(self):
        text = """
A puller. Building material.

"""
        return text

src.items.addType(Puller)

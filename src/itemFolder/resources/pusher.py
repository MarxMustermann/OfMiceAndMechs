import src

'''
'''
class Pusher(src.items.Item):
    type = "pusher"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="pusher",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.pusher,xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True

    def getLongInfo(self):
        text = """
item: Pusher

description:
A pusher. Building material.

"""
        return text

src.items.addType(Pusher)

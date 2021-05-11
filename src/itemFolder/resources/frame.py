import src

'''
'''
class Frame(src.items.Item):
    type = "Frame"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="Frame",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.frame,xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True

    def getLongInfo(self):
        text = """
item: Frame

description:
A frame. Building material.

"""
        return text

src.items.addType(Frame)

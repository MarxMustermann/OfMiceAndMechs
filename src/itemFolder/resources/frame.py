import src

'''
'''
class Frame(src.items.Item):
    type = "Frame"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,name="Frame",noId=False):
        super().__init__(display=src.canvas.displayChars.frame,name=name)

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

import src

'''
'''
class Mount(src.items.Item):
    type = "Mount"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="mount",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.nook,xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True

    def getLongInfo(self):
        text = """
A mount. Simple building material.

"""
        return text

src.items.addType(Mount)

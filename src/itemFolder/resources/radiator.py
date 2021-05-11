import src

'''
'''
class Radiator(src.items.Item):
    type = "Radiator"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="radiator",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.coil,xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True

    def getLongInfo(self):
        text = """
item: Radiator

description:
A radiator. Simple building material.

"""
        return text

src.items.addType(Radiator)

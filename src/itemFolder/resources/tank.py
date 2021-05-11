import src

'''
'''
class Tank(src.items.Item):
    type = "Tank"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="tank",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.tank,xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True

    def getLongInfo(self):
        text = """
item: Tank

description:
A tank. Building material.

"""
        return text

src.items.addType(Tank)

import src

'''
'''
class Connector(src.items.Item):
    type = "Connector"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="connector",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.connector,xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True

    def getLongInfo(self):
        text = """
item: Connector

description:
A connector. Building material.

"""
        return text

src.items.addType(Connector)

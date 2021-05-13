import src

'''
'''
class Connector(src.items.Item):
    type = "Connector"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self, name="connector",noId=False):
        super().__init__(display=src.canvas.displayChars.connector,name=name)

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

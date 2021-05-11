import src

'''
'''
class Heater(src.items.Item):
    type = "Heater"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="heater",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.heater,xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True

    def getLongInfo(self):
        text = """
item: Heater

description:
A heater. Building material.

"""
        return text


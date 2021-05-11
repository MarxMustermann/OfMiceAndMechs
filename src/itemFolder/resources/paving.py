import src

'''
'''
class Paving(Item):
    type = "Paving"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="floor plate",creator=None,noId=False):
        super().__init__(";;",xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True

    def getLongInfo(self):
        text = """
item: Paving

description:
Used as building material for roads

"""
        return text

src.items.addType(Paving)


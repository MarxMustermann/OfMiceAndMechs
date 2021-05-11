import src

'''
'''
class Case(src.items.ItemNew):
    type = "Case"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="case",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.case,xPosition,yPosition,name=name,creator=creator)

    def getLongInfo(self):
        text = """

A case. Is complex building item. It is used to build bigger things.

"""
        return text

src.items.addType(Case)


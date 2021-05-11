import src

'''
basic item with different appearance
'''
class Winch(src.items.Item):
    type = "Winch"

    '''
    call superclass constructor with modified paramters 
    '''
    def __init__(self,xPosition=0,yPosition=0,name="winch",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.winch_inactive,xPosition,yPosition,name=name,creator=creator)

    def getLongInfo(self):
        text = """
item: Winch

description:
A Winch. It is useless.

"""
        return text

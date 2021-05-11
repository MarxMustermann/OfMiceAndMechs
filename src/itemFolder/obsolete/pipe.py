import src

'''
basic item with different appearance
'''
class Pipe(src.items.ItemNew):
    type = "Pipe"

    '''
    call superclass constructor with modified paramters
    '''
    def __init__(self,xPosition=0,yPosition=0,name="Pipe",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.pipe,xPosition,yPosition,name=name,creator=creator)

    def getLongInfo(self):
        text = """
item: Pipe

description:
A Pipe. It is useless

"""
        return text

src.items.addType(Pipe)

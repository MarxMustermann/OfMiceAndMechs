import src

'''
'''
class MemoryCell(src.items.Item):
    type = "MemoryCell"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="memory cell",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.memoryCell,xPosition,yPosition,name=name,creator=creator)
        self.walkable = True

    def getLongInfo(self):
        text = """

A memory cell. Is complex building item. It is used to build logic items.

"""
        return text

src.items.addType(MemoryCell)

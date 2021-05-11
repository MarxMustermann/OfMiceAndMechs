import src

'''
basic item with different appearance
'''
class Wall(src.items.ItemNew):
    type = "Wall"

    '''
    call superclass constructor with modified paramters
    '''
    def __init__(self,xPosition=0,yPosition=0,name="Wall",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.wall,xPosition,yPosition,name=name,creator=creator)
        self.description = "Used to build rooms."

src.items.addType(Wall)

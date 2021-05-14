import src

class Wall(src.items.Item):
    '''
    basic item with different appearance
    '''

    type = "Wall"

    def __init__(self,name="Wall",noId=False):
        '''
        call superclass constructor with modified paramters
        '''
        super().__init__(display=src.canvas.displayChars.wall,name=name)
        self.description = "Used to build rooms."

src.items.addType(Wall)

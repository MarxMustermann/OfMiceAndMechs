import src

class Wall(src.items.Item):
    '''
    basic item with different appearance
    '''

    type = "Wall"
    description = "Used to build rooms."
    name = "wall"

    def __init__(self):
        '''
        set up internal state
        '''
        super().__init__(display=src.canvas.displayChars.wall)

src.items.addType(Wall)

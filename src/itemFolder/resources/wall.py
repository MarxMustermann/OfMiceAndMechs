import src

class Wall(src.items.Item):
    '''
    basic item with different appearance
    '''

    type = "Wall"

    def __init__(self):
        '''
        set up internal state
        '''
        super().__init__(display=src.canvas.displayChars.wall)
        self.description = "Used to build rooms."
        self.name = "wall"

src.items.addType(Wall)

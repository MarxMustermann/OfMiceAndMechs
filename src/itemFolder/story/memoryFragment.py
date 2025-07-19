import src


class MemoryFragment(src.items.Item):
    '''
    ingame item mainy used as ressource to buy reports
    '''
    type = "MemoryFragment"
    def __init__(self):
        super().__init__(display="mf", name="Memory Fragment")
        self.walkable = True
        self.bolted = False

# register the item class
src.items.addType(MemoryFragment, nonManufactured=True)

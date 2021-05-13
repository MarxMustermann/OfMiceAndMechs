import src

class Bolt(src.items.Item):
    type = "Bolt"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self, name="bolt",noId=False):
        super().__init__(src.canvas.displayChars.bolt,name=name)

        self.bolted = False
        self.walkable = True

    def getLongInfo(self):
        text = """
item: Bolt

description:
A Bolt. Simple building material.

"""
        return text

src.items.addType(Bolt)

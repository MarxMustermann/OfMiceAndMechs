import src

'''
basic item with different appearance
'''
class Pipe(src.items.Item):
    type = "Pipe"

    '''
    call superclass constructor with modified paramters
    '''
    def __init__(self):
        super().__init__(display=src.canvas.displayChars.pipe)
        self.name = "pipe"

    def getLongInfo(self):
        text = """
item: Pipe

description:
A Pipe. It is useless

"""
        return text

src.items.addType(Pipe)

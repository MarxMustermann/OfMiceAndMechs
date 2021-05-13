import src

'''
'''
class Pusher(src.items.Item):
    type = "pusher"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,noId=False):
        super().__init__(display=src.canvas.displayChars.pusher,noId=noId)
        name = "pusher"

        self.bolted = False
        self.walkable = True

    def getLongInfo(self):
        text = """
item: Pusher

description:
A pusher. Building material.

"""
        return text

src.items.addType(Pusher)
src.items.itemMap["Pusher"] = Pusher

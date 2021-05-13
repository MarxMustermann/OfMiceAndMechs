import src

'''
'''
class Puller(src.items.Item):
    type = "puller"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,name="puller",noId=False):
        super().__init__(display=src.canvas.displayChars.puller,name=name)

        self.bolted = False
        self.walkable = True

    def getLongInfo(self):
        text = """
A puller. Building material.

"""
        return text

src.items.addType(Puller)
src.items.itemMap["Puller"] = Puller

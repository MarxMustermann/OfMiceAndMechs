import src

'''
basically refined scrap and the default resource
'''
class MetalBars(src.items.Item):
    type = "MetalBars"

    def __init__(self):
        super().__init__()
        self.display = src.canvas.displayChars.metalBars
        self.name ="metal bar"
        self.walkable = True
        self.bolted = False 

    def getLongInfo(self):
        text = """ 
item: MetalBars

description:
A metal bar is a raw resource. It is used by most machines and produced by a scrap compactor.

"""
        return text

src.items.addType(MetalBars)

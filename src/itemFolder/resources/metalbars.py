import src

'''
basically refined scrap and the default resource
'''
class MetalBars(src.items.ItemNew):
    type = "MetalBars"

    def __init__(self,xPosition=0,yPosition=0,name="metal bar",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.metalBars,xPosition,yPosition,name=name,creator=creator)
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

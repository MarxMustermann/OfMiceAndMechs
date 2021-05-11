import src

'''
'''
class Stripe(src.items.Item):
    type = "Stripe"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="stripe",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.stripe,xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True

    def getLongInfo(self):
        text = """
item: Stripe

description:
A Stripe. Simple building material.

"""
        return text

src.items.addType(Stripe)

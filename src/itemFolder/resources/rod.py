import src

'''
'''
class Rod(src.items.Item):
    type = "Rod"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="rod",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.rod,xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True
        self.baseDamage = 6
        self.attributesToStore.extend([
               "baseDamage",
               ])

    def getLongInfo(self):
        text = """
item: Rod

description:
A rod. Simple building material.

baseDamage:
%s

"""%(self.baseDamage,)
        return text

    def apply(self,character):
        character.weapon = self
        self.container.removeItem(self)

src.items.addType(Rod)

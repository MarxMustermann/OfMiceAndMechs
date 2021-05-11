import src
import random

'''
'''
class Armor(src.items.Item):
    type = "Armor"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="armor",creator=None,noId=False):
        super().__init__("ar",xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True
        self.armorValue = random.randint(1,5)
        self.damageType = "attacked"

    def getArmorValue(self,damageType):
        if damageType == self.damageType:
            return self.armorValue
        return 0

    def getLongInfo(self):
        text = """
item: Armor

armorvalue:
%s

description:
protects you in combat

"""%(self.armorValue,)
        return text

    def apply(self,character):
        character.armor = self
        self.container.removeItem(self)

src.items.addType(Armor)

import random
import re
import src
import math


class Voider(src.items.Item):
    """
    """


    type = "Voider"

    def __init__(self,name="voider",god=None):
        """
        set up the initial state
        """

        super().__init__(display="vo", name=name)
        self.walkable = True

    def apply(self,character):

        offsets = ((1,0,0),(-1,0,0),(0,1,0),(0,-1,0))
        for offset in offsets:
            items = character.container.getItemByPosition(character.getPosition(offset=offset))
            character.container.removeItems(items)

src.items.addType(Voider)

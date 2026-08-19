import math

import src


class GeneEnhancer(src.items.Item):
    '''
    ingame item to provide characters with an oportunity to heal
    '''

    type = "GeneEnhancer"
    def __init__(self):
        super().__init__(display="GE")

        self.name = "gene enhancer"
        self.description = "it improves your stats"

        self.walkable = False
        self.bolted = False

    def getLongInfo(self, character=None):
        '''
        return a longer than normal description text

        Returns:
            the description text
        '''

        text = super().getLongInfo(character)
        text += f"""
This item can enhance your stats.
"""
        return text

    def getIngredients(self,character):
        '''
        get input ressources
        '''
        if not self.container:
            return []

        vials = []

        for offset in [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0)]:
            items = self.container.getItemByPosition(self.getPosition(offset))
            for item in items:
                if item.type == "Vial":
                    vials.append(item)

        if not vials:
            for item in character.inventory:
                if item.type == "Vial":
                    vials.append(item)

        return vials

    def apply(self, character):
        '''
        handle a character trying to use this item

        Parameters:
            character: the character trying to use this item
        '''

        vials = self.getIngredients(character)
        if not vials:
            character.addMessage("you need to have a Vials in your inventory or in the input stockpiles")
            return

        character.maxHealth 

        character.container.addAnimation(character.getPosition(),"showchar",1,{"char":[(src.interaction.urwid.AttrSpec("#f00", "#000"), "++")]})

# register the item type
src.items.addType(GeneEnhancer)

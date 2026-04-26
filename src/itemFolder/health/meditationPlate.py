import src

import random

class MeditationPlate(src.items.Item):
    """
    ingame item used to give the player hints to treasure
    """
    type = "MeditationPlate"
    def __init__(self,inscription=None):
        super().__init__(display=(src.interaction.urwid.AttrSpec("#3c3","#000"),"::"))
        self.name = "meditation plate"
        self.description = "a place to find yourself and heal"

        self.bolted = True
        self.walkable = True

    def apply(self, character):
        """
        Parameters:
            character: the character trying to use the item
        """

        self.delayedAction({"action":self.heal,"character":character,"delayTime":100,"description":random.choice(["you meditate","you introspect","you make peace with yourself"])+"\n"})

    def heal(self, extraParams):
        character = extraParams["character"]

        character.changed("meditated",{"character":character,"item":self})

        heal_amount = max(50-character.health,0)

        character.heal(heal_amount,reason="meditation")

        if heal_amount:
            text = f"you heal by {heal_amount} HP to reach 50 HP"
            character.showTextMenu(text)
            character.addMessage(text)
            return
        else:
            text = "you don't heal, you already have 50 health"
            character.showTextMenu(text)
            character.addMessage(text)
            return

src.items.addType(MeditationPlate)

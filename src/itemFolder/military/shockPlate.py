import random

import src


class ShockPlate(src.items.Item):
    """
    ingame item used as ressource to build bombs and stuff
    should have the habit to explode at inconvienent times
    """

    type = "ShockPlate"
    walkable = True
    name = "shockplate"
    isStepOnActive = True
    bolted = False

    def __init__(self):
        """
        set up internal state
        """

        super().__init__(display=";;")

        self.active = True
        self.charges = 0
        self.faction = None

    def getLongInfo(self):
        """
        return a longer than normal description text

        Returns:
            the description text
        """

        text = super().getLongInfo()
        text += f"""

This item shocks enemies when stepped on.

"""
        return text

    def configure(self,character):
        """
        if self.active:
            character.addMessage("you defuse the landmine, that takes 30 ticks")
            character.takeTime(30,"defused")
            self.active = False
        else:
            character.addMessage("you fuse the landmine again, that takes 50 ticks")
            character.takeTime(50,"fused")
            self.active = True
        """

    def doStepOnAction(self, character):
        if self.charges and character.faction != self.faction:
            character.addMessage("you step on a ShockPlate")
            1/0

    def render(self):
        if self.charges:
            return ";;"
        else:
            return ";:"

    def apply(self, character):
        """
        handle a character trying to use this item
        by starting to explode

        Parameters:
            character: the character trying to use the item
        """

        self.faction = character.faction
        self.charges = 1

src.items.addType(ShockPlate)

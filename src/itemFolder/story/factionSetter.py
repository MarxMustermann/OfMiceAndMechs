import src
import random

class FactionSetter(src.items.Item):
    """
    """

    type = "FactionSetter"

    def __init__(self,epoch=0):
        """
        configure the superclass
        """

        super().__init__(display="FS")
        self.faction = None

        self.walkable = False
        self.bolted = True

    def apply(self,character):
        character.faction = self.faction
        character.addMessage(f"your faction was changed to {self.faction}")
        character.changed("set faction")

        text = f"""
You insert your head into the machine.
It claws into your head and connects to you implant.

It changes your implant and sets your faction marker to {self.faction}.
"""
        character.macroState["submenue"] = src.interaction.TextMenu(text)

src.items.addType(FactionSetter)
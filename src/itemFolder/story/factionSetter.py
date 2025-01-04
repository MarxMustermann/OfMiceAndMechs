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

        self.container.addAnimation(character.getPosition(),"showchar",1,{"char":"OO"})
        self.container.addAnimation(self.getPosition(),"showchar",1,{"char":"OO"})

        text = f"""
You insert your head into the machine.
It claws into your head and connects to your implant.

It changes your implant and sets your faction marker to {self.faction}.
"""
        character.macroState["submenue"] = src.menuFolder.textMenu.TextMenu(text)

src.items.addType(FactionSetter)

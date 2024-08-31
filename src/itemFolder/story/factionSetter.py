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

src.items.addType(FactionSetter)

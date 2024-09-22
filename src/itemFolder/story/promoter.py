import src
import random

class Promoter(src.items.Item):
    """
    """

    type = "Promoter"

    def __init__(self,):
        """
        configure the superclass
        """

        super().__init__(display="PR")
        self.faction = None

        self.walkable = False
        self.bolted = True

    def apply(self,character):
        if character.rank > 2:
            character.rank = character.rank-1
        character.addMessage(f"you were promoted to rank {character.rank}")
        character.changed("got promotion",{})

src.items.addType(Promoter)

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
            character.rank = 2
            character.addMessage(f"you were promoted to base commander")
            submenu = src.menuFolder.TextMenu.TextMenu("""
You put your head into the machine.

Its tendrils reach out and touch your implant.

It is upgraded to rank 2.
This means you can do special attacks now.""")
            character.macroState["submenue"] = submenu
            character.runCommandString("~",nativeKey=True)
            character.hasSpecialAttacks = True
        character.changed("got promotion",{})

src.items.addType(Promoter)

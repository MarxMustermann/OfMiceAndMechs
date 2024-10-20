import src
import random

class Communicator(src.items.Item):
    """
    """

    type = "Communicator"

    def __init__(self,):
        """
        configure the superclass
        """

        super().__init__(display="CC")
        self.faction = None

        self.walkable = False
        self.bolted = True

    def apply(self,character):
        if character.rank > 5:
            character.addMessage("You need to be at least rank 5.")
            character.changed("permission denied",{})
            if character == src.gamestate.gamestate.mainChar:
                src.gamestate.gamestate.stern["failedContact1"] = True
        return
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

src.items.addType(Communicator)

import src


class SuicideBooth(src.items.Item):
    """
    ingame item that kills the player
    has some potential use when using the ingame automation
    """

    type = "SuicideBooth"

    def __init__(self):
        """
        configure the super class
        """

        super().__init__(display="SB")
        self.name = "suicide booth"

    def apply(self, character):
        """
        handle a character tring to use the item to kill itself

        Parameters:
            character: the character trying to kill itself
        """

        character.addMessage("you die")
        character.die(reason="used suicide booth")

src.items.addType(SuicideBooth)

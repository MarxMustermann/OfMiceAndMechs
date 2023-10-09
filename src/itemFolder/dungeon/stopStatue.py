import src


class StopStatue(src.items.Item):
    """
    an item to stop statues
    """

    type = "StopStatue"

    def __init__(self):
        """
        configure the super class
        """

        super().__init__(display="OO")
        self.name = "stop statue"

        self.walkable = False
        self.bolted = True

    def apply(self, character):
        """
        handle a character tyring to destroy the wall

        Parameters:
            character: the character trying to destroy the wall
        """

        if not self.container.isRoom:
            return

        for otherChar in self.container.characters[:]:
            if character.faction == otherChar.faction:
                continue
            otherChar.die()
        self.destroy()

src.items.addType(StopStatue)

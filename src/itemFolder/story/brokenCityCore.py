import random

import src


class BrokenCityBuilder(src.items.Item):

    type = "BrokenCityBuilder"
    def __init__(self):
        super().__init__(display=(src.interaction.urwid.AttrSpec("#ff2", "black"), "Cc"))
        self.broken = True

    def apply(self, character):
        """
        handle a character trying to go up

        Parameters:
            character: the character using the item
        """

        if self.broken:
            character.addMessage("The city core is broken and you can not repair it")
            character.addMessage("locate and activate the reserve city core")

src.items.addType(BrokenCityBuilder)

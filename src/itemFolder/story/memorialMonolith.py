import src


class MemorialMonolith(src.items.Item):
    """
    ingame item used to give the player hints to treasure
    """
    type = "MemorialMonolith"
    def __init__(self,inscription=None):
        super().__init__(display=(src.interaction.urwid.AttrSpec("#ca0","#000"),"MM"))
        self.name = "memorial monolith"
        self.description = "holds a memorial engraving and is lavishly decorated"

        self.bolted = True
        self.walkable = False
        self.inscription = inscription

    def apply(self, character):
        """
        handle a character trying to use this item
        by showing some info

        Parameters:
            character: the character trying to use the item
        """

        if self.inscription:
            character.addMessage(self.inscription)
            character.showTextMenu(self.inscription)
        else:
            character.addMessage("The monolith has no inscription")

src.items.addType(MemorialMonolith)

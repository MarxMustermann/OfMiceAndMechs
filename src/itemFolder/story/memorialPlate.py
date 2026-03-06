import src


class MemorialPlate(src.items.Item):
    """
    ingame item used to give the player hints to treasure
    """
    type = "MemorialPlate"
    def __init__(self,inscription=None):
        super().__init__(display=(src.interaction.urwid.AttrSpec("#ca0","#000"),"::"))
        self.name = "memorial plate"
        self.description = "holds a memorial engraving and is decorated"

        self.bolted = True
        self.walkable = True
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
            character.addMessage("The plate has no inscription")

src.items.addType(MemorialPlate)

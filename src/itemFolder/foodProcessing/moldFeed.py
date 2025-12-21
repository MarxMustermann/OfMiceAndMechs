import src


class MoldFeed(src.items.Item):
    """
    ingame item acting as a fertilizer for mold.
    """

    type = "MoldFeed"

    def __init__(self):
        """
        configure super class
        """

        super().__init__(display=src.canvas.displayChars.moldFeed)
        self.name = "mold feed"
        self.description = "This is a good base for mold growth."

        self.walkable = True
        self.bolted = False

    def destroy(self, generateScrap=True):
        """
        destroy this item without leaving residue
        """

        super().destroy(generateScrap=False)

    def apply(self, character):
        """
        handle a character eating the item

        Parameters:
            character: the character eating this item
        """

        character.addSatiation(1000,reason="ate mold feed")
        self.destroy()

src.items.addType(MoldFeed)

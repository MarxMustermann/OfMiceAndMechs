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
        self.description "This is a good base for mold growth. If mold grows onto it, it will grow into a bloom."
        self.usageInfo = """
place mold feed next to a mold and when the mold grows onto it, it will grow into a bloom.

Activate it to eat
"""

        self.walkable = True
        self.bolted = False

    def destroy(self, generateSrcap=True):
        """
        destroy this item without leaving residue
        """

        super().destroy(generateSrcap=False)

    def apply(self, character):
        """
        handle a character eating the item

        Parameters:
            character: the character eating this item
        """

        character.addSatiation(1000,reason="ate mold feed")
        self.destroy()

src.items.addType(MoldFeed)

import src

class GlassCrystal(src.items.Item):
    """
    """

    type = "GlassCrystal"
    name = "glass crystal"
    description = "a fraction of something bigger"
    walkable = True
    bolted = False

    def __init__(self):
        """
        set up internal state
        """

        super().__init__(display="++")

    def destroy(self, generateScrap=True):
        """
        destroy without residue

        Parameters:
            generateScrap: flag to leave no residue
        """

        super().destroy(generateScrap=False)

src.items.addType(GlassCrystal)

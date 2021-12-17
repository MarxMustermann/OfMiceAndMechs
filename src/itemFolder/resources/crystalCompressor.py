import src

class CrystalCompressor(src.items.Item):
    """
    ingame item used as ressource. basically does nothing
    """
    type = "CrystalCompressor"
    name = "crystal compressor"
    description = "used to recharge shockers"
    walkable = True

    def __init__(self):
        """
        set up internal state
        """
        super().__init__()
        display = "<>"

src.items.addType(CrystalCompressor)

import src


class LightningRod(src.items.Item):
    """
    ingame item used as ressource. basically does nothing
    """
    type = "LightningRod"
    name = "lightning rod"
    description = "a metal Rod with static electricity running through it"
    walkable = True
    bolted = False

    def __init__(self):
        """
        set up internal state
        """
        super().__init__()
        self.display = "|*"

src.items.addType(LightningRod)

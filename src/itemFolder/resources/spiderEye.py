import src


class SpiderEye(src.items.Item):
    """
    ingame item serving as a ressource. basically does nothing
    """

    type = "SpiderEye"

    name = "a spiders eye"
    description = "used to brew potions"

    bolted = False
    walkable = True

    def __init__(self):
        """
        set up internal state
        """

        super().__init__("~~")

src.items.addType(SpiderEye)

import src


class Grindstone(src.items.Item):
    type = "Grindstone"
    name = "Grind stone"
    description = "item dropped from golems that can be used to improve weapons"
    walkable = True
    bolted = False

    def __init__(self):
        """
        set up internal state
        """

        super().__init__(display="^ ")


src.items.addType(Grindstone)

import src


class CitinPlates(src.items.Item):
    type = "CitinPlates"
    name = "Citin Plates"
    description = "item dropped from golems that can be used to improve armors"
    walkable = True
    bolted = False

    def __init__(self):
        """
        set up internal state
        """

        super().__init__(display=">")


src.items.addType(CitinPlates)

import src


class Implant(src.items.Item):
    type = "Implant"

    def __init__(self):
        super().__init__(display="IM")
        self.walkable = True
        self.bolted = False


src.items.addType(Implant)

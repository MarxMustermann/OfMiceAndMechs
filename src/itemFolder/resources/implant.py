import src


class Implant(src.items.Item):
    type = "Implant"
    description = "A mind control implant for Clones"
    def __init__(self):
        super().__init__(display="ip", name="Implant")
        self.walkable = True
        self.bolted = False


src.items.addType(Implant, nonManufactured=True)

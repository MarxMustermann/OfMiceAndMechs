import src


class MemoryFragment(src.items.Item):
    type = "MemoryFragment"

    def __init__(self):
        super().__init__(display="mf", name="Memory Fragment")
        self.walkable = True
        self.bolted = False


src.items.addType(MemoryFragment)

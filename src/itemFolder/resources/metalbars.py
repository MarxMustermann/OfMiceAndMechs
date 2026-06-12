import src


class MetalBars(src.items.Item):
    """
    ingame item used as ressource. basically does nothing
    """

    type = "MetalBars"
    name = "metal bar"
    description = "It is used by most machines and produced by a scrap compactor"
    walkable = True
    bolted = False

    def __init__(self):
        """
        set up internal state
        """

        super().__init__(display = src.canvas.displayChars.metalBars)

    def configure(self, character):
        if self in character.inventory:
            character.removeItemFromInventory(self)
        else:
            self.container.removeItem(self)

        metalWorkingBench = src.items.itemMap["MetalWorkingBench"]()

        container = character.container
        pos = character.getPosition()
        container.addItem(metalWorkingBench,pos)

src.items.addType(MetalBars)

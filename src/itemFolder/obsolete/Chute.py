import src


class Chute(src.items.Item):
    type = "Chute"

    def __init__(self):

        super().__init__(display="CH")
        self.name = "chute"

    def apply(self, character):
        if self.xPosition == None or not self.container:
            character.addMessage("This has to be placed in order to be used")
            return

        if character.inventory:
            item = character.inventory[-1]
            character.inventory.remove(item)
            item.xPosition = self.xPosition + 1
            item.yPosition = self.yPosition

            self.container.addItems([item])


src.items.addType(Chute)

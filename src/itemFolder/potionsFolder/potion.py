import src
from abc import ABC, abstractmethod


class Potion(src.items.Item):
    type = "Potion"

    def __init__(self):
        super().__init__(display=src.canvas.displayChars.gooflask_empty)
        self.walkable = True

    def apply(self, character):
        flask = src.items.itemMap["Flask"]()
        if not self.container:
            character.removeItemFromInventory(self)
            character.addToInventory(flask)
        else:
            container = self.container
            pos = self.getPosition()

            container.removeItem(self)
            container.addItem(flask, pos)

    def render(self):
        return src.canvas.displayChars.vial_full
    
    @abstractmethod
    def ingredients(): ...

src.items.addType(Potion)

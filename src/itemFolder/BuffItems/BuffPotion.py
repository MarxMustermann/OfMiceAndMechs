from abc import ABC, abstractmethod

import src


class BuffPotion(src.items.Item, ABC):
    type = "BuffPotion"

    def __init__(self):
        super().__init__(display=src.canvas.displayChars.gooflask_empty)

    def apply(self, character):
        character.buffs.append(self.BuffToAdd)
        character.changed("buffed")

        flask = src.items.itemMap["Flask"]()
        if not self.container:
            character.inventory.remove(self)
            character.inventory.append(flask)
        else:
            container = self.container
            pos = self.getPosition() 
            
            container.removeItem(self)
            container.addItem(flask, pos)

    def render(self):
        return src.canvas.displayChars.vial_full

    @property
    @abstractmethod
    def BuffToAdd(self): ...


src.items.addType(BuffPotion)

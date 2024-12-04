from abc import ABC, abstractmethod

import src


class BuffPotion(src.items.Item, ABC):
    type = "BuffPotion"

    def __init__(self):
        super().__init__(display=src.canvas.displayChars.gooflask_empty)

    def apply(self, character):
        character.buffs.append(self.BuffToAdd)
        character.changed()
        character.inventory.remove(self)
        character.inventory.append(src.items.itemMap["Flask"]())

    def render(self):
        return src.canvas.displayChars.vial_full

    @property
    @abstractmethod
    def BuffToAdd(self): ...


src.items.addType(BuffPotion)

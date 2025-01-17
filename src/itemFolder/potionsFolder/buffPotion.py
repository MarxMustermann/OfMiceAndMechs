from abc import ABC, abstractmethod

import src


class BuffPotion(src.items.itemMap["Potion"], ABC):
    type = "BuffPotion"
    isAbstract = True

    def apply(self, character):
        character.statusEffects.extend(self.getBuffsToAdd())
        character.changed("new status effect")
        super().apply(character)

    @abstractmethod
    def getBuffsToAdd(self): ...


src.items.addType(BuffPotion)

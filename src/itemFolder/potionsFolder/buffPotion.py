from abc import ABC, abstractmethod

import src


class BuffPotion(src.items.itemMap["Potion"], ABC):
    '''
    abstract class for ingame items that apply buffs to the player
    '''
    type = "BuffPotion"
    isAbstract = True

    def apply(self, character):
        '''
        apply the buffs to the character
        '''
        character.statusEffects.extend(self.getBuffsToAdd())
        character.changed("new status effect")
        super().apply(character)

    @abstractmethod
    def getBuffsToAdd(self): ...

# register the item type (should it be really?)
src.items.addType(BuffPotion)

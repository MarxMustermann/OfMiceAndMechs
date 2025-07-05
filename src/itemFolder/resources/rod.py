import random

import src


class Rod(src.items.Item):
    '''
    ingame item used as ressource. basically does nothing
    '''
    type = "Rod"
    name = "rod"
    description = "used to build items"
    bolted = False
    walkable = True
    def __init__(self,badQuality=False):
        super().__init__(display=src.canvas.displayChars.rod)

        if badQuality:
            self.baseDamage = 4
        else:
            self.baseDamage = int(random.triangular(4,21,10))

    def getLongInfo(self):
        '''
        return a longer than normal description text

        Returns:
            the description text
        '''
        text = super().getLongInfo()
        text += f"""
baseDamage:
{self.baseDamage}

"""
        return text

    # bad code: very hacky way of equiping things
    def apply(self, character):
        '''
        handle a character trying to use this item
        by equiping itself on the player

        Parameters:
            character: the character trying to use the iten
        '''

        character.addMessage(f"you equip the rod and wield a {self.baseDamage} weapon now")

        if character.weapon:
            oldWeapon = character.weapon
            character.weapon = None
            if character.getFreeInventorySpace():
                character.inventory.append(oldWeapon)

        character.weapon = self
        character.changed("equipedItem",(character,self))
        if self.container:
            self.container.removeItem(self)
        else:
            if self in character.inventory:
                character.inventory.remove(self)

    def upgrade(self):
        '''
        upgrade the rod. (obsolete?)
        '''
        self.baseDamage += 1
        super().upgrade()

    def downgrade(self):
        '''
        downgrade the rod. (obsolete?)
        '''
        self.baseDamage -= 1
        super().downgrade()

# register the item
src.items.addType(Rod)

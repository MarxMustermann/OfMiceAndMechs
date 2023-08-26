import src
import random

class Rod(src.items.Item):
    """
    ingame item used as ressource. basically does nothing
    """

    type = "Rod"

    name = "rod"
    description = "used to build items"

    bolted = False
    walkable = True

    def __init__(self,badQuality=False):
        """
        set initial state
        """

        super().__init__(display=src.canvas.displayChars.rod)

        if badQuality:
            self.baseDamage = 4
        else:
            self.baseDamage = int(random.triangular(4,21,10))
        self.attributesToStore.extend(
                [
                    "baseDamage",
                ]
            )

    def getLongInfo(self):
        """
        return a longer than normal description text

        Returns:
            the description text
        """

        text = super().getLongInfo()
        text += """
baseDamage:
%s

""" % (
            self.baseDamage,
        )
        return text

    # bad code: very hacky way of equiping things
    def apply(self, character):
        """
        handle a character trying to use this item
        by equiping itself on the player

        Parameters:
            character: the character trying to use the iten
        """

        character.addMessage("you equip the rod and wield a %s weapon now"%(self.baseDamage,))

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
        self.baseDamage += 1
        super().upgrade()

    def downgrade(self):
        self.baseDamage -= 1
        super().downgrade()

src.items.addType(Rod)

import random

import src


class Sword(src.items.Item):
    """
    ingame item used as ressource. basically does nothing
    """

    type = "Sword"

    name = "sword"
    description = "used to hit people"

    bolted = False
    walkable = True

    def __init__(self,generateFrom=None,badQuality=False):
        """
        set initial state
        """

        super().__init__(display="wt")

        if badQuality:
            self.baseDamage = 10
        else:
            self.baseDamage = int(random.triangular(10,25,15))

    def degrade(self,multiplier=1,character=None):
        if self.baseDamage <= 10:
            return

        if random.random()*self.baseDamage*multiplier > 200:
            self.baseDamage -= 1
            if character:
                character.addMessage(f"your weapon degrades and now has {self.baseDamage} damage")

    def getLongInfo(self):
        """
        return a longer than normal description text

        Returns:
            the description text
        """

        text = super().getLongInfo()
        text += f"""
baseDamage:
{self.baseDamage}

"""
        return text

    # bad code: very hacky way of equiping things
    def apply(self, character):
        """
        handle a character trying to use this item
        by equiping itself on the player

        Parameters:
            character: the character trying to use the iten
        """

        character.addMessage(f"you equip the sword and wield a {self.baseDamage} weapon now")
        charSequence = []
        for i in range(2,self.baseDamage+1):
            char = str(i)
            if i < 10:
                char = " "+char
            charSequence.append(char)
        character.container.addAnimation(character.getPosition(),"showchar",2,{"char":(src.interaction.urwid.AttrSpec("#fff", "black"), "wt")})
        character.container.addAnimation(character.getPosition(),"charsequence",len(charSequence)-1,{"chars":charSequence})
        character.container.addAnimation(character.getPosition(),"showchar",5,{"char":charSequence[-1]})
        character.container.addAnimation(character.getPosition(),"showchar",2,{"char":(src.interaction.urwid.AttrSpec("#fff", "black"), "wt")})

        if character.weapon:
            oldWeapon = character.weapon
            character.weapon = None
            character.container.addItem(oldWeapon,character.getPosition())

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

src.items.addType(Sword)

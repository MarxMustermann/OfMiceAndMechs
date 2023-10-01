import src
import random

class Armor(src.items.Item):
    """
    ingame item increasing the players armor
    """

    type = "Armor"
    name = "armor"
    bolted = False
    walkable = True
    damageType = "attacked"

    def __init__(self,badQuality=False):
        """
        set up internal state
        """

        super().__init__(display="ar")

        if badQuality:
            self.armorValue = 1
        else:
            self.armorValue = random.randint(1, 5)

    def getArmorValue(self, damageType):
        """
        returns the items armor value

        Parameters:
            damageType: the damage type to armor against
        """

        if damageType == self.damageType:
            return self.armorValue
        if damageType == "explosion":
            return self.armorValue*5
        return 0

    def getLongInfo(self):
        """
        returns a longer than normal description text

        Returns:
            the description text
        """

        text = super().getLongInfo()

        text += f"""
armorvalue:
{self.armorValue}

description:
protects you in combat

"""
        return text

    def apply(self, character):
        """
        handle a character trying to use this item
        by equiping it
        """

        character.addMessage(f"you equip the armor and wear a {self.armorValue} armor now")

        charSequence = []
        for i in range(1,self.armorValue+1):
            char = str(i)
            if i < 10:
                char = " "+char
            charSequence.append(char)
            charSequence.append(char)
            charSequence.append(char)
            charSequence.append(char)
        character.container.addAnimation(character.getPosition(),"showchar",2,{"char":(src.interaction.urwid.AttrSpec("#fff", "black"), "ar")})
        character.container.addAnimation(character.getPosition(),"charsequence",len(charSequence)-1,{"chars":charSequence})
        character.container.addAnimation(character.getPosition(),"showchar",5,{"char":charSequence[-1]})
        character.container.addAnimation(character.getPosition(),"showchar",2,{"char":(src.interaction.urwid.AttrSpec("#fff", "black"), "ar")})

        if character.armor:
            oldArmor = character.armor
            character.armor = None
            character.container.addItem(oldArmor,character.getPosition())

        character.armor = self
        character.changed("equipedItem",(character,self))
        if self.container:
            self.container.removeItem(self)
        else:
            if self in character.inventory:
                character.inventory.remove(self)

    def upgrade(self):
        self.armorValue += 1
        super().upgrade()

    def downgrade(self):
        self.armorValue -= 1
        super().downgrade()

src.items.addType(Armor)

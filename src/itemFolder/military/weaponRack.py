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

    def __init__(self):
        """
        set up internal state    
        """

        super().__init__(display="ar")

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

        text += """
armorvalue:
%s

description:
protects you in combat

""" % (
            self.armorValue,
        )
        return text

    def apply(self, character):
        """
        handle a character trying to use this item
        by equiping it
        """

        character.addMessage("you equip the armor and wear a %s armor now"%(self.armorValue,))

        if character.armor:
            oldArmor = character.armor
            character.armor = None
            self.container.addItem(oldArmor,self.getPosition())

        character.armor = self
        self.container.removeItem(self)

    def upgrade(self):
        self.armorValue += 1
        super().upgrade()

    def downgrade(self):
        self.armorValue -= 1
        super().downgrade()

src.items.addType(Armor)

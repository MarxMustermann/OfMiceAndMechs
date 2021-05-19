import src
import random

class Armor(src.items.Item):
    """
    ingame item increasing the players armor
    """

    type = "Armor"

    def __init__(self):
        """
        set up internal state    
        """

        super().__init__(display="ar")

        self.name = "armor"

        self.bolted = False
        self.walkable = True
        self.armorValue = random.randint(1, 5)
        self.damageType = "attacked"

    def getArmorValue(self, damageType):
        """
        returns the items armor value

        Parameters:
            damageType: the damage type to armor against
        """

        if damageType == self.damageType:
            return self.armorValue
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

        character.armor = self
        self.container.removeItem(self)

src.items.addType(Armor)

import src
import random

class Rod(src.items.Item):
    """
    ingame item used as ressource. basically does nothing
    """

    type = "Rod"

    def __init__(self):
        """
        set initial state
        """

        super().__init__(display=src.canvas.displayChars.rod)

        self.name = "rod"
        self.description = "used to build items"

        self.bolted = False
        self.walkable = True

        num = 40
        while num > 20:
            num = random.expovariate(1/3)//1 + 4

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

        character.weapon = self
        self.container.removeItem(self)

    def upgrade(self):
        self.baseDamage += 1
        super().upgrade()

    def downgrade(self):
        self.baseDamage -= 1
        super().downgrade()

src.items.addType(Rod)

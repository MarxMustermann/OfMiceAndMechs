import src
import random

class Rod(src.items.Item):
    """
    ingame item used as ressource. basically does nothing
    """

    type = "Rod"
    attributesToStore = []

    name = "rod"
    description = "used to build items"

    bolted = False
    walkable = True

    def __init__(self):
        """
        set initial state
        """

        super().__init__(display=src.canvas.displayChars.rod)

        self.baseDamage = int(random.triangular(4,21,10))
        if not self.attributesToStore:
            self.attributesToStore.extend(super().attributesToStore)
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

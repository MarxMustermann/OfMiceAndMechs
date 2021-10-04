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
        self.baseDamage = random.randint(3,15)
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

src.items.addType(Rod)

import src
import random

class GhulFeeder(src.items.Item):
    """
    ingame item for filling up goo flasks
    """

    type = "GhulFeeder"

    def __init__(self):
        """
        configure super class
        """

        super().__init__()

        self.display = src.canvas.displayChars.gooDispenser

        self.name = "ghul feeder"

        self.activated = False
        self.baseName = self.name
        self.level = 1

        # set up meta information for saving
        self.attributesToStore.extend(["activated", "charges"])

        self.charges = 0
        self.maxCharges = 100

        self.description = self.baseName + " (%s charges)" % (self.charges)

    def setDescription(self):
        """
        set own description
        """
        self.description = self.baseName + " (%s charges)" % (self.charges)

    def apply(self, character):
        """
        handle a ghul trying to eat

        Parameters:
            character: the character trying to use this item
        """

        while character.satiation < 1000:
            #if not self.charges:
            #    character.addMessage("the ghul feeder has no charges")
            #    return

            character.satiation += 15
            if character.satiation > 1000:
                character.satiation = 1000
            #self.charges -= 1
            character.addMessage("you eat from the corpse and gain 15 satiation")

            if character.satiation > random.randint(0,10000):
                character.hurt(1,reason="the solid food hurts your stomach")

    def addCharge(self):
        """
        charge up this item
        one charge is one refill
        """

        self.charges += 1
        self.description = self.baseName + " (%s charges)" % (self.charges)

    def setState(self, state):
        """
        set state from dict and ensure own description is set
        """

        super().setState(state)

        self.setDescription()

    def getLongInfo(self):
        """
        return a longer than normal descriotion text for this item

        Returns:
            the description text
        """

        text = """
This ghul feeder currently has %s charges
""" % (
            self.charges
        )
        return text

src.items.addType(GhulFeeder)

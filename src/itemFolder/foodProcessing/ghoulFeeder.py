import random

import src


class GhoulFeeder(src.items.Item):
    """
    ingame item for filling up goo flasks
    """

    type = "GhoulFeeder"

    def __init__(self):
        """
        configure super class
        """

        super().__init__()

        self.display = src.canvas.displayChars.gooDispenser

        self.name = "ghoul feeder"

        self.activated = False
        self.baseName = self.name
        self.level = 1

        self.charges = 0
        self.maxCharges = 100

        self.description = self.baseName + " (%s charges)" % (self.charges)

    def getConfigurationOptions(self, character):
        """
        register the configuration options with superclass

        Parameters:
            character: the character trying to conigure the machine
        """

        options = super().getConfigurationOptions(character)
        if self.bolted:
            options["b"] = ("unbolt", self.unboltAction)
        else:
            options["b"] = ("bolt down", self.boltAction)
        return options

    def boltAction(self,character):
        self.bolted = True
        character.addMessage("you bolt down the ScrapCompactor")
        character.changed("boltedItem",{"character":character,"item":self})

    def unboltAction(self,character):
        self.bolted = False
        character.addMessage("you unbolt the ScrapCompactor")
        character.changed("unboltedItem",{"character":character,"item":self})

    def setDescription(self):
        """
        set own description
        """
        self.description = self.baseName + " (%s charges)" % (self.charges)

    def apply(self, character):
        """
        handle a ghoul trying to eat

        Parameters:
            character: the character trying to use this item
        """

        while character.satiation < 1000:
            #if not self.charges:
            #    character.addMessage("the ghoul feeder has no charges")
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

    def getLongInfo(self):
        """
        return a longer than normal descriotion text for this item

        Returns:
            the description text
        """

        text = """
This ghoul feeder currently has %s charges
""" % (
            self.charges
        )
        return text

src.items.addType(GhoulFeeder)

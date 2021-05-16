import src



class GooDispenser(src.items.Item):
    """
    ingame item for filling up goo flasks
    """

    type = "GooDispenser"

    def __init__(self):
        """
        configure super class
        """

        super().__init__()

        self.display = src.canvas.displayChars.gooDispenser

        self.name = "goo dispenser"
        self.description = "A goo dispenser can fill goo flasks"
        self.usageInfo = """
Activate it with a goo flask in you inventory.
The goo flask will be filled by the goo dispenser.

Filling a flask will use up a charge from your goo dispenser.
"""

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
        handle a character trying to fill goo flask

        Parameters:
            character: the character trying to use this item
        """

        if not self.charges:
            character.addMessage("the dispenser has no charges")
            return

        filled = False
        fillAmount = 100 + ((self.level - 1) * 10)
        for item in character.inventory:
            if isinstance(item, GooFlask) and not item.uses >= fillAmount:
                item.uses = fillAmount
                filled = True
                self.charges -= 1
                self.description = self.baseName + " (%s charges)" % (self.charges)
                break
        if filled:
            character.addMessage("you fill the goo flask")
        self.activated = True

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
This goo dispenser currently has %s charges
""" % (
            self.charges
        )
        return text

src.items.addType(GooDispenser)

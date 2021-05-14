import src

"""
machine for filling up goo flasks
"""


class GooDispenser(src.items.Item):
    type = "GooDispenser"

    """
    call superclass constructor with modified paramters and set some state
    """

    def __init__(self):
        super().__init__()

        self.display = src.canvas.displayChars.gooDispenser

        self.name = "goo dispenser"
        self.activated = False
        self.baseName = self.name
        self.level = 1

        # set up meta information for saveing
        self.attributesToStore.extend(["activated", "charges"])

        self.charges = 0
        self.maxCharges = 100

        self.description = self.baseName + " (%s charges)" % (self.charges)

    def setDescription(self):
        self.description = self.baseName + " (%s charges)" % (self.charges)

    """
    fill goo flask
    """

    def apply(self, character):
        super().apply(character, silent=True)

        if not self.room:
            character.addMessage("this machine can only be used within rooms")
            return

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
        self.charges += 1
        self.description = self.baseName + " (%s charges)" % (self.charges)

    """
    set state from dict
    """

    def setState(self, state):
        super().setState(state)

        self.setDescription()

    def getLongInfo(self):
        text = """
item: GooDispenser

description:
A goo dispenser can fill goo flasks.

Activate it with a goo flask in you inventory.
The goo flask will be filled by the goo dispenser.

Filling a flask will use up a charge from your goo dispenser.

This goo dispenser currently has %s charges

""" % (
            self.charges
        )
        return text


src.items.addType(GooDispenser)

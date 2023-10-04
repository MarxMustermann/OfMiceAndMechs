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

    def render(self):
        if self.readyToUse():
            baseDisplay = "%="
            if self.charges > 5:
                baseDisplay = "§="
            if self.charges > 20:
                baseDisplay = "$="
            if self.charges == self.maxCharges:
                baseDisplay = "&="
            return (src.interaction.urwid.AttrSpec("#fff", "black"),baseDisplay)
        return self.display


    def readyToUse(self):
        if not self.charges > 0:
            return False

        return True

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
            self.container.addAnimation(self.getPosition(),"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#f00", "black"),"][")})
            return

        filled = False
        fillAmount = 100 + ((self.level - 1) * 10)

        if character.flask and character.flask.uses < fillAmount:
            character.flask.uses = fillAmount
            self.runCommand("filled",character)
            self.charges -= 1
            self.description = self.baseName + " (%s charges)" % (self.charges)
            character.addMessage("you fill your goo flask")
            self.container.addAnimation(self.getPosition(offset=(0,0,0)),"charsequence",1,{"chars":["&=","$=","§="]})
            character.container.addAnimation(character.getPosition(offset=(0,0,0)),"charsequence",1,{"chars":["o "," o","oo"]})
            return

        for item in character.inventory:
            if isinstance(item, src.items.itemMap["GooFlask"]) and not item.uses >= fillAmount:
                item.uses = fillAmount
                filled = True
                self.charges -= 1
                self.description = self.baseName + " (%s charges)" % (self.charges)
                character.addMessage("you fill the goo flask")
                break
        if filled:
            self.runCommand("filled",character)
            character.addMessage("you fill goo flasks in your inventory")
            return

        character.addMessage("you have no flask to be filled")
        self.container.addAnimation(self.getPosition(),"showchar",2,{"char":(src.interaction.urwid.AttrSpec("#740", "black"),"XX")})
        character.container.addAnimation(character.getPosition(),"showchar",2,{"char":(src.interaction.urwid.AttrSpec("#740", "black"),"[]")})

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
This goo dispenser currently has %s charges
""" % (
            self.charges
        )
        return text

src.items.addType(GooDispenser)

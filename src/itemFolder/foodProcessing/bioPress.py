import src


class BioPress(src.items.Item):
    """
    processes food by converting biomass to press cake
    """

    type = "BioPress"

    """
    call superclass constructor with modified paramters and set some state
    """

    def __init__(self):
        super().__init__(display=src.canvas.displayChars.bioPress)
        self.activated = False
        self.name = "bio press"
        self.description = "A bio press produces press cake from bio mass."
        self.usageInfo = """
Place 10 bio mass to the left/west of the bio press.
Activate the bio press to produce press cake.
"""

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
            return "%H"
        else:
            return self.display

    def readyToUse(self):
        if not self.xPosition:
            return False

        # fetch input scrap
        items = []
        for item in self.container.getItemByPosition((self.xPosition - 1, self.yPosition, self.zPosition)):
            if item.type == "BioMass":
                items.append(item)

        # refuse to produce without resources
        if len(items) < 10:
            return False

        # check if target area is full
        targetFull = False
        itemList = self.container.getItemByPosition(
            (self.xPosition + 1, self.yPosition, self.zPosition)
        )
        if len(itemList) > 15:
            targetFull = True
        for item in itemList:
            if item.walkable is False:
                targetFull = True

        if targetFull:
            return False

        return True

    # needs abstraction: takes x input and produces y output
    def apply(self, character):
        """
        handle a character trying to produce a press cake from bio mass

        Parameters:
            character: the character using the item
        """

        character.changed("operated machine",{"character":character,"machine":self})

        # fetch input bio mass
        items = []
        for item in self.container.getItemByPosition(
            (self.xPosition - 1, self.yPosition, self.zPosition)
        ):
            if item.type == "BioMass":
                items.append(item)

        # refuse to produce without resources
        if len(items) < 10:
            character.addMessage("not enough bio mass")
            self.container.addAnimation(self.getPosition(offset=(-1,0,0)),"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#f00", "black"),"XX")})
            self.container.addAnimation(self.getPosition(),"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#f00", "black"),"XX")})
            return

        # check if target area is full
        targetFull = False
        itemList = self.container.getItemByPosition(
            (self.xPosition + 1, self.yPosition, self.zPosition)
        )
        if len(itemList) > 15:
            targetFull = True
        for item in itemList:
            if item.walkable is False:
                targetFull = True

        if targetFull:
            character.addMessage(
                "the target area is full, the machine does not produce anything"
            )
            return

        # remove resources
        counter = 0
        for item in items:
            if counter >= 10:
                break
            counter += 1
            self.container.removeItem(item)

        character.addMessage(
            "you produce a press cake"
        )

        # spawn the new item
        new = src.items.itemMap["PressCake"]()
        self.container.addItem(
            new, (self.xPosition + 1, self.yPosition, self.zPosition)
        )

        self.container.addAnimation(self.getPosition(offset=(-1,0,0)),"showchar",3,{"char":(src.interaction.urwid.AttrSpec("#fff", "black"),"--")})
        self.container.addAnimation(self.getPosition(offset=(0,0,0)),"charsequence",1,{"chars":["§H","%H","$H"]})
        self.container.addAnimation(self.getPosition(offset=(1,0,0)),"showchar",3,{"char":(src.interaction.urwid.AttrSpec("#fff", "black"),"++")})


src.items.addType(BioPress)

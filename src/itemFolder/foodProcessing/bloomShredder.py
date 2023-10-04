import src


class BloomShredder(src.items.Item):
    """
    ingame item thats part of the production chain for goo from bloomb
    """

    type = "BloomShredder"

    def __init__(self):
        """
        simple superclass configuration
        """

        self.activated = False
        super().__init__(display=src.canvas.displayChars.bloomShredder)
        self.name = "bloom shredder"
        self.description = "A bloom shredder produces bio mass from blooms"
        self.usageInfo = """
Place bloom to the left/west of the bloom shredder.
Activate the bloom shredder to produce biomass.
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

    def apply(self, character):
        """
        handle a character trying to use this item to convert a bloom into a bio mass

        Parameters:
            character: the character using the item
        """

        items = []
        for item in self.container.getItemByPosition((self.xPosition - 1, self.yPosition, self.zPosition)):
            if isinstance(item, src.items.itemMap["Bloom"]):
                items.append(item)

        # refuse to produce without resources
        if len(items) < 1:
            self.container.addAnimation(self.getPosition(),"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#f00", "black"),"XX")})
            self.container.addAnimation(self.getPosition(offset=(-1,0,0)),"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#f00", "black"),"][")})
            character.addMessage("not enough blooms")
            return

        targetFull = False
        if (self.xPosition + 1, self.yPosition, self.zPosition) in self.container.itemByCoordinates:
            if (
                len(self.container.itemByCoordinates[(self.xPosition + 1, self.yPosition, self.zPosition)])
                > 15
            ):
                targetFull = True
            for item in self.container.itemByCoordinates[
                (self.xPosition + 1, self.yPosition, self.zPosition)
            ]:
                if item.walkable == False:
                    targetFull = True

        if targetFull:
            character.addMessage(
                "the target area is full, the machine does not produce anything"
            )
            self.container.addAnimation(self.getPosition(),"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#740", "black"),"XX")})
            self.container.addAnimation(self.getPosition(offset=(-1,0,0)),"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#740", "black"),"[]")})
            return

        # remove resources
        self.container.removeItem(items[0])

        # spawn the new item
        new = src.items.itemMap["BioMass"]()
        self.container.addItem(new,(self.xPosition + 1,self.yPosition,self.zPosition))

        self.container.addAnimation(self.getPosition(offset=(-1,0,0)),"showchar",3,{"char":(src.interaction.urwid.AttrSpec("#fff", "black"),"--")})
        self.container.addAnimation(self.getPosition(offset=(0,0,0)),"charsequence",1,{"chars":["§>","%>","$>"]})
        self.container.addAnimation(self.getPosition(offset=(1,0,0)),"showchar",3,{"char":(src.interaction.urwid.AttrSpec("#fff", "black"),"++")})

src.items.addType(BloomShredder)

import src

class VialFiller(src.items.Item):
    """
    ingame item for filling up goo flasks
    """

    type = "VialFiller"

    def __init__(self):
        """
        configure super class
        """

        super().__init__()

        self.display = src.canvas.displayChars.gooDispenser

        self.name = "vial filler"
        self.ins = [(-1,0,0)]

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
            baseDisplay = "o="
            return (src.interaction.urwid.AttrSpec("#fff", "black"),baseDisplay)
        return "x="

    def getDispenser(self):
        if not self.container:
            return

        fallBackItem = None
        for inOffset in self.ins:
            items = self.container.getItemByPosition(self.getPosition(offset=inOffset))
            for item in items:
                print(item)
                if not item.bolted:
                    continue
                if not item.type == "GooDispenser":
                    continue
                fallBackItem = item
                if not item.charges:
                    continue
                return item
        return fallBackItem

    def readyToUse(self):
        self.ins = [(-1,0,0)]
        if not self.getDispenser():
            return False
        if not self.getDispenser().charges > 0:
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

        dispenser = self.getDispenser()
        if not dispenser:
            character.addMessage("there needs to be a goo dispenser placed")
            self.container.addAnimation(self.getPosition(),"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#f00", "black"),"][")})
            return

        if not dispenser.charges:
            character.addMessage("the GooDispenser has no charges")
            self.container.addAnimation(self.getPosition(),"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#f00", "black"),"][")})
            return

        filled = False
        chargesUsed = 0

        for item in character.inventory:
            if dispenser.charges and isinstance(item, src.items.itemMap["Vial"]) and not item.uses >= item.maxUses:
                item.uses = 10
                dispenser.charges -= 1
                filled = True
                character.addMessage("you fill the vial")
                break
        if filled:
            character.addMessage("you fill vials in your inventory")
            character.addMessage(f"you used {chargesUsed} charges")
            if not dispenser.charges > 0:
                character.addMessage("the GooDispenser is empty now")
            return

        character.addMessage("you have no vial to be filled")
        self.container.addAnimation(self.getPosition(),"showchar",2,{"char":(src.interaction.urwid.AttrSpec("#740", "black"),"XX")})
        character.container.addAnimation(character.getPosition(),"showchar",2,{"char":(src.interaction.urwid.AttrSpec("#740", "black"),"[]")})

src.items.addType(VialFiller)

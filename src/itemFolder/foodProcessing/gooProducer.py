import src

class GooProducer(src.items.Item):
    """
    ingame item that is the final step of the goo (food) production
    """

    type = "GooProducer"

    def __init__(self):
        """
        configure super class
        """

        super().__init__(display=src.canvas.displayChars.gooProducer)
        self.name = "goo producer"
        self.description = "A goo producer produces goo from press cakes"
        self.usageInfo = """
Place 10 press cakes to the left/west of the goo producer and a goo dispenser to the rigth/east.
Activate the maggot fermenter to add a charge to the goo dispenser.
"""

        self.activated = False
        self.level = 1

        # bad code: repetitive and easy to forget
        self.attributesToStore.extend(["level"])

    def apply(self, character):
        """
        handle a character trying to produce goo

        Parameters:
            character: the character trying to use the item
        """

        character.changed("operated machine",{"character":character,"machine":self})

        # fetch input items
        items = []
        for item in self.container.getItemByPosition((self.xPosition - 1, self.yPosition, self.zPosition)):
            if item.type == "PressCake":
                items.append(item)

        # refuse to produce without resources
        if len(items) < 10 + (self.level - 1):
            character.addMessage("not enough press cakes")
            self.container.addAnimation(self.getPosition(),"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#f00", "black"),"XX")})
            self.container.addAnimation(self.getPosition(offset=(-1,0,0)),"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#f00", "black"),"XX")})
            return

        # refill goo dispenser
        dispenser = None

        for item in self.container.getItemByPosition((self.xPosition + 1, self.yPosition, self.zPosition)):
            if item.type == "GooDispenser":
                dispenser = item
        if not dispenser:
            character.addMessage("no goo dispenser attached")
            self.container.addAnimation(self.getPosition(),"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#f00", "black"),"XX")})
            self.container.addAnimation(self.getPosition(offset=(1,0,0)),"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#f00", "black"),"XX")})
            return

        if dispenser.level > self.level:
            character.addMessage(
                "the goo producer has to have higher or equal the level as the goo dispenser"
            )
            return

        if dispenser.charges >= dispenser.maxCharges:
            character.addMessage("the goo dispenser is full")
            return

        # remove resources
        counter = 0
        for item in items:
            if counter >= 10:
                break
            counter += 1
            self.container.removeItem(item)

        dispenser.addCharge()
        character.addMessage("You produce some goo and add a charge to the goo dispenser")
        self.container.addAnimation(self.getPosition(offset=(-1,0,0)),"showchar",3,{"char":(src.interaction.urwid.AttrSpec("#fff", "black"),"--")})
        self.container.addAnimation(self.getPosition(offset=(0,0,0)),"charsequence",1,{"chars":["§T","%T","$T"]})
        self.container.addAnimation(self.getPosition(offset=(1,0,0)),"charsequence",1,{"chars":["§=","$=","&="]})

    def render(self):
        if self.readyToUse():
            return "%T"
        else:
            return self.display

    def readyToUse(self):
        """
        handle a character trying to produce goo

        Parameters:
            character: the character trying to use the item
        """
        if not self.xPosition:
            return False

        # fetch input items
        items = []
        for item in self.container.getItemByPosition((self.xPosition - 1, self.yPosition, self.zPosition)):
            if item.type == "PressCake":
                items.append(item)

        # refuse to produce without resources
        if len(items) < 10 + (self.level - 1):
            return False

        # refill goo dispenser
        dispenser = None

        for item in self.container.getItemByPosition((self.xPosition + 1, self.yPosition, self.zPosition)):
            if item.type == "GooDispenser":
                dispenser = item
        if not dispenser:
            return False

        if dispenser.level > self.level:
            return False

        if dispenser.charges >= dispenser.maxCharges:
            return False

        return True

src.items.addType(GooProducer)

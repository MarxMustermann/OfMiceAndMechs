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

        super().apply(character)

        # fetch input items
        items = []
        for item in self.container.getItemByPosition((self.xPosition - 1, self.yPosition, self.zPosition)):
            if item.type == "PressCake":
                items.append(item)

        # refuse to produce without resources
        if len(items) < 10 + (self.level - 1):
            character.addMessage("not enough press cakes")
            return

        # refill goo dispenser
        dispenser = None

        for item in self.container.getItemByPosition((self.xPosition + 1, self.yPosition, self.zPosition)):
            if item.type == "GooDispenser":
                dispenser = item
        if not dispenser:
            character.addMessage("no goo dispenser attached")
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

src.items.addType(GooProducer)

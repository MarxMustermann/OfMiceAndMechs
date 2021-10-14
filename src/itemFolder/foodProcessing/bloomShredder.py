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

    def apply(self, character):
        """
        handle a character trying to use this item to convert a bloom into a bio mass

        Parameters:
            character: the character using the item
        """

        items = []
        for item in self.container.getItemByPosition((self.xPosition - 1, self.yPosition, self.zPosition)):
            if isinstance(item, src.items.Bloom):
                items.append(item)

        # refuse to produce without resources
        if len(items) < 1:
            character.addMessage("not enough blooms")
            return

        targetFull = False
        if (self.xPosition + 1, self.yPosition) in self.container.itemByCoordinates:
            if (
                len(self.container.itemByCoordinates[(self.xPosition + 1, self.yPosition)])
                > 15
            ):
                targetFull = True
            for item in self.container.itemByCoordinates[
                (self.xPosition + 1, self.yPosition)
            ]:
                if item.walkable == False:
                    targetFull = True

        if targetFull:
            character.addMessage(
                "the target area is full, the machine does not produce anything"
            )
            return

        # remove resources
        self.container.removeItem(items[0])

        # spawn the new item
        new = src.items.itemMap["BioMass"]()
        self.container.addItem(new,(self.xPosition + 1,self.yPosition,self.zPosition))

src.items.addType(BloomShredder)

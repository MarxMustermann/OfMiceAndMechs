import src

"""
"""


class BloomShredder(src.items.Item):
    type = "BloomShredder"

    """
    call superclass constructor with modified paramters and set some state
    """

    def __init__(self, name="bloom shredder", noId=False):
        self.activated = False
        super().__init__(display=src.canvas.displayChars.bloomShredder, name=name)

    """
    """

    def apply(self, character):
        super().apply(character, silent=True)

        items = []
        for item in self.container.getItemByPosition((self.xPosition - 1, self.yPosition, self.zPosition)):
            if isinstance(item, Bloom):
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

    def getLongInfo(self):
        text = """
item: BloomShredder

description:
A bloom shredder produces bio mass from blooms.

Place bloom to the left/west of the bloom shredder.
Activate the bloom shredder to produce biomass.

"""
        return text


src.items.addType(BloomShredder)

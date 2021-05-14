import src

"""
"""


class SporeExtractor(src.items.Item):
    type = "SporeExtractor"

    """
    call superclass constructor with modified paramters and set some state
    """

    def __init__(self):
        super().__init__()

        self.display = src.canvas.displayChars.sporeExtractor
        self.name = "spore extractor"
        self.activated = False

    """
    """

    def apply(self, character):

        super().apply(character, silent=True)

        if self.xPosition is None:
            character.addMessage("this machine needs to be placed to be used")
            return

        items = []
        for item in self.container.getItemByPositio((self.xPosition - 1, self.yPosition, self.zPosition):
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
        for i in range(1, 5):
            new = src.items.itemMap["MoldSpore"]()
            self.container.addItem(new,(self.xPosition,self.yPosition,self.zPosition))

    def getLongInfo(self):
        text = """
item: SporeExtractor

description:
A Spore Extractor removes spores from mold blooms.

Place mold bloom to the west/left and activate the Spore Extractor.
The MoldSpores will be outputted to the east/right.

"""
        return text


src.items.addType(SporeExtractor)

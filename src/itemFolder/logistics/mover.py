import src


class Mover(src.items.Item):
    """
    ingame item to move other items a short distance
    inteded to help with coding edgecases
    """

    type = "Mover"

    def __init__(self):
        """
        call superclass constructor with modified parameters
        """

        super().__init__(display=src.canvas.displayChars.sorter)
        self.name = "mover"
        self.description = "A mover moves items"
        self.usageInfo = """
Place the item or items to the west of the mover.
activate the mover to move one item to the east of the mover.
"""

    def apply(self, character):
        """
        handle a character trying to us this item to move items
        by trying to move the items

        Parameters:
            character: the character trying to use this item
        """

        if self.xPosition is None:
            character.addMessage("this machine needs to be placed to be used")
            return

        # fetch input
        itemFound = None
        for item in self.container.getItemByPosition(
            (self.xPosition - 1, self.yPosition)
        ):
            itemFound = item
            break

        if not itemFound:
            character.addMessage("nothing to be moved")
            return

        # remove input
        self.container.removeItem(itemFound)

        targetPos = (self.xPosition + 1, self.yPosition)

        itemFound.xPosition = targetPos[0]
        itemFound.yPosition = targetPos[1]

        targetFull = False
        new = itemFound
        items = self.container.getItemByPosition((self.xPosition + 1, self.yPosition))
        if new.walkable:
            if len(items) > 15:
                targetFull = True
            for item in items:
                if item.walkable == False:
                    targetFull = True
        else:
            if len(items) > 1:
                targetFull = True

        if targetFull:
            character.addMessage(
                "the target area is full, the machine does not produce anything"
            )
            return

        self.container.addItems([itemFound])

src.items.addType(Mover)

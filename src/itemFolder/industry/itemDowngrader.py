import src


class ItemDowngrader(src.items.Item):
    """
    ingame item to downgrade other items
    """

    type = "ItemDowngrader"

    def __init__(self):
        """
        set up internal state
        """

        super().__init__(display="ID")
        self.name = "item downgrader"
        self.description = "the item downgrader downgrades items"
        self.usageInfo = """
Place item to upgrade to the west and the downgraded item will be placed to the east.
"""

    def apply(self, character):
        """
        handle a character trying to use this item to downgrade another item

        Parameters:
            character: the character trying to use the item
        """

        if self.xPosition is None:
            character.addMessage("this machine has to be placed to be used")
            return

        inputItem = None

        itemsFound = self.container.getItemByPosition((self.xPosition - 1, self.yPosition,0))
        if itemsFound:
            inputItem = itemsFound[0]

        if not inputItem:
            character.addMessage("place item to downgrade on the left")
            return

        if not hasattr(inputItem, "level"):
            character.addMessage("cannot downgrade %s" % (inputItem.type))
            return

        if inputItem.level == 1:
            character.addMessage("cannot downgrade item further")
            return

        targetFull = False
        if (self.xPosition + 1, self.yPosition) in self.container.itemByCoordinates:
            if inputItem.walkable:
                if (
                    len(
                        self.container.itemByCoordinates[
                            (self.xPosition + 1, self.yPosition)
                        ]
                    )
                    > 15
                ):
                    targetFull = True
                for item in self.container.itemByCoordinates[
                    (self.xPosition + 1, self.yPosition)
                ]:
                    if item.walkable is False:
                        targetFull = True
            else:
                if (
                    len(
                        self.container.itemByCoordinates[
                            (self.xPosition + 1, self.yPosition)
                        ]
                    )
                    > 1
                ):
                    targetFull = True

        if targetFull:
            character.addMessage(
                "the target area is full, the machine does not produce anything"
            )
            return

        self.container.removeItem(inputItem)

        inputItem.level -= 1
        character.addMessage(f"{inputItem.type} downgraded")
        inputItem.xPosition = self.xPosition + 1
        inputItem.yPosition = self.yPosition
        self.container.addItems([inputItem])

src.items.addType(ItemDowngrader)

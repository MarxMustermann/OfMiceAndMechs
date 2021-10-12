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

    # needs abstraction: takes x input and produces y output
    def apply(self, character):
        """
        handle a character trying to produce a press cake from bio mass

        Parameters:
            character: the character using the item
        """

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
            return

        # check if target area is full
        targetFull = False
        itemList = self.container.getItemByPosition(
            (self.xPosition + 1, self.yPosition, self.zPosition)
        )
        if len(itemList) > 15:
            targetFull = True
        for item in itemList:
            if item.walkable == False:
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

        # spawn the new item
        new = src.items.itemMap["PressCake"]()
        self.container.addItem(
            new, (self.xPosition + 1, self.yPosition, self.zPosition)
        )


src.items.addType(BioPress)

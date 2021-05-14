import src


class MaggotFermenter(src.items.Item):
    type = "MaggotFermenter"

    """
    call superclass constructor with modified paramters and set some state
    """

    def __init__(self, name="maggot fermenter", noId=False):
        self.activated = False
        super().__init__(display=src.canvas.displayChars.maggotFermenter, name=name)

    """
    """

    def apply(self, character):
        super().apply(character, silent=True)

        if not self.xPosition:
            character.addMessage("This has to be placed to be used")
            return

        # fetch input scrap
        items = []
        for item in self.container.getItemByPosition((self.xPosition - 1, self.yPosition, self.zPosition)):
            if isinstance(item, VatMaggot):
                items.append(item)

        # refuse to produce without resources
        if len(items) < 10:
            character.addMessage("not enough maggots")
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
        counter = 0
        for item in items:
            if counter >= 10:
                break
            counter += 1
            self.container.removeItem(item)

        # spawn the new item
        new = src.items.itemMap["BioMass"]()
        self.container.addItem(new,(self.xPosition+1,self.yPosition,self.zPosition))

    def getLongInfo(self):
        text = """
item: MaggotFermenter

description:
A maggot fermenter produces bio mass from vat maggots.

Place 10 vat maggots to the left/west of the maggot fermenter.
Activate the maggot fermenter to produce biomass.

"""
        return text


src.items.addType(MaggotFermenter)

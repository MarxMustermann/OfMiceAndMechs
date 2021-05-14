import src


class Sorter(src.items.Item):
    type = "Sorter"

    """
    call superclass constructor with modified parameters
    """

    def __init__(self):
        super().__init__()

        self.display = src.canvas.displayChars.sorter
        self.name = "sorter"
        self.coolDown = 10
        self.coolDownTimer = -self.coolDown

        self.attributesToStore.extend(["coolDown", "coolDownTimer"])

    """
    """

    def apply(self, character, resultType=None):
        super().apply(character, silent=True)

        # fetch input scrap
        itemFound = None
        for item in self.container.getItemByPosition((self.xPosition - 1, self.yPosition, 0))
            itemFound = item
            break

        compareItemFound = None
        for item in self.container.getItemByPosition((self.xPosition, self.yPosition - 1, 0))
                compareItemFound = item
                break

        if src.gamestate.gamestate.tick < self.coolDownTimer + self.coolDown:
            character.addMessage(
                "cooldown not reached. Wait %s ticks"
                % (self.coolDown - (src.gamestate.gamestate.tick - self.coolDownTimer),)
            )
            return
        self.coolDownTimer = src.gamestate.gamestate.tick

        # refuse to produce without resources
        if not itemFound:
            character.addMessage("no items available")
            return
        if not compareItemFound:
            character.addMessage("no compare items available")
            return

        # remove resources
        self.container.removeItem(itemFound)

        if itemFound.type == compareItemFound.type:
            targetPos = (self.xPosition, self.yPosition + 1, 0)
        else:
            targetPos = (self.xPosition + 1, self.yPosition, 0)

        targetFull = False
        new = itemFound
        if (self.xPosition + 1, self.yPosition) in self.container.itemByCoordinates:
            if new.walkable:
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
                    if item.walkable == False:
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

        self.container.addItem(itemFound,targetPos)

    def getLongInfo(self):
        text = """
item: Sorter

description:
A sorter can sort items.

To sort item with a sorter place the item you want to compare against on the north.
Place the item or items to be sorted on the west of the sorter.
Activate the sorter to sort an item.
Matching items will be moved to the south and non matching items will be moved to the east.

"""
        return text


src.items.addType(Sorter)

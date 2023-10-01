import src

class Scraper(src.items.Item):
    """
    ingame item to destroy other items
    """

    type = "Scraper"

    def __init__(self):
        """
        set up internal state
        """

        self.coolDown = 10
        self.coolDownTimer = -self.coolDown
        self.charges = 3

        super().__init__(display=src.canvas.displayChars.scraper)
        self.name = "scraper"
        self.description = "A scrapper shreds items to scrap"
        self.usageInfo = """
Place an item to the west and activate the scrapper to shred an item.
"""

    # bug: should destroy the item instead of placing scrap
    def apply(self, character):
        """
        handle a character trying to use this item to destroy another item

        Parameters:
            character: the character trying to use the item
        """

        super().apply(character)

        # fetch input scrap
        itemFound = None
        for item in self.container.getItemByPosition((self.xPosition-1,self.yPosition,self.zPosition)):
            itemFound = item
            break

        if (
            src.gamestate.gamestate.tick < self.coolDownTimer + self.coolDown
            and not self.charges
        ):
            character.addMessage(
                "cooldown not reached. Wait {} ticks".format(self.coolDown - (src.gamestate.gamestate.tick - self.coolDownTimer))
            )
            return

        if self.charges:
            self.charges -= 1
        else:
            self.coolDownTimer = src.gamestate.gamestate.tick

        # refuse to produce without resources
        if not itemFound:
            character.addMessage("no items available")
            return

        targetFull = False
        if (self.xPosition+1,self.yPosition,self.zPosition) in self.container.itemByCoordinates:
            if (
                len(self.container.itemByCoordinates[(self.xPosition+1,self.yPosition,self.zPosition)])
                > 15
            ):
                targetFull = True
            for item in self.container.itemByCoordinates[(self.xPosition+1,self.yPosition,self.zPosition)]:
                if item.walkable == False:
                    targetFull = True

        if targetFull:
            character.addMessage(
                "the target area is full, the machine does not produce anything"
            )
            return

        # remove resources
        self.container.removeItem(item)

        # spawn scrap
        new = src.items.itemMap["Scrap"](amount=1)
        self.container.addItem(new,(self.xPosition + 1,self.yPosition,self.zPosition))

src.items.addType(Scraper)

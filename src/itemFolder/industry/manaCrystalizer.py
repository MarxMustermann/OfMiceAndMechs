import src


class ManaCrystalizer(src.items.Item):
    """
    ingame item to destroy other items
    """

    type = "ManaCrystalizer"

    def __init__(self):
        """
        set up internal state
        """

        super().__init__(display=src.canvas.displayChars.scraper)
        self.name = "mana crystalizer"

    def apply(self, character):
        # spawn mana crystal
        new = src.items.itemMap["ManaCristal"](amount=1)
        self.container.addItem(new,(self.xPosition + 1,self.yPosition,self.zPosition))
        character.addMessage("you crystalize some mana")

src.items.addType(ManaCrystalizer)

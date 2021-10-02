import src

class CorpseShredder(src.items.Item):
    """
    ingame item producing fertilizer components from corpses
    """

    type = "CorpseShredder"


    def __init__(self):
        """
        configure superclass
        """

        self.activated = False
        super().__init__(display=src.canvas.displayChars.corpseShredder)
        self.name = "corpse shredder"
        self.description = """
A corpse shredder produces mold feed from corpses.
If corpses and MoldSpores are supplied it produces seeded mold feed
"""
        self.usageInfo = """
Place corpse/mold seed to the west of the bloom shredder.
Activate the corpse shredder to produce mold feed/seeded mold feed.
"""

    def apply(self, character):
        """
        handle a character tying to use the item to shred a corpse

        Parameters:
            character: the character using the item
        """

        corpse = None
        moldSpores = []

        for item in self.container.getItemByPosition((self.xPosition - 1, self.yPosition, 0)):
            if item.type == "Corpse":
                corpse = item
            if item.type == "MoldSpore":
                moldSpores.append(item)

        # refuse to produce without resources
        if not corpse:
            character.addMessage("no corpse")
            return

        targetFull = False
        items = self.container.getItemByPosition((self.xPosition + 1, self.yPosition,0))
        if len(items) > 15:
            targetFull = True
        for item in items:
            if item.walkable == False:
                targetFull = True

        if targetFull:
            character.addMessage(
                "the target area is full, the machine does not produce anything"
            )
            return

        # remove resources
        self.container.removeItem(corpse)

        for i in range(0, corpse.charges // 100):
            if moldSpores:
                self.container.removeItem(moldSpores.pop())
                new = src.items.itemMap["SeededMoldFeed"]()
            else:
                # spawn the new item
                new = src.items.itemMap["MoldFeed"]()
            self.container.addItem(new,( self.xPosition + 1,self.yPosition,self.zPosition))

src.items.addType(CorpseShredder)

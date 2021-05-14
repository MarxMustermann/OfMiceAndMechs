import src

"""
"""


class CorpseShredder(src.items.Item):
    type = "CorpseShredder"

    """
    call superclass constructor with modified paramters and set some state
    """

    def __init__(self):
        self.activated = False
        super().__init__(display=src.canvas.displayChars.corpseShredder)
        self.name = "corpse shredder"

    """
    """

    def apply(self, character):
        super().apply(character, silent=True)

        corpse = None
        moldSpores = []

        for item in self.container.getItemByPosition((self.xPosition - 1, self.yPosition, self.xPosition)):
            if isinstance(item, Corpse):
                corpse = item
            if isinstance(item, MoldSpore):
                moldSpores.append(item)

        # refuse to produce without resources
        if not corpse:
            character.addMessage("no corpse")
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
        self.container.removeItem(corpse)

        for i in range(0, corpse.charges // 100):
            if moldSpores:
                self.container.removeItem(moldSpores.pop())
                new = src.items.itemMap["SeededMoldFeed"]()
            else:
                # spawn the new item
                new = src.items.itemMap["MoldFeed"]()
            self.container.addItem(new,( self.xPosition + 1,self.yPosition,self.zPosition))

    def getLongInfo(self):
        text = """
item: CorpseShredder

description:
A corpse shredder produces mold feed from corpses.
If corpses and MoldSpores are supplied it produces seeded mold feed

Place corpse/mold seed to the west of the bloom shredder.
Activate the corpse shredder to produce mold feed/seeded mold feed.

"""
        return text


src.items.addType(CorpseShredder)

import src


class SeededMoldFeed(src.items.Item):
    """
    ingame item that is basically seed for agriculture
    """

    type = "SeededMoldFeed"

    def __init__(self):
        """
        conigure super class
        """

        super().__init__(display=src.canvas.displayChars.seededMoldFeed)
        self.name = "seeded mold feed"
        self.description = "This is mold feed mixed with mold spores"
        self.usageInfo = """
Place it on the ground and activate it to start mold growth.
The seeded mold feed grows stronger then a mold spore on its own.
"""

        self.walkable = True
        self.bolted = False

    def apply(self, character):
        """
        handle a character trying to activate the item

        Parameters:
            character: the character activating the item
        """

        if self.container.isRoom:
            character.addMessage("this needs to be placed outside to be used")
            return

        self.startSpawn()
        character.addMessage("you activate the seeded mold feed")

    def startSpawn(self):
        """
        make the item register to start spawning mold in x ticks
        """
        event = src.events.RunCallbackEvent(
            src.gamestate.gamestate.tick
            + (2 * self.xPosition + 3 * self.yPosition + src.gamestate.gamestate.tick)
            % 10,
        )
        event.setCallback({"container": self, "method": "spawn"})
        self.terrain.addEvent(event)

    def spawn(self):
        """
        make the item spawn new mold
        """

        new = src.items.itemMap["Mold"]()
        self.container.addItem(new,self.getPosition())
        new.charges = 8
        new.startSpawn()
        self.destroy(generateScrap=False)

    def destroy(self, generateScrap=True):
        """
        get destroyed without leaving anything
        """

        super().destroy(generateScrap=False)

src.items.addType(SeededMoldFeed)

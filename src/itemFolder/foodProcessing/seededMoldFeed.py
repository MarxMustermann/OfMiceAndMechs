import src


class SeededMoldFeed(src.items.Item):
    type = "SeededMoldFeed"

    def __init__(self):
        super().__init__(display=src.canvas.displayChars.seededMoldFeed)
        self.name = "seeded mold feed"
        self.walkable = True
        self.bolted = False

    def apply(self, character):
        if not self.terrain:
            character.addMessage("this needs to be placed outside to be used")
            return

        self.startSpawn()
        character.addMessage("you activate the seeded mold feed")

    def startSpawn(self):
        event = src.events.RunCallbackEvent(
            src.gamestate.gamestate.tick
            + (2 * self.xPosition + 3 * self.yPosition + src.gamestate.gamestate.tick)
            % 10,
        )
        event.setCallback({"container": self, "method": "spawn"})
        self.terrain.addEvent(event)

    def spawn(self):
        new = src.items.itemMap["Mold"]()
        self.container.addItem(new,self.getPosition())
        new.charges = 8
        new.startSpawn()
        self.destroy(generateSrcap=False)

    def getLongInfo(self):
        return """
item: SeededMoldFeed

description:

This is mold feed mixed with mold spores.
Place it on the ground and activate it to start mold growth.
The seeded mold feed grows stronger then a mold spore on its own.
"""

    def destroy(self, generateSrcap=True):
        super().destroy(generateSrcap=False)


src.items.addType(SeededMoldFeed)

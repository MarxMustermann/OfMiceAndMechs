import src


class MoldSpore(src.items.Item):
    """
    ingame item that spawns mold
    """

    type = "MoldSpore"
    name = "mold spore"
    description = "grows into mold"
    usageInfo = """
put it on the ground and activate it to plant it
"""
    walkable = True
    bolted = False

    def __init__(self):
        """
        set up internal state
        """
        super().__init__(display=src.canvas.displayChars.moldSpore)

    def apply(self, character, forceSpawn=0):
        """
        handle a character using this item
        by spawning mold

        Parameters:
            character: the character spawning the mold
        """

        if not self.container:
            character.addMessage("this needs to be placed outside to be used")
            return
        if not forceSpawn:
            self.startSpawn()
        else:
            self.spawn(forceSpawn=forceSpawn)
        character.addMessage("you activate the mold spore")

    def startSpawn(self):
        """
        schedule spawining more mold
        """

        event = src.events.RunCallbackEvent(
            src.gamestate.gamestate.tick
            + (2 * self.xPosition + 3 * self.yPosition + src.gamestate.gamestate.tick)
            % 10,
        )
        event.setCallback({"container": self, "method": "spawn"})
        self.container.addEvent(event)

    def spawn(self,forceSpawn=0):
        """
        spawn more mold
        """

        if not self.container:
            return

        new = src.items.itemMap["Mold"]()
        self.container.addItem(new,self.getPosition())
        if not forceSpawn:
            new.startSpawn()
        else:
            new.spawn(forceSpawn=forceSpawn)
        self.destroy(generateScrap=False)

src.items.addType(MoldSpore)

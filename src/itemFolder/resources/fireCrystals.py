import src


class FireCrystals(src.items.Item):
    type = "FireCrystals"

    def __init__(self):

        super().__init__(display=src.canvas.displayChars.fireCrystals)
        self.walkable = True
        self.name = "fireCrystals"

    def apply(self, character):
        character.addMessage("The fire crystals start sparkling")
        self.startExploding()

    def startExploding(self):
        if not self.xPosition:
            return
        event = src.events.RunCallbackEvent(
            src.gamestate.gamestate.tick
            + 2
            + (2 * self.xPosition + 3 * self.yPosition + src.gamestate.gamestate.tick)
            % 10,
        )
        event.setCallback({"container": self, "method": "explode"})
        self.container.addEvent(event)

    def explode(self):
        self.destroy()

    def destroy(self, generateSrcap=False):
        if not self.xPosition or not self.yPosition:
            return

        new = Explosion()
        self.container.addItem(new,self.getPosition())
        event = src.events.RunCallbackEvent(
            src.gamestate.gamestate.tick + 1
        )
        event.setCallback({"container": new, "method": "explode"})
        self.container.addEvent(event)

        new = Explosion()
        self.container.addItems(new,self.getPosition())
        event = src.events.RunCallbackEvent(
            src.gamestate.gamestate.tick + 1
        )
        event.setCallback({"container": new, "method": "explode"})
        self.container.addEvent(event)

        new = Explosion()
        self.container.addItem(new,self.getPosition())
        event = src.events.RunCallbackEvent(
            src.gamestate.gamestate.tick + 1
        )
        event.setCallback({"container": new, "method": "explode"})
        self.container.addEvent(event)

        new = Explosion()
        self.container.addItem(new,self.getPosition())
        event = src.events.RunCallbackEvent(
            src.gamestate.gamestate.tick + 1
        )
        event.setCallback({"container": new, "method": "explode"})
        self.container.addEvent(event)

        new = Explosion()
        self.container.addItems(new,self.getPosition())
        event = src.events.RunCallbackEvent(
            src.gamestate.gamestate.tick + 1
        )
        event.setCallback({"container": new, "method": "explode"})
        self.container.addEvent(event)

        super().destroy(generateSrcap=False)


src.items.addType(FireCrystals)

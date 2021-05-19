import src


class Bomb(src.items.Item):
    """
    ingame item to kill things and destroy stuff
    """

    type = "Bomb"

    def __init__(self):
        """
        initialise state
        """

        super().__init__(display=src.canvas.displayChars.bomb)

        self.name = "bomb"
        self.description = "designed to explode"
        self.usageInfo = """
The explosion will damage/destroy everything on the current tile or the container.

Activate it to trigger a exlosion.
"""

        self.bolted = False
        self.walkable = True

    def apply(self, character):
        """
        handle a character trying to use this item
        by exploding

        Parameters:
            character: the character trying to use this item
        """

        self.destroy()

    def destroy(self, generateSrcap=True):
        """
        handle this item getting destroyed
        by exploding
        """

        xPosition = self.xPosition
        yPosition = self.yPosition

        if xPosition:
            new = Explosion()
            new.bolted = False
            self.container.addItem(new,(self.xPosition,self.yPosition,self.zPosition))
            event = src.events.RunCallbackEvent(
                src.gamestate.gamestate.tick + 1
            )
            event.setCallback({"container": new, "method": "explode"})
            self.container.addEvent(event)

            new = Explosion()
            new.bolted = False
            self.container.addItem(new,(self.xPosition-1,self.yPosition,self.zPosition))
            event = src.events.RunCallbackEvent(
                src.gamestate.gamestate.tick + 1
            )
            event.setCallback({"container": new, "method": "explode"})
            self.container.addEvent(event)

            new = Explosion()
            new.bolted = False
            self.container.addItem(new,(self.xPosition,self.yPosition-1,self.zPosition))
            event = src.events.RunCallbackEvent(
                src.gamestate.gamestate.tick + 1
            )
            event.setCallback({"container": new, "method": "explode"})
            self.container.addEvent(event)

            new = Explosion()
            new.bolted = False
            self.container.addItem(new,(self.xPosition+1,self.yPosition,self.zPosition))
            event = src.events.RunCallbackEvent(
                src.gamestate.gamestate.tick + 1 
            )
            event.setCallback({"container": new, "method": "explode"})
            self.container.addEvent(event)

            new = Explosion()
            new.bolted = False
            self.container.addItem(new,(self.xPosition,self.yPosition+1,self.zPosition))
            event = src.events.RunCallbackEvent(
                src.gamestate.gamestate.tick + 1
            )
            event.setCallback({"container": new, "method": "explode"})
            self.container.addEvent(event)

        super().destroy()

        """
        if xPosition and yPosition:
            for item in self.container.itemByCoordinates[(xPosition,yPosition)]:
                if item == self:
                    continue
                if item.type == "Explosion":
                    continue
                item.destroy()
        """

src.items.addType(Bomb)

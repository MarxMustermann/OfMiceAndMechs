import src

class Bomb(src.items.Item):
    type = "Bomb"

    '''
    almost straightforward state initialization
    '''
    def __init__(self):

        super().__init__(display=src.canvas.displayChars.bomb)

        self.name = "bomb"
        
        self.bolted = False
        self.walkable = True

    def getLongInfo(self):

        text = """

A simple Bomb. It explodes when destroyed.

The explosion will damage/destroy everything on the current tile or the container.

Activate it to trigger a exlosion.

"""
        return text

    def apply(self,character):
        self.destroy()

    def destroy(self, generateSrcap=True):
        xPosition = self.xPosition
        yPosition = self.yPosition

        if xPosition:
            new = Explosion(creator=self)
            new.xPosition = self.xPosition
            new.yPosition = self.yPosition
            new.bolted = False
            self.container.addItems([new])
            event = src.events.RunCallbackEvent(src.gamestate.gamestate.tick+1,creator=self)
            event.setCallback({"container":new,"method":"explode"})
            self.container.addEvent(event)

            new = Explosion(creator=self)
            new.xPosition = self.xPosition-1
            new.yPosition = self.yPosition
            new.bolted = False
            self.container.addItems([new])
            event = src.events.RunCallbackEvent(src.gamestate.gamestate.tick+1,creator=self)
            event.setCallback({"container":new,"method":"explode"})
            self.container.addEvent(event)

            new = Explosion(creator=self)
            new.xPosition = self.xPosition
            new.yPosition = self.yPosition-1
            new.bolted = False
            self.container.addItems([new])
            event = src.events.RunCallbackEvent(src.gamestate.gamestate.tick+1,creator=self)
            event.setCallback({"container":new,"method":"explode"})
            self.container.addEvent(event)

            new = Explosion(creator=self)
            new.xPosition = self.xPosition+1
            new.yPosition = self.yPosition
            new.bolted = False
            self.container.addItems([new])
            event = src.events.RunCallbackEvent(src.gamestate.gamestate.tick+1,creator=self)
            event.setCallback({"container":new,"method":"explode"})
            self.container.addEvent(event)

            new = Explosion(creator=self)
            new.xPosition = self.xPosition
            new.yPosition = self.yPosition+1
            new.bolted = False
            self.container.addItems([new])
            event = src.events.RunCallbackEvent(src.gamestate.gamestate.tick+1,creator=self)
            event.setCallback({"container":new,"method":"explode"})
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

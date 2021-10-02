import src
import random


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

        character.addMessage("the bomb starts to fizzle")
        event = src.events.RunCallbackEvent(
            src.gamestate.gamestate.tick+random.randint(1,4)
        )
        event.setCallback({"container": self, "method": "destroy"})
        self.container.addEvent(event)

    def destroy(self, generateScrap=True):
        """
        handle this item getting destroyed
        by exploding
        """

        xPosition = self.xPosition
        yPosition = self.yPosition
        zPosition = self.zPosition
        container = self.container

        super().destroy()

        if xPosition:
            new = src.items.itemMap["Explosion"]()
            new.bolted = False
            container.addItem(new,(xPosition,yPosition,zPosition))
            event = src.events.RunCallbackEvent(
                src.gamestate.gamestate.tick + 1
            )
            event.setCallback({"container": new, "method": "explode"})
            container.addEvent(event)

            new = src.items.itemMap["Explosion"]()
            new.bolted = False
            container.addItem(new,(xPosition-1,yPosition,zPosition))
            event = src.events.RunCallbackEvent(
                src.gamestate.gamestate.tick + 1
            )
            event.setCallback({"container": new, "method": "explode"})
            container.addEvent(event)

            new = src.items.itemMap["Explosion"]()
            new.bolted = False
            container.addItem(new,(xPosition,yPosition-1,zPosition))
            event = src.events.RunCallbackEvent(
                src.gamestate.gamestate.tick + 1
            )
            event.setCallback({"container": new, "method": "explode"})
            container.addEvent(event)

            new = src.items.itemMap["Explosion"]()
            new.bolted = False
            container.addItem(new,(xPosition+1,yPosition,zPosition))
            event = src.events.RunCallbackEvent(
                src.gamestate.gamestate.tick + 1
            )
            event.setCallback({"container": new, "method": "explode"})
            container.addEvent(event)

            new = src.items.itemMap["Explosion"]()
            new.bolted = False
            container.addItem(new,(xPosition,yPosition+1,zPosition))
            event = src.events.RunCallbackEvent(
                src.gamestate.gamestate.tick + 1
            )
            event.setCallback({"container": new, "method": "explode"})
            container.addEvent(event)

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

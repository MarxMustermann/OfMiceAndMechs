import src
import random

class FireCrystals(src.items.Item):
    """
    ingame item used as ressource to build bombs and stuff
    should have the habit to explode at inconvienent times
    """

    type = "FireCrystals"
    walkable = True
    name = "fireCrystals"
    isStepOnActive = True

    def __init__(self):
        """
        set up internal state
        """

        super().__init__(display=src.canvas.displayChars.fireCrystals)

    def doStepOnAction(self, character):
        if random.choice([True,False]):
            character.addMessage("you step on an fire crystal")
            self.apply(character)

    def apply(self, character):
        """
        handle a character trying to use this item
        by starting to explode

        Parameters:
            character: the character trying to use the item
        """

        character.addMessage("The fire crystals start sparkling")
        self.startExploding()

    def startExploding(self):
        """
        schedule an explosion
        """

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
        """
        actually explode
        """

        self.destroy()

    def destroy(self, generateScrap=False):
        """
        destroy the item
        
        Parameters:
            generateScrap: flag to toggle leaving residue
        """

        if not self.xPosition or not self.yPosition:
            return

        new = src.items.itemMap["Explosion"]()
        event = src.events.RunCallbackEvent(
            src.gamestate.gamestate.tick + 1
        )
        event.setCallback({"container": new, "method": "explode"})
        self.container.addEvent(event)

        new = src.items.itemMap["Explosion"]()
        self.container.addItem(new,(self.xPosition,self.yPosition,self.zPosition))
        event = src.events.RunCallbackEvent(
            src.gamestate.gamestate.tick + 1
        )
        event.setCallback({"container": new, "method": "explode"})
        self.container.addEvent(event)

        new = src.items.itemMap["Explosion"]()
        self.container.addItem(new,(self.xPosition+1,self.yPosition,self.zPosition))
        event = src.events.RunCallbackEvent(
            src.gamestate.gamestate.tick + 1
        )
        event.setCallback({"container": new, "method": "explode"})
        self.container.addEvent(event)

        new = src.items.itemMap["Explosion"]()
        self.container.addItem(new,(self.xPosition-1,self.yPosition,self.zPosition))
        event = src.events.RunCallbackEvent(
            src.gamestate.gamestate.tick + 1
        )
        event.setCallback({"container": new, "method": "explode"})
        self.container.addEvent(event)

        new = src.items.itemMap["Explosion"]()
        self.container.addItem(new,(self.xPosition,self.yPosition+1,self.zPosition))
        event = src.events.RunCallbackEvent(
            src.gamestate.gamestate.tick + 1
        )
        event.setCallback({"container": new, "method": "explode"})
        self.container.addEvent(event)

        new = src.items.itemMap["Explosion"]()
        self.container.addItem(new,(self.xPosition,self.yPosition-1,self.zPosition))
        event = src.events.RunCallbackEvent(
            src.gamestate.gamestate.tick + 1
        )
        event.setCallback({"container": new, "method": "explode"})
        self.container.addEvent(event)

        super().destroy(generateScrap=False)

src.items.addType(FireCrystals)

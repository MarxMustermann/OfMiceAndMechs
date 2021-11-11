import src
import random

class LandMine(src.items.Item):
    """
    ingame item used as ressource to build bombs and stuff
    should have the habit to explode at inconvienent times
    """

    type = "LandMine"
    walkable = True
    name = "landmine"
    isStepOnActive = True
    bolted = False

    def __init__(self):
        """
        set up internal state
        """

        super().__init__(display="_~")

    def pickUp(self, character):
        print("picked up")
        if random.random() < 0.5:
            self.destroy()
        else:
            super().pickUp(character)

    def doStepOnAction(self, character):
        character.addMessage("you step on a landmine")
        self.apply(character)

    def apply(self, character):
        """
        handle a character trying to use this item
        by starting to explode

        Parameters:
            character: the character trying to use the item
        """

        self.destroy()

    def destroy(self, generateScrap=True):
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

src.items.addType(LandMine)

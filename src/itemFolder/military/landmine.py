import random

import src


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

        super().__init__(display=src.canvas.displayChars.landmine)

        self.active = True

    def getLongInfo(self):
        """
        return a longer than normal description text

        Returns:
            the description text
        """

        text = super().getLongInfo()
        text += f"""

This item explodes when stepped on.
The explosion covers 4 of the 5 nearby fields.
So you get a chance to evade the explosion.

The explosion happens in 2 phases.
You get hit with 30 damage directly.
You get extra damage, if you wait around and do not move out of the explosion.
This will hit you with 50 more explosion damage.

"""
        return text

    def configure(self,character):
        if self.active:
            character.addMessage("you defuse the landmine, that takes 30 ticks")
            character.timeTaken += 30
            self.active = False
        else:
            character.addMessage("you fuse the landmine again, that takes 50 ticks")
            character.timeTaken += 50
            self.active = True

    def pickUp(self, character):
        if self.active and random.random() < 0.5:
            self.destroy()
        else:
            super().pickUp(character)

    def doStepOnAction(self, character):
        if self.active:
            character.addMessage("you step on an active landmine")
            self.apply(character)

    def render(self):
        if self.active:
            return self.display
        else:
            return "_~"

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

        if src.gamestate.gamestate.mainChar in self.container.characters:
            src.interaction.playSound("explosion","importantActions")

        offsets = [(0,0,0),(1,0,0),(-1,0,0),(0,1,0),(0,-1,0)]
        random.shuffle(offsets)

        for offset in offsets[:-1]:
            new = src.items.itemMap["Explosion"]()
            self.container.addItem(new,self.getPosition(offset=offset))
            event = src.events.RunCallbackEvent(
                src.gamestate.gamestate.tick + 1
            )
            event.setCallback({"container": new, "method": "explode"})
            self.container.addEvent(event)
            self.container.addAnimation(new.getPosition(),"explosion",5,{})
            for character in self.container.getCharactersOnPosition(self.getPosition(offset=offset)):
                character.hurt(30,reason="hurt by an exploding land mine")

        super().destroy(generateScrap=False)

src.items.addType(LandMine)

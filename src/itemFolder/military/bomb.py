import src
import random


class Bomb(src.items.Item):
    """
    ingame item to kill things and destroy stuff
    """

    type = "Bomb"
    name = "bomb"
    description = "designed to explode"
    usageInfo = """
The explosion will damage/destroy everything on the current tile or the container.

Activate it to trigger a exlosion.
"""

    bolted = False
    walkable = True

    def __init__(self):
        """
        initialise state
        """

        super().__init__(display=src.canvas.displayChars.bomb)

    def apply(self, character):
        """
        handle a character trying to use this item
        by exploding

        Parameters:
            character: the character trying to use this item
        """

        character.addMessage("the bomb starts to fizzle")
        event = src.events.RunCallbackEvent(
            #src.gamestate.gamestate.tick+random.randint(1,4)+delay
            src.gamestate.gamestate.tick+1
        )
        event.setCallback({"container": self, "method": "destroy"})
        self.container.addEvent(event)

    def destroy(self, generateScrap=True):
        """
        destroy the item
        
        Parameters:
            generateScrap: flag to toggle leaving residue
        """

        if not self.xPosition or not self.yPosition:
            return

        offsets = [(0,0),(1,0),(-1,0),(0,1),(0,-1)]
        random.shuffle(offsets)

        delay = 1
        if isinstance(self.container,src.rooms.Room):
            delay = 2

        for offset in offsets[:-1]:
            new = src.items.itemMap["Explosion"]()
            self.container.addItem(new,self.getPosition(offset=offset))
            event = src.events.RunCallbackEvent(
                src.gamestate.gamestate.tick + delay
            )
            event.setCallback({"container": new, "method": "explode"})
            self.container.addEvent(event)

            self.container.addAnimation(new.getPosition(),"explosion",5,{})
            for character in self.container.getCharactersOnPosition(self.getPosition(offset=offset)):
                character.hurt(30,reason="hurt by an exploding land mine")

        super().destroy(generateScrap=False)

src.items.addType(Bomb)

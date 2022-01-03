import src
import random

class Bloom(src.items.Item):
    """
    ingame item used as a food source
    """

    type = "Bloom"
    name = "bloom"
    description = "blossomed mold"
    bolted = False
    walkable = True
    dead = False

    def __init__(self):
        """
        set up internal state
        """

        super().__init__(display=src.canvas.displayChars.bloom)

        self.attributesToStore.extend(["dead"])

    def apply(self, character):
        """
        handle a character trying to use this item

        Parameters:
            character: the character trying to use this item
        """

        if not self.container:
            character.addMessage("this needs to be placed to be used")
            return

        if self.dead:
            character.satiation += 100
            self.destroy(generateScrap=False)
            character.addMessage("you eat the dead bloom and gain 100 satiation")
        else:
            character.satiation += 115
            if character.satiation > 1000:
                character.satiation = 1000
            self.destroy(generateScrap=False)
            character.addMessage("you eat the bloom and gain 115 satiation")

    def startSpawn(self):
        """
        schedule spawning new mold
        """

        if not (self.dead or self.xPosition is None or self.yPosition is None):
            event = src.events.RunCallbackEvent(
                src.gamestate.gamestate.tick
                + (
                    2 * self.xPosition
                    + 3 * self.yPosition
                    + src.gamestate.gamestate.tick
                )
                % 10000,
            )
            event.setCallback({"container": self, "method": "spawn"})
            self.container.addEvent(event)

    def pickUp(self, character):
        """
        handle getting picked up by a character

        Parameters:
            character: the character picking the item uo
        """

        self.bolted = False
        self.localSpawn()
        self.dead = True
        super().pickUp(character)

    def spawn(self):
        """
        swapn new mold
        """

        if self.dead:
            return
        if not (self.xPosition and self.yPosition):
            return
        if not self.container:
            return
        direction = (random.randint(1, 13), random.randint(1, 13))
        newPos = (
            self.xPosition - self.xPosition % 15 + direction[0],
            self.yPosition - self.yPosition % 15 + direction[1],
            self.zPosition,
        )

        if not self.container.getItemByPosition(newPos):
            new = src.items.itemMap["Mold"]()
            self.container.addItem(new, newPos)
            new.startSpawn()

    def localSpawn(self):
        """
        spawn a new patch of mold
        """

        if not self.dead:
            new = src.items.itemMap["Mold"]()
            new.charges = 4
            self.container.addItem(new, self.getPosition())
            new.startSpawn()

    def getLongInfo(self):
        """
        return a longer description text than usual

        Returns:
            the description text
        """

        text = super().getLongInfo()

        satiation = 115
        if self.dead:
            satiation = 100
        text += """
you can eat it to gain %s satiation.
""" % (
            satiation
        )

        return text

    def destroy(self, generateScrap=True):
        """
        destroy this item and spawn new mold
        """

        self.localSpawn()

        super().destroy(generateScrap=False)

src.items.addType(Bloom)

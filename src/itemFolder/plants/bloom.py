import src
import random


class Bloom(src.items.Item):
    type = "Bloom"

    def __init__(self):
        super().__init__(display=src.canvas.displayChars.bloom)

        self.name = "bloom"
        self.bolted = False
        self.walkable = True
        self.dead = False
        self.attributesToStore.extend(["dead"])

    def apply(self, character):
        if not self.container:
            character.addMessage("this needs to be placed to be used")
            return

        if self.dead:
            character.satiation += 100
            self.destroy(generateSrcap=False)
            character.addMessage("you eat the dead bloom and gain 100 satiation")
        else:
            character.satiation += 115
            if character.satiation > 1000:
                character.satiation = 1000
            self.destroy(generateSrcap=False)
            character.addMessage("you eat the bloom and gain 115 satiation")

    def startSpawn(self):
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
        self.bolted = False
        self.localSpawn()
        self.dead = True
        super().pickUp(character)

    def spawn(self):
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

        if self.container.getItemByPosition(newPos):
            new = src.items.itemMap["Mold"]()
            self.container.addItem(new, newPos)
            new.startSpawn()

    def localSpawn(self):
        if not self.dead:
            new = src.items.itemMap["Mold"]()
            new.charges = 4
            self.container.addItem(new, self.getPosition())
            new.startSpawn()

    def getLongInfo(self):
        satiation = 115
        if self.dead:
            satiation = 100
        return """
item: Bloom

description:
This is a mold bloom.

you can eat it to gain %s satiation.
""" % (
            satiation
        )

    def destroy(self, generateSrcap=True):
        self.localSpawn()

        super().destroy(generateSrcap=False)


src.items.addType(Bloom)

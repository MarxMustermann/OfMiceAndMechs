import src
import random

class Corpse(src.items.Item):
    """
    ingame item that is a ressource and basically does nothing
    also it is food and dead people
    """

    type = "Corpse"

    def __init__(self):
        """
        initialise internal state
        """

        super().__init__(display=src.canvas.displayChars.corpse)

        self.name = "corpse"
        self.description = "something dead"
        self.usageInfo = """
Activate it to eat from it. Eating from a corpse will gain you 15 satiation and may hurt your stomage for 1 damage.

can be processed in a corpse shredder
"""

        self.charges = 1000
        self.attributesToStore.extend(["activated", "charges"])
        self.walkable = True
        self.bolted = False

    def getLongInfo(self):
        """
        return a longer than normal description text

        Returns:
            the description text
        """

        text = super().getLongInfo()
        text = """
The corpse has %s charges left.
""" % (
            self.charges
        )
        return text

    def apply(self, character):
        """
        handle a character trying to use this item
        by getting eaten

        Parameters:
            character: the character that tries to use the item
        """

        if isinstance(character, src.characters.Monster):
            if character.phase == 3:
                character.enterPhase4()
            else:
                if self.container and character.satiation < 950:
                    character.macroState["commandKeyQueue"] = [
                        ("j", []),
                        ("m", []),
                    ] + character.macroState["commandKeyQueue"]
            character.frustration -= 1
        else:
            character.frustration += 1

        if self.charges:
            character.satiation += 15
            if character.satiation > 1000:
                character.satiation = 1000
            self.charges -= 1
            character.addMessage("you eat from the corpse and gain 15 satiation")

            if character.satiation > random.randint(0,10000):
                character.hurt(1,reason="the solid food hurts your stomach")
        else:
            self.destroy(generateScrap=False)

src.items.addType(Corpse)

import src
import random

class GlassThrone(src.items.Item):
    """
    ingame item ment to be placed by characters and to mark things with
    """

    type = "GlassThrone"

    """
    call superclass constructor with modified paramters and set some state
    """

    def __init__(self):
        self.activated = False
        super().__init__("HH")
        self.walkable = False
        self.bolted = False
        self.name = "glass throne"
        self.description = """
A throne. Take control over the throne to win the game.
"""
        self.wavesSpawned = 0
        self.lastWave = None

    def apply(self,character):

        noSeekerStatus = True
        for statusEffect in character.statusEffects:
            if not statusEffect.type == "ThroneSeeker":
                continue
            noSeekerStatus = False

        if noSeekerStatus:
            character.addMessage("you need to climb a throne first")
        else:
            if character == src.gamestate.gamestate.mainChar:
                if src.gamestate.gamestate.stern.get("fixedImplant",False):
                    endingType = "good"
                else:
                    endingType = "bad"
                src.interaction.showRunOutro()
                text = f"""
You won the game! congratulations

You got the {endingType} ending.

Feel free to continue building your base.
I'll try to keep things interesting, but you reached official end of content now.

= press enter to continue =
"""
            src.interaction.showInterruptText(text)
            character.rank = 1
            character.changed("ascended")

    def getConfigurationOptions(self, character):
        """
        register the configuration options with superclass

        Parameters:
            character: the character trying to conigure the machine
        """

        options = super().getConfigurationOptions(character)
        if self.bolted:
            options["b"] = ("unbolt", self.unboltAction)
        else:
            options["b"] = ("bolt down", self.boltAction)
        return options

    def boltAction(self,character):
        self.bolted = True
        character.addMessage("you bolt down the Thone")
        character.changed("boltedItem",{"character":character,"item":self})

    def unboltAction(self,character):
        self.bolted = False
        character.addMessage("you unbolt the Thone")
        character.changed("unboltedItem",{"character":character,"item":self})

    def getLongInfo(self):
        if self.wavesSpawned:
            return f"""The Throne did not attune to you.

Collect all glass hearts and activate it to attune it.
"""
        else:
            return f"""The Throne is attuning to you.

Survive the wave to complete the attuning proccess.
"""
src.items.addType(GlassThrone)

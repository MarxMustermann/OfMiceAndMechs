import src
import random

class Throne(src.items.Item):
    """
    ingame item ment to be placed by characters and to mark things with
    """

    type = "Throne"

    """
    call superclass constructor with modified paramters and set some state
    """

    def __init__(self):
        self.activated = False
        super().__init__("TT")
        self.walkable = False
        self.bolted = False
        self.name = "throne"
        self.description = """
A throne. Take control over the throne to win the game.
"""
        self.wavesSpawned = 0
        self.lastWave = None

    def apply(self,character):
        hasAllSpecialItems = True
        currentTerrain = character.getTerrain()

        terrainPos = (currentTerrain.xPosition,currentTerrain.yPosition)

        foundMissingHeart = False
        for god in src.gamestate.gamestate.gods.values():
            if god["lastHeartPos"] == terrainPos:
                continue
            foundMissingHeart = True

        if foundMissingHeart:
            character.addMessage("you need to control all GlassHearts")
            return

        if character == src.gamestate.gamestate.mainChar:
            text = f"""
You control all GlassHearts and activate the throne.

The council acceps you as new leader.
The attacks on your base will stop now.

= press enter to continue =
"""
            src.interaction.showInterruptText(text)
            text = f"""
You won the game! congratulations

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

Survive {self.maxWaves-self.wavesSpawned} to complete the attuning proccess.
"""
src.items.addType(Throne)

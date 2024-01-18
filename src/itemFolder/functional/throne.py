import src


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
A throne. Use it to win the game.
"""

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
            character.addMessage("you need to control all special items")
            return

        character.changed("ascended",{"character":character})
        character.rank = 1

        if character == src.gamestate.gamestate.mainChar:
            text = """
You won the game and rule the world now. congratz.

I know the ending is cheap, but the game is a shadow of whait it should be.
I'm currently working on making this thing more fluid and hope to get tha actual game running.

I'd love to get feedback. Do not hestiate to contact me.

The game will continue to run, but there is not further content for you to see.
The rules changed ab bit, though.
The game will actually end now as soon as you loose a single glass heart, now.

= press enter to continue =
"""
            src.interaction.showInterruptText(text)

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

src.items.addType(Throne)

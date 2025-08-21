import src
import random

class Throne(src.items.Item):
    '''
    ingame item repesesenting the starting point to ascend to world leader
    '''
    type = "Throne"
    def __init__(self):
        self.activated = False
        super().__init__("TT")
        self.walkable = False
        self.bolted = False
        self.name = "throne"
        self.description = """
A throne. A symbol of power.
"""
        self.wavesSpawned = 0
        self.lastWave = None

    def apply(self,character):
        '''
        handly a character trying to get a promotion
        '''
        if character == src.gamestate.gamestate.mainChar:
            src.gamestate.gamestate.stern["failedAscend"] = True

        hasAllSpecialItems = True
        currentTerrain = character.getTerrain()

        terrainPos = (currentTerrain.xPosition,currentTerrain.yPosition)

        foundMissingHeart = False
        for god in src.gamestate.gamestate.gods.values():
            if god["lastHeartPos"] == terrainPos:
                continue
            foundMissingHeart = True

        if foundMissingHeart:
            submenu = src.menuFolder.textMenu.TextMenu("""
The throne rejects you.

You need to collect all GlassHarts to be accepted as supreme leader.
""")
            character.macroState["submenue"] = submenu
            character.runCommandString("~",nativeKey=True)

            character.changed("missing glass heart",{})

            character.addMessage("you need to control all GlassHearts")
            return

        text = f"""
You sit on the Throne, but you realize:

You need to take the glass throne at (7,7,0)

= press enter to continue =
"""
        submenu = src.menuFolder.textMenu.TextMenu(text)
        character.macroState["submenue"] = submenu
        character.runCommandString("~",nativeKey=True)

        noSeekerStatus = True
        for statusEffect in character.statusEffects:
            if not statusEffect.type == "ThroneSeeker":
                continue
            noSeekerStatus = False

        if noSeekerStatus:
            newEffect = src.statusEffects.statusEffectMap["ThroneSeeker"]()
            character.addStatusEffect(newEffect)

        character.changed("told to ascend")

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
src.items.addType(Throne)

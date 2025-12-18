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

        if not character.rank or character.rank > 2:

            submenu = src.menuFolder.textMenu.TextMenu("""
You touch the throne and a shock runns through you.

You need to be rank 2 to interact with the throne.
""")
            character.macroState["submenue"] = submenu
            character.runCommandString("~",nativeKey=True)
            character.hurt(40,reason="touching the throne")
            return


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

        noSeekerStatus = True
        for statusEffect in character.statusEffects:
            if not statusEffect.type == "ThroneSeeker":
                continue
            noSeekerStatus = False

        if noSeekerStatus:
            newEffect = src.statusEffects.statusEffectMap["ThroneSeeker"]()
            character.addStatusEffect(newEffect)

            text = f"""
You sit on the Throne and tendril connect to you body.
They dig through your flesh and reach you implant.

It unlocks something inside you implant.
Something you did not know about.

= press enter to continue =
"""
            submenu = src.menuFolder.textMenu.TextMenu(text)
            submenu.followUp = {"container":self,"method":"doMagicUpgrade","params":{"character":character}}
            character.macroState["submenue"] = submenu
            character.runCommandString("~",nativeKey=True)
        else:
            self.offerTeleport({"character":character})

        character.changed("told to ascend")

    def doMagicUpgrade(self,extraInfo):
        character = extraInfo["character"]
        character.hasMagic = True

        text = f"""
You feel a strange new power.

You can cast spells now.
press P to cast a spell.
press p ro recast the last spell you cast.

The spells consume mana from the local terrain.
The amount of mana available on the current terrain should be shown on you HUD now.

= press enter to continue =
"""
        submenu = src.menuFolder.textMenu.TextMenu(text)
        submenu.followUp = {"container":self,"method":"offerTeleport","params":{"character":character}}
        character.macroState["submenue"] = submenu
        character.runCommandString("~",nativeKey=True)

    def offerTeleport(self,extraInfo):
        character = extraInfo["character"]

        text = f"""
You need to visit the true Throne on the terrain (7,7,0) to reach rank 1.

Do you you want to teleport there now?

"""
        options = [("yes","yes"),("no","no")]
        submenu = src.menuFolder.selectionMenu.SelectionMenu(text,options)
        submenu.tag = "throneTeleport"
        submenu.followUp = {"container":self,"method":"teleport","params":{"character":character}}
        character.macroState["submenue"] = submenu
        character.runCommandString("~",nativeKey=True)

        character.changed("told to ascend")

    def teleport(self,extraInfo):
        if extraInfo.get("selection") != "yes":
            return

        character = extraInfo["character"]
        target_terrain_position = (7,7)
        src.magic.teleportToTerrain(character, target_terrain_position, spawnOutside=True)

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

import src

class CorpseAnimator(src.items.Item):
    """
    an ingame item giving the character spawning item
    """

    type = "CorpseAnimator"
    attributesToStore = []
    commandOptions = []

    def __init__(self, filled=False):
        """
        setting properties of the base class
        """

        super().__init__()

        self.name = "corpse animator"
        self.description = "A machine that animates corpses"
        self.usageInfo = """
Put a corpse into the corpse animator to prepare for animating a corpse.
You can fill it by activating it with a corpse in your inventory.

Activate a filled corpse animator to spawn a ghul
"""

        self.runsCommands = True
        self.filled = filled
        self.commands = {}
        if not self.attributesToStore:
            self.attributesToStore.extend(super().attributesToStore)
            self.attributesToStore.extend(["filled", "commands"])

        if not self.commandOptions:
            self.attributesToStore.extend(super().commandOptions)
            self.commandOptions = [
                ("born", "set command for newly animated ghuls"),
            ]


    def render(self):
        """
        render the growth tank depending on the fill state 

        Returns:
            how the growth tank should be shown
        """

        if self.filled:
            return src.canvas.displayChars.corpseAnimator_filled
        else:
            return src.canvas.displayChars.corpseAnimator_unfilled

    """
    manually eject character
    """

    def apply(self, character):
        """
        refill or spawn a new npc depending on fill status

        Parameters
            character: the character trying to something with the growth tank
        """

        if self.filled:
            self.eject(originalActor=character)
        else:
            self.refill(character)

    def refill(self, character):
        """
        refill the growth tank

        Parameters
            character: the character trying to refill the growth tank
        """

        corpse = None
        for item in character.inventory:
            if isinstance(item, src.items.itemMap["Corpse"]):
                corpse = item
        if corpse:
            character.inventory.remove(corpse)
            self.filled = True
        else:
            character.addMessage(
                "you need to have a corpse to refill the corpse animator"
            )

    def eject(self, character=None, originalActor=None):
        """
        spawn a new npc

        Parameters:
            character: the character to eject (only used in story)
        """

        # emtpy growth tank
        self.filled = False

        #bad code: should be somewhere else
        #bad code: redundant code
        def getRandomName(seed1=0, seed2=None):
            """
            generates a random name

            Parameters:
                seed1: rng seed
                seed2: rng seed

            Returns:
                the generated name
            """

            if seed2 is None:
                seed2 = seed1 + (seed1 // 5)

            """
            firstName = config.names.characterFirstNames[
                seed1 % len(config.names.characterFirstNames)
            ]
            lastName = config.names.characterLastNames[
                seed2 % len(config.names.characterLastNames)
            ]

            name = "%s %s"%(firstName,lastName,)
            """
            name = "worker"
                
            return name

        # add character
        if not character:
            name = getRandomName(
                self.xPosition + self.container.timeIndex,
                self.yPosition + self.container.timeIndex,
            )
            character = src.characters.Ghul()
            if originalActor:
                character.faction = originalActor.faction

        # inhabit character
        # character.fallUnconcious()
        # character.hasFloorPermit = False
        self.container.addCharacter(character, self.xPosition + 1, self.yPosition)
        # character.revokeReputation(amount=4,reason="beeing helpless")
        # character.runCommandString("j")
        character.macroState["macros"]["j"] = "Jf"
        self.runCommand("born", character=character)

        return character

src.items.addType(CorpseAnimator)

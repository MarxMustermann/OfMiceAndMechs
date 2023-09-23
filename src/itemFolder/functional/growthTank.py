import src

class GrowthTank(src.items.Item):
    """
    an ingame item giving the character spawning item
    """

    type = "GrowthTank"

    def __init__(self, filled=False):
        """
        setting properties of the base class
        """

        super().__init__()

        self.name = "growth tank"
        self.description = "A growth tank produces NPCs."
        self.usageInfo = """
Fill a growth tank to prepare it for generating an npc.
You can fill it by activating it with a full goo flask in your inventory.

Activate a filled growth tank to spawn a new npc.
Wake the NPC by taking to the NPC.

You talk to NPCs by pressing h and selecting the NPC to talk to.
"""

        self.runsCommands = True
        self.filled = filled
        self.commands = {}
        self.attributesToStore.extend(["filled", "commands"])

        self.commandOptions = [
                ("born", "set command for newly born npcs"),
            ]


    def render(self):
        """
        render the growth tank depending on the fill state 

        Returns:
            how the growth tank should be shown
        """

        if self.filled:
            return src.canvas.displayChars.growthTank_filled
        else:
            return src.canvas.displayChars.growthTank_unfilled

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
        character.addMessage("you bolt down the GrowthTank")
        character.changed("boltedItem",{"character":character,"item":self})

    def unboltAction(self,character):
        self.bolted = False
        character.addMessage("you unbolt the GrowthTank")
        character.changed("unboltedItem",{"character":character,"item":self})

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
            self.eject()
        else:
            self.refill(character)

    def refill(self, character):
        """
        refill the growth tank

        Parameters
            character: the character trying to refill the growth tank
        """

        flask = None
        for item in character.inventory:
            if isinstance(item, src.items.itemMap["GooFlask"]):
                if item.uses == 100:
                    flask = item
        if flask:
            flask.uses = 0
            flask.changed()
            self.filled = True
            self.changed()
        else:
            character.addMessage(
                "you need to have a full goo flask to refill the growth tank"
            )

    def eject(self, character=None):
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
            character = src.characters.Character(
                src.canvas.displayChars.staffCharactersByLetter[name[0].lower()],
                name=name,
            )

            character.solvers = [
                "SurviveQuest",
                "Serve",
                "NaiveMoveQuest",
                "MoveQuestMeta",
                "NaiveActivateQuest",
                "ActivateQuestMeta",
                "NaivePickupQuest",
                "PickupQuestMeta",
                "DrinkQuest",
                "ExamineQuest",
                "FireFurnaceMeta",
                "CollectQuestMeta",
                "WaitQuest",
                "NaiveDropQuest",
                "DropQuestMeta",
            ]

        # inhabit character
        # character.fallUnconcious()
        # character.hasFloorPermit = False
        self.container.addCharacter(character, self.xPosition + 1, self.yPosition)
        # character.revokeReputation(amount=4,reason="being helpless")
        # character.runCommandString("j")
        character.macroState["macros"]["j"] = "Jf"
        self.runCommand("born", character=character)

        return character

src.items.addType(GrowthTank)

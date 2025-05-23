import src
from src.helpers import getRandomName


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
        self.gooCharges = 0

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

    def boltAction(self, character):
        self.bolted = True
        character.addMessage("you bolt down the GrowthTank")
        character.changed("boltedItem", {"character": character, "item": self})

    def unboltAction(self, character):
        self.bolted = False
        character.addMessage("you unbolt the GrowthTank")
        character.changed("unboltedItem", {"character": character, "item": self})

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
            self.eject(character)
            character.changed("spawned clone")
            character.timeTaken += 2
        else:
            self.refill(character)

    def getItems(self, character, item_type):
        items = []
        for offset in [(-1, 0, 0), (1, 0, 0), (0, 1, 0), (0, -1, 0)]:
            for item in self.container.getItemByPosition(self.getPosition(offset=offset)):
                if isinstance(item, item_type):
                    items.append(item)
        for item in character.inventory:
            if isinstance(item, item_type):
                items.append(item)

        return items

    def getFlasks(self, character=None):
        return self.getItems(character, src.items.itemMap["GooFlask"])

    def getImplants(self, character):
        return self.getItems(character, src.items.itemMap["Implant"])

    def refill(self, character):
        """
        refill the growth tank

        Parameters
            character: the character trying to refill the growth tank
        """

        flasks = self.getFlasks(character)
        if not flasks:
            character.changed("no flask", {})
            character.addMessage("you need to have 2 full goo flasks to refill the growth tank")
            return

        while self.gooCharges <= 100:
            for flask in flasks[:]:
                self.gooCharges += flask.uses
                character.addMessage(f"you fill the GrowthTank with {flask.uses} now it has {self.gooCharges}")

                if flask in character.inventory:
                    character.inventory.remove(flask)
                    character.inventory.append(src.items.itemMap["Flask"]())
                else:
                    pos = flask.getPosition()
                    self.container.removeItem(flask)
                    self.container.addItem(src.items.itemMap["Flask"](), pos)

                if self.gooCharges > 100:
                    break
            break

        if self.gooCharges > 100:
            self.gooCharges -= 100
            self.filled = True
            character.addMessage("the growthtank is filled now")

    def eject(self, character=None):
        """
        spawn a new npc
        """

        """
        tmpdisabled implant requirement
        implants = self.getImplants(character)

        if not len(implants):
            character.addMessage("you need to supply an implant to grow a clone")
            return None

        implant = implants[0]

        if implant in character.inventory:
            character.inventory.remove(implant)
        else:
            self.container.removeItem(implant)
        """

        # emtpy growth tank
        self.filled = False

        name = getRandomName(
            self.xPosition + self.container.timeIndex,
            self.yPosition + self.container.timeIndex,
        )
        character = src.characters.characterMap["Clone"](
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

        flask = src.items.itemMap["GooFlask"]()
        flask.uses = self.gooCharges
        self.gooCharges = 0
        character.flask = flask

        # inhabit character
        # character.fallUnconcious()
        # character.hasFloorPermit = False
        self.container.addCharacter(character, self.xPosition + 1, self.yPosition)
        # character.revokeReputation(amount=4,reason="being helpless")
        character.runCommandString("j")
        #self.runCommand("born", character=character)

        return character

src.items.addType(GrowthTank)

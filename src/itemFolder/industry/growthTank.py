import src

"""
an character spawning item
"""


class GrowthTank(src.items.Item):
    type = "GrowthTank"

    """
    almost straightforward state initialization
    """

    def __init__(self, filled=False):
        super().__init__()

        name = "growth tank"
        self.filled = filled
        self.commands = {}
        self.attributesToStore.extend(["filled", "commands"])

    def render(self):
        if self.filled:
            return src.canvas.displayChars.growthTank_filled
        else:
            return src.canvas.displayChars.growthTank_unfilled

    """
    manually eject character
    """

    def apply(self, character):

        if not self.room:
            character.addMessage("this machine can only be used within rooms")
            return

        super().apply(character, silent=True)
        if self.filled:
            self.eject()
        else:
            flask = None
            for item in character.inventory:
                if isinstance(item, GooFlask):
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

    def configure(self, character):
        options = [("addCommand", "add command"), ("reset", "reset")]
        self.submenue = src.interaction.SelectionMenu(
            "what do you want to do?", options
        )
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.configure2
        self.character = character

    def configure2(self):
        if self.submenue.selection == "addCommand":
            options = []
            options.append(("born", "set command for newly born npcs"))

            self.submenue = src.interaction.SelectionMenu(
                "Setting command for handling triggers.", options
            )
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = {
                "container": self,
                "method": "setCommand",
            }
        if self.submenue.selection == "reset":
            self.character.addMessage("you reset the machine")
            self.commands = {}

    """
    ejecting a character
    """

    def eject(self, character=None):
        # emtpy growth tank
        self.filled = False

        """
        generate a name
        bad code: should be somewhere else
        bad code: redundant code
        """

        def getRandomName(seed1=0, seed2=None):
            if seed2 == None:
                seed2 = seed1 + (seed1 // 5)
            return (
                config.names.characterFirstNames[
                    seed1 % len(config.names.characterFirstNames)
                ]
                + " "
                + config.names.characterLastNames[
                    seed2 % len(config.names.characterLastNames)
                ]
            )

        # add character
        if not character:
            name = getRandomName(
                self.xPosition + self.room.timeIndex,
                self.yPosition + self.room.timeIndex,
            )
            character = characters.Character(
                src.canvas.displayChars.staffCharactersByLetter[name[0].lower()],
                self.xPosition + 1,
                self.yPosition,
                name=name,
                creator=self,
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
                "WaitQuest" "NaiveDropQuest",
                "DropQuestMeta",
            ]

        # inhabit character
        # character.fallUnconcious()
        # character.hasFloorPermit = False
        self.room.addCharacter(character, self.xPosition + 1, self.yPosition)
        # character.revokeReputation(amount=4,reason="beeing helpless")
        # character.macroState["commandKeyQueue"] = [("j",[])]
        character.macroState["macros"]["j"] = "Jf"
        self.runCommand("born", character=character)

        return character

    def getLongInfo(self):
        text = """
item: GrowthTank

description:
A growth tank produces NPCs.

Fill a growth tank to prepare it for generating an npc.
You can fill it by activating it with a full goo flask in your inventory.

Activate a filled growth tank to spawn a new npc.
Wake the NPC by taking to the NPC.

You talk to NPCs by pressing h and selecting the NPC to talk to.

"""
        return text


src.items.addType(GrowthTank)

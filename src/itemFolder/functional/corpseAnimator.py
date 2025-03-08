import src
from src.helpers import getRandomName


class CorpseAnimator(src.items.Item):
    """
    an ingame item giving the character spawning item
    """

    type = "CorpseAnimator"

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

Activate a filled corpse animator to spawn a ghoul
"""

        self.runsCommands = True
        self.filled = filled
        self.commands = {"born":"j"}

        self.commandOptions = [
                ("born", "set command for newly animated ghouls"),
            ]

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
        character.addMessage("you bolt down the CorpseAnimater")
        character.changed("boltedItem",{"character":character,"item":self})

    def unboltAction(self,character):
        self.bolted = False
        character.addMessage("you unbolt the CorpseAnimater")
        character.changed("unboltedItem",{"character":character,"item":self})


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
            self.container.addAnimation(character.getPosition(),"showchar",1,{"char":"--"})
            self.container.addAnimation(self.getPosition(),"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#fff", "black"),"OO")})
        else:
            character.addMessage(
                "you need to have a corpse to refill the corpse animator"
            )
            self.container.addAnimation(character.getPosition(),"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#f00", "black"),"][")})
            self.container.addAnimation(self.getPosition(),"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#f00", "black"),"XX")})

    def eject(self, character=None, originalActor=None):
        """
        spawn a new npc

        Parameters:
            character: the character to eject (only used in story)
        """

        # emtpy growth tank
        self.filled = False

        # add character
        if not character:
            name = getRandomName(
                self.xPosition + self.container.timeIndex,
                self.yPosition + self.container.timeIndex,
            )
            character = src.characters.characterMap["Ghoul"]()
            if originalActor:
                character.faction = originalActor.faction

        # inhabit character
        # character.fallUnconcious()
        # character.hasFloorPermit = False
        self.container.addCharacter(character, self.xPosition + 1, self.yPosition)
        # character.revokeReputation(amount=4,reason="being helpless")
        # character.runCommandString("j")
        character.macroState["macros"]["j"] = "Jf"
        self.runCommand("born", character=character)

        self.container.addAnimation(self.getPosition(),"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#fff", "black"),"OO")})
        self.container.addAnimation(self.getPosition(offset=(1,0,0)),"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#fff", "black"),"@ ")})

        return character

src.items.addType(CorpseAnimator)

import src


class StasisTank(src.items.Item):
    """
    ingame item that removes characters from the game and readds them later
    """

    type = "StasisTank"

    def __init__(self):
        """
        configure super class
        """

        super().__init__()

        self.display = src.canvas.displayChars.stasisTank

        self.name = "stasis tank"
        self.description = "Allows you to enter stasis. In stasis you do not need food and can not do anything"
        self.usageInfo = """
Use an empty stasis tank to enter it.
In stasis you do not need food and can not do anything.
You cannot leave the stasis tank on your own.

Use an occupied stasis tank to eject the inhabitant.
The ejected character will be placed to the south of the stasis tank and will start to act again.
"""

        self.character = None
        self.bolted = True
        self.walkable = False
        self.character = None
        self.characterTimeEntered = None

    def eject(self):
        """
        eject the current inhabitant
        """

        if self.character:
            self.container.addCharacter(self.character, self.xPosition, self.yPosition + 1)
            self.character.stasis = False
            self.character = None
            self.characterTimeEntered = None

    def apply(self, character):
        """
        handle a character trying to use the stasis tank

        Parameters:
            character: the character trying to use the item
        """

        if self.character and self.character.stasis:
            self.eject()
        else:
            options = []
            options.append(("enter", "yes"))
            options.append(("noEnter", "no"))
            self.submenue = src.interaction.SelectionMenu(
                "The stasis tank is empty. You will not be able to leave it on your on.\nDo you want to enter it?",
                options,
            )
            self.character = character
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.enterSelection

    def enterSelection(self):
        """
        handle the character having decided to enter or not.
        take the character in if the character decided so
        """

        if self.submenue.selection == "enter":
            self.character.stasis = True
            self.container.removeCharacter(self.character)
            self.character.addMessage(
                "you entered the stasis tank. You will not be able to move until somebody activates it"
            )
            self.characterTimeEntered = src.gamestate.gamestate.tick
        else:
            self.character.addMessage("you do not enter the stasis tank")

    # bad code: nonfunctional experimental code
    def configure(self, character):
        """
        handle a character trying to set a timeout for automatic reawakening

        Parameters:
            character: the character trying to use the item
        """

        character.addMessage(src.gamestate.gamestate.tick)
        character.addMessage(self.characterTimeEntered)
        if src.gamestate.gamestate.tick > self.characterTimeEntered + 100:
            self.eject()

src.items.addType(StasisTank)

import src


class Command(src.items.Item):
    """
    ingame item that makes characters using the item run commands
    """

    type = "Command"

    def __init__(self):
        """
        configure super class
        """

        super().__init__(display=src.canvas.displayChars.command)

        self.name = "command"
        self.description = "A command is written on it"
        self.usageInfo = "Activate it to run command"

        self.bolted = False
        self.walkable = True
        self.command = ""
        self.extraName = ""
        self.level = 1
        self.repeat = False

        self.attributesToStore.extend(["command", "extraName", "level", "description"])

    def configure(self, character):
        self.repeat = not self.repeat
        character.addMessage("you set the command to repeat: %s"%(self.repeat,))

    def apply(self, character):
        """
        handle a character using the command

        Parameters:
            character: the character trying to use the command
        """

        if isinstance(character, src.characters.Monster):
            return

        if self.level == 1:
            self.runPayload(character)
        else:
            options = [
                ("runCommand", "run command"),
                ("setName", "set name"),
            ]
            if self.level > 2:
                options.append(("setDescription", "set description"))
            if self.level > 3:
                options.append(("rememberCommand", "store command in memory"))

            self.submenue = src.interaction.SelectionMenu(
                "Do you want to reconfigure the machine?", options
            )
            character.macroState["submenue"] = self.submenue
            character.macroState["submenue"].followUp = self.advancedActions
            self.character = character
            pass

    # bad code: should be splitted up
    def advancedActions(self):
        """
        do a selected action from a list of actions
        """

        if self.submenue.selection == "runCommand":
            self.runPayload(self.character)
        elif self.submenue.selection == "setName":
            self.submenue = src.interaction.InputMenu("Enter the name")
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.setName
        elif self.submenue.selection == "setDescription":
            self.submenue = src.interaction.InputMenu("Enter the description")
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.setDescription
        elif self.submenue.selection == "rememberCommand":

            if not self.name or self.name == "":
                self.character.addMessage("command not loaded: command has no name")
                return

            properName = True
            for char in self.name[:-1]:
                if not (char.isupper() or char == " "):
                    properName = False
                    break
            if self.name[-1].isupper():
                properName = False
                pass

            if properName:
                self.character.macroState["macros"][self.name] = self.command
                self.character.addMessage("loaded command to macro storage")
            else:
                self.character.addMessage(
                    'command not loaded: name not in propper format. Should be capital letters except the last letter. example "EXAMPLE NAMe"'
                )
        else:
            self.character.addMessage("action not found")

    def setName(self):
        """
        set the name of the command
        """

        self.name = self.submenue.text
        self.character.addMessage("set command name to %s" % (self.name))

    def setDescription(self):
        """
        set the description of the command
        """

        self.description = self.submenue.text
        self.character.addMessage("set command description")

    def runPayload(self, character):
        """
        run the stored command on a character

        Parameters:
            character: the character to run the command on
        """

        if self.repeat:
            character.runCommandString("j")
        character.runCommandString(self.command)

    def setPayload(self, command):
        """
        set the stored command

        Parameters:
            command: the command (string,list) to set
        """

        import copy

        self.command = copy.deepcopy(command)

    def getDetailedInfo(self):
        """
        return a longer than normal description

        Returns:
            the description
        """

        if self.extraName == "":
            return super().getDetailedInfo() + " "
        else:
            return super().getDetailedInfo() + " - " + self.extraName

    def getLongInfo(self):
        """
        returns a longer than normal description of the item

        Returns:
            the description
        """

        text = super().getLongInfo()

        compressedMacro = ""
        for keystroke in self.command:
            if len(keystroke) == 1:
                compressedMacro += keystroke
            else:
                compressedMacro += "/" + keystroke + "/"

        text += """

This command has the name: %s
""" % (
            self.extraName
            )

        text += """

This is a level %s item.
""" % (
            self.level
        )

        text += """

it holds the command:

%s

""" % (
            compressedMacro
        )
        return text

src.items.addType(Command)

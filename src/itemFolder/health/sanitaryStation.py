import src

class SanitaryStation(src.items.Item):
    """
    ingame item to check the health status and run actions depending on the result
    this is inteded to be used as way for the player to automate the game
    it is also intended to be used to automate the game 
    """

    type = "SanitaryStation"

    def __init__(self):
        """
        configure super class
        """

        super().__init__()

        self.name = "sanitary station"
        self.description = "use it to collect items"
        self.display = "SS"
        self.bolted = False
        self.walkable = False
        self.commands = {}
        self.healthThreshold = 10
        self.satiationThreshold = 100
        self.frustrationThreshold = 10000

        self.attributesToStore.extend(
                [
                    "commands",
                    "healthThreshold",
                    "satiationThreshold",
                ]
            )

    def apply(self, character):
        """
        run commands on an character depending on its health

        Parameters:
            character: the character to heathcheck
        """

        super().apply(character)

        if character.health < self.healthThreshold:
            character.addMessage("health needed")
            self.runCommand("healing", character)
            return
        if character.frustration > self.frustrationThreshold:
            character.addMessage("depressed")
            self.runCommand("depressed", character)
            return
        if character.satiation < self.satiationThreshold:
            character.addMessage("satiation needed")
            self.runCommand("hungry", character)
            return
        character.addMessage("nothing needed")

    # abstraction: should be replaced by super class function
    def configure(self, character):
        """
        offer an character a selection of actions to run
        
        Parameters:
            character: the character trying to use the item
        """
        options = [
            ("addCommand", "add command"),
            ("changeSetting", "change settings"),
            ("showSettings", "show settings"),
        ]
        self.submenue = src.interaction.SelectionMenu(
            "what do you want to do?", options
        )
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.configure2
        self.character = character

    # abstraction: should be replaced by super class function
    def configure2(self):
        """
        run the selected action
        """
        if self.submenue.selection == "addCommand":
            options = []
            options.append(("healing", "need healing"))
            options.append(("hungry", "need satiation"))
            options.append(("depressed", "need depressed"))
            self.submenue = src.interaction.SelectionMenu(
                "Setting command for handling triggers.", options
            )
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.setCommand
        if self.submenue.selection == "changeSetting":
            options = []
            options.append(("health", "set health threshold"))
            options.append(("satiation", "set satiation threshold"))
            options.append(("depressed", "set depressed threshold"))
            self.submenue = src.interaction.SelectionMenu(
                "Choose setting to set", options
            )
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.setSetting
            self.settingName = None
        if self.submenue.selection == "showSettings":
            self.submenue = src.interaction.TextMenu(
                "health threshold: %s\nsatiation threshold: %s"
                % (
                    self.healthThreshold,
                    self.satiationThreshold,
                )
            )
            self.character.macroState["submenue"] = self.submenue

    def setSetting(self):
        """
        set a machine setting
        """

        if not self.settingName:
            self.settingName = self.submenue.selection

            self.submenue = src.interaction.InputMenu("input the value")
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.setSetting
            return

        if self.settingName == "health":
            self.healthThreshold = int(self.submenue.text)
        if self.settingName == "satiation":
            self.satiationThreshold = int(self.submenue.text)
        if self.settingName == "depressed":
            self.frustrationThreshold = int(self.submenue.text)

    def setCommand(self):
        """
        set a command
        """

        itemType = self.submenue.selection

        commandItem = None
        for item in self.container.getItemByPosition(
            (self.xPosition, self.yPosition - 1)
        ):
            if item.type == "Command":
                commandItem = item

        if not commandItem:
            self.character.addMessage("no command found - place command to the north")
            return

        self.commands[itemType] = commandItem.command
        self.container.removeItem(commandItem)

        self.character.addMessage(
            "added command for %s - %s" % (itemType, commandItem.command)
        )
        return

    def runCommand(self, trigger, character=None):
        """
        run a command

        Parameters:
            
        """

        if character is None:
            character = self.character

        if trigger not in self.commands:
            return

        command = self.commands[trigger]

        character.runCommandString(command)

        character.addMessage(
            "running command to handle trigger %s - %s" % (trigger, command)
        )

    def fetchSpecialRegisterInformation(self):
        """
        returns some of the objects state to be stored ingame in a characters registers

        Returns:
            a dictionary containing the information
        """

        result = super().fetchSpecialRegisterInformation()

        result["healthThreshold"] = self.healthThreshold
        result["satiationThreshold"] = self.satiationThreshold
        result["frustrationThreshold"] = self.frustrationThreshold

        return result


src.items.addType(SanitaryStation)

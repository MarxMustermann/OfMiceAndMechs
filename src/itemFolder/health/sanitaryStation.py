import src

"""
"""


class SanitaryStation(src.items.Item):
    type = "SanitaryStation"

    """
    call superclass constructor with modified paramters
    """

    def __init__(self):
        super().__init__()

        self.name = "SanitaryStation"
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

    """
    collect items
    """

    def apply(self, character):
        super().apply(character, silent=True)

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

    def configure(self, character):
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

    def configure2(self):
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

        if character is None:
            character = self.character

        if trigger not in self.commands:
            return

        command = self.commands[trigger]

        convertedCommand = []
        for char in command:
            convertedCommand.append((char, "norecord"))

        character.macroState["commandKeyQueue"] = (
            convertedCommand + character.macroState["commandKeyQueue"]
        )
        character.addMessage(
            "running command to handle trigger %s - %s" % (trigger, command)
        )

    def getLongInfo(self):
        text = """
item: ItemCollector

description:
use it to collect items
"""
        return text

    def fetchSpecialRegisterInformation(self):
        result = super().fetchSpecialRegisterInformation()

        result["healthThreshold"] = self.healthThreshold
        result["satiationThreshold"] = self.satiationThreshold
        result["frustrationThreshold"] = self.frustrationThreshold

        return result


src.items.addType(SanitaryStation)

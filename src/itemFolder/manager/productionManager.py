import src


class ProductionManager(src.items.Item):
    type = "ProductionManager"

    """
    call superclass constructor with modified parameters
    """

    def __init__(self):
        self.commands = {}

        super().__init__(display=src.canvas.displayChars.productionManager)

        self.name = "production manager"

        self.bolted = False
        self.walkable = False

    def getLongInfo(self):

        commandsString = ""
        for (itemType, command) in self.commands.items():
            commandsString += "* " + itemType + " " + str(command) + "\n"

        text = """
item: ProductionManager

description:
allows to set commands for production of items.
job order can be inserted and commands can be run depending on the item the job order is for.

%s

commands:
%s

""" % (
            commandsString,
            self.commands,
        )
        return text

    def apply(self, character):
        if not (
            character.xPosition == self.xPosition
            and character.yPosition == self.yPosition - 1
        ):
            character.addMessage("this item can only be used from north")
            return

        if (
            character.macroState["recording"]
            and "auto" in character.macroState["macros"]
        ):
            optionText = "set recorded command"
        else:
            optionText = "start recording command"
        options = [
            ("runJobOrder", "run job order"),
            ("runCommand", "run command"),
            ("recordCommand", optionText),
            ("addCommand", "add command"),
        ]
        self.submenue = src.interaction.SelectionMenu(
            "what do you want to do?", options
        )
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.apply2
        self.character = character

        if "auto" in self.character.macroState["macros"]:
            self.macroSafe = self.character.macroState["macros"]["auto"][:]
        else:
            self.macroSafe = None

    def apply2(self):
        self.character.addMessage("self.submenue.selection")
        self.character.addMessage(self.submenue.selection)
        if self.submenue.selection == "runJobOrder":
            jobOrder = None
            for item in reversed(self.character.inventory):
                if (
                    item.type == "JobOrder"
                    and not item.done
                    and item.tasks[-1]["task"] == "produce"
                ):
                    jobOrder = item
                    break

            if not jobOrder:
                self.character.addMessage("no production job order found")
                return

            if jobOrder.tasks[-1]["toProduce"] not in self.commands:
                self.character.addMessage("no command for job order found")
                return

            itemType = jobOrder.tasks[-1]["toProduce"]
            command = self.commands[itemType]

            convertedCommand = []
            for char in command:
                convertedCommand.append((char, "norecord"))

            self.character.macroState["commandKeyQueue"] = (
                convertedCommand + self.character.macroState["commandKeyQueue"]
            )
            self.character.addMessage(
                "running command to produce %s - %s" % (itemType, command)
            )

        elif self.submenue.selection == "recordCommand":
            if (
                self.character.macroState["recording"]
                and "auto" in self.character.macroState["macros"]
            ):
                self.character.macroState["recording"] = False
                self.character.macroState["recordingTo"] = None
                del self.character.macroState["macros"]["auto"]
                options = []
                for key in itemMap.keys():
                    options.append((key, key))
                self.submenue = src.interaction.SelectionMenu(
                    "Setting command for producing item. What item do you want to set the command for?",
                    options,
                )
                self.character.macroState["submenue"] = self.submenue
                self.character.macroState["submenue"].followUp = self.setCommand2
            else:
                self.character.macroState["recording"] = True
                self.character.macroState["recordingTo"] = "auto"
                self.character.macroState["macros"]["auto"] = []
        elif self.submenue.selection == "runCommand":
            options = []
            for itemType in self.commands:
                options.append((itemType, itemType))

            if not options:
                self.character.addMessage("there are no commands set")
                return

            self.submenue = src.interaction.SelectionMenu(
                "Run command for producing item. select item to produce.", options
            )
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.runCommand
        elif self.submenue.selection == "addCommand":
            options = []
            for key in itemMap.keys():
                options.append((key, key))
            self.submenue = src.interaction.SelectionMenu(
                "Setting command for producing item. What item do you want to set the command for?",
                options,
            )
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.setCommand

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

    def setCommand2(self):
        itemType = self.submenue.selection

        if not len(self.macroSafe) > 1:
            return
        self.commands[itemType] = self.macroSafe[:-2]

        self.character.addMessage(
            "added command for %s - %s" % (itemType, self.commands[itemType])
        )

    def runCommand(self):
        itemType = self.submenue.selection
        command = self.commands[itemType]

        convertedCommand = []
        for char in command:
            convertedCommand.append((char, "norecord"))

        self.character.macroState["commandKeyQueue"] = (
            convertedCommand + self.character.macroState["commandKeyQueue"]
        )
        self.character.addMessage(
            "running command to produce %s - %s" % (itemType, command)
        )

    def getState(self):
        state = super().getState()
        state["commands"] = self.commands
        return state

    def setState(self, state):
        super().setState(state)
        if "commands" in state:
            self.commands = state["commands"]


src.items.addType(ProductionManager)

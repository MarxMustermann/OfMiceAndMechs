import src


class PavingGenerator(src.items.Item):
    type = "PavingGenerator"

    """
    call superclass constructor with modified parameters
    """

    def __init__(self, name="paving generator", creator=None, noId=False):
        self.coolDown = 100
        self.coolDownTimer = -self.coolDown
        self.charges = 3
        self.level = 1
        self.commands = {}

        super().__init__(display="PG", name=name)

        self.attributesToStore.extend(["coolDown", "coolDownTimer", "charges", "level"])

    """
    produce a paving
    """

    def apply(self, character, resultType=None):
        if not self.container:
            character.addMessage("this machine has be somewhere to be used")
            return

        # fetch input scrap
        scrap = None
        if not hasattr(self, "container"):
            if self.room:
                self.container = self.room
            else:
                self.container = self.terrain

        for item in self.container.getItemByPosition(
            (self.xPosition - 1, self.yPosition, self.zPosition)
        ):
            if item.type == "Scrap":
                scrap = item
                break
        if self.level > 1:
            if not scrap:
                for item in self.container.getItemByPosition(
                    (self.xPosition, self.yPosition + 1, self.zPosition)
                ):
                    if isinstance(item, itemMap["Scrap"]):
                        scrap = item
                        break
        if self.level > 2:
            if not scrap:
                for item in self.container.getItemByPosition(
                    (self.xPosition, self.yPosition - 1, self.zPosition)
                ):
                    if isinstance(item, itemMap["Scrap"]):
                        scrap = item
                        break

        if (
            src.gamestate.gamestate.tick < self.coolDownTimer + self.coolDown
            and not self.charges
        ):
            character.addMessage(
                "cooldown not reached. Wait %s ticks"
                % (self.coolDown - (src.gamestate.gamestate.tick - self.coolDownTimer),)
            )
            self.runCommand("cooldown", character)
            return

        # refuse to produce without resources
        if not scrap:
            character.addMessage("no scraps available")
            self.runCommand("material Scrap", character)
            return

        targetPos = (self.xPosition + 1, self.yPosition, self.zPosition)
        targetFull = False
        itemList = self.container.getItemByPosition(targetPos)

        if len(itemList) > 15:
            targetFull = True
        for item in itemList:
            if item.walkable == False:
                targetFull = True

        if targetFull:
            character.addMessage(
                "the target area is full, the machine does not produce anything"
            )
            self.runCommand("targetFull", character)
            return

        if self.charges:
            self.charges -= 1
        else:
            self.coolDownTimer = src.gamestate.gamestate.tick

        character.addMessage("you produce a paving")

        # remove resources
        if scrap.amount <= 1:
            self.container.removeItem(scrap)
        else:
            scrap.amount -= 1
            scrap.setWalkable()

        for i in range(1, 4):
            # spawn the metal bar
            new = src.items.itemMap["Paving"]()
            self.container.addItem(
                new, (self.xPosition + 1, self.yPosition, self.zPosition)
            )

        self.runCommand("success", character)

    def getLongInfo(self):
        directions = "west"
        if self.level > 1:
            directions += "/south"
        if self.level > 2:
            directions += "/north"
        text = """
item: ScrapCompactor

description:
This machine converts scrap into metal bars. Metal bars are a form of metal that can be used to produce other things.

Place scrap to the %s of the machine and activate it 

After using this machine you need to wait %s ticks till you can use this machine again.
""" % (
            directions,
            self.coolDown,
        )

        coolDownLeft = self.coolDown - (
            src.gamestate.gamestate.tick - self.coolDownTimer
        )
        if coolDownLeft > 0:
            text += """
Currently you need to wait %s ticks to use this machine again.

""" % (
                coolDownLeft,
            )
        else:
            text += """
Currently you do not have to wait to use this machine.

"""

        if self.charges:
            text += """
Currently the machine has %s charges

""" % (
                self.charges
            )
        else:
            text += """
Currently the machine has no charges

"""

        text += """
thie is a level %s item

""" % (
            self.level
        )
        return text

    def configure(self, character):
        options = [("addCommand", "add command")]
        self.submenue = src.interaction.SelectionMenu(
            "what do you want to do?", options
        )
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.apply2
        self.character = character

    def apply2(self):
        if self.submenue.selection == "runCommand":
            options = []
            for itemType in self.commands:
                options.append((itemType, itemType))
            self.submenue = src.interaction.SelectionMenu(
                "Run command for producing item. select item to produce.", options
            )
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.runCommand
        elif self.submenue.selection == "addCommand":
            options = []
            options.append(("success", "set success command"))
            options.append(("cooldown", "set cooldown command"))
            options.append(("targetFull", "set target full command"))
            options.append(("material Scrap", "set Scrap fetching command"))
            self.submenue = src.interaction.SelectionMenu(
                "Setting command for handling triggers.", options
            )
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.setCommand

    def setCommand(self):
        itemType = self.submenue.selection

        commandItem = None
        for item in self.container.getItemByPosition(
            (self.xPosition, self.yPosition - 1, self.zPosition)
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

    def runCommand(self, trigger, character):
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

    def getState(self):
        state = super().getState()
        state["commands"] = self.commands
        return state

    def setState(self, state):
        super().setState(state)
        if "commands" in state:
            self.commands = state["commands"]


src.items.addType(PavingGenerator)

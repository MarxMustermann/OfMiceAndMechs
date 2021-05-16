import src


class UniformStockpileManager(src.items.Item):
    """
    ingame item to repreent and manage a stockpile
    items will be nearby
    is intended to help the player with automation
    is used with prefabs and in logistics
    """

    type = "UniformStockpileManager"


    def __init__(self):
        """
        configure superclass
        """

        super().__init__(display=src.canvas.displayChars.uniformStockpileManager)

        self.name = "uniform stockpile manager"
        self.description = "stores items, but only a single item type"
        self.usageInfo = "needs to be placed in the center of a tile. The tile should be emtpy and mold free for proper function."

        self.bolted = False
        self.walkable = False

        self.storedItemType = None
        self.storedItemWalkable = None
        self.restrictStoredItemType = True
        self.restrictStoredItemWalkable = True
        self.numItemsStored = 0
        self.lastAction = ""

        self.attributesToStore.extend(
            [
                "commands",
                "numItemsStored",
                "storedItemType",
                "storedItemWalkable",
                "restrictStoredItemType",
                "restrictStoredItemWalkable",
            ]
        )
        self.objectsToStore.extend(["submenue", "character"])

        self.commands = {}
        self.submenue = None
        self.character = None
        self.blocked = False

    def getLongInfo(self):
        """
        return a longer than normal description text

        Returns:
            the description
        """

        text = super().getLongInfo()

        text += """
lastAction: %s
commands: %s
storedItemType: %s
storedItemWalkable: %s
restrictStoredItemType: %s
restrictStoredItemWalkable: %s
""" % (
            self.lastAction,
            self.commands,
            self.storedItemType,
            self.storedItemWalkable,
            self.restrictStoredItemType,
            self.restrictStoredItemWalkable,
        )
        return text

    # bug: this form of using interaction menus causes mixups when used by multiple characters at once
    def apply(self, character):
        """
        spwan an interaction menu offering a selection of actions and run them

        Parameters:
            character: the character using this item
        """

        if not (
            character.xPosition == self.xPosition
            and character.yPosition == self.yPosition - 1
        ):
            character.addMessage("this item can only be used from north")
            return

        if self.blocked:
            character.runCommandString("Js")
            character.addMessage("item blocked - auto retry")
            return
        self.blocked = True
        self.lastAction = "apply"

        options = [
                ("storeItem", "store item"),
                ("fetchItem", "fetch item"),
                ("clearInventory", "clear inventory"),
                ("fillInventory", "fill inventory"),
        ]
        self.submenue = src.interaction.SelectionMenu(
            "what do you want to do?", options
        )
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = {
            "container": self,
            "method": "apply2",
        }
        self.character = character

    def configure(self, character):
        """
        spaw a interaction meu to trigger complex/configuration actions

        Parameters:
            character: the character using the item
        """

        if self.blocked:
            character.runCommandString("sc")
            character.addMessage("item blocked - auto retry")
            return
        self.blocked = True

        self.lastAction = "configure"

        self.submenue = src.interaction.OneKeystrokeMenu(
            """
a: addCommand
s: machine settings
j: run job order
r: reset
"""
        )
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.configure2
        self.character = character

    # bad code: should be split up
    # bad code: should use new way of spawning interaction menus
    def configure2(self):
        """
        actually do the complex/configuration action
        """

        self.lastAction = "configure2"

        if self.submenue.keyPressed == "j":
            if not self.character.jobOrders:
                self.character.addMessage("no job order")
                self.blocked = False
                return

            self.character.addMessage("do job order stuff")
            jobOrder = self.character.jobOrders[-1]
            self.character.addMessage(jobOrder.getTask())
            if jobOrder.getTask()["task"] == "generateStatusReport":
                self.character.runCommandString("se.")
                jobOrder.popTask()
            self.character.addMessage(jobOrder.getTask())
            if jobOrder.getTask()["task"] == "configure machine":
                self.character.addMessage("configured machine")
                task = jobOrder.popTask()
                self.commands.update(task["commands"])
            self.blocked = False
            return

        if self.submenue.keyPressed == "a":
            options = []
            options.append(("empty", "set empty command"))
            options.append(("full", "set full command"))
            options.append(("wrong", "wrong item type or item"))

            self.submenue = src.interaction.SelectionMenu(
                "Setting command for handling triggers.", options
            )
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.setCommand
            return
        if self.submenue.keyPressed == "s":
            options = []
            options.append(("restrictStoredItemType", "restict stored item type"))
            options.append(("storedItemType", "stored item type"))
            options.append(("restrictStoredItemWalkable", "restict item size"))
            options.append(("storedItemWalkable", "stored item size"))

            self.submenue = src.interaction.SelectionMenu(
                "select setting to change.", options
            )
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.setMachineSettings
            self.settingType = None
            return
        if self.submenue.keyPressed == "r":
            self.character.addMessage("you reset the machine")
            self.storedItemType = None
            self.storedItemWalkable = False
            self.restrictStoredItemType = False
            self.restrictStoredItemWalkable = True
            self.numItemsStored = 0
            return
        self.blocked = False

    # abstraction: should use generalised code
    def setMachineSettings(self):
        """
        set the settings for the machine 
        """

        if self.settingType is None:
            self.settingType = self.submenue.selection

            self.submenue = src.interaction.InputMenu("input the value")
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.setMachineSettings

        rawValue = self.submenue.text
        if self.settingType == "restrictStoredItemType":
            if rawValue == "True":
                self.restrictStoredItemType = True
            else:
                self.restrictStoredItemType = False
        if self.settingType == "storedItemType":
            self.storedItemType = rawValue
        if self.settingType == "restrictStoredItemWalkable":
            if rawValue == "True":
                self.restrictStoredItemWalkable = True
            else:
                self.restrictStoredItemWalkable = False
        if self.settingType == "restrictStoredItemType":
            self.storedItemWalkable = bool(rawValue)

        self.blocked = False

    # bad code: should use superclass ability
    def runCommand(self, commandName):
        """
        runs a preconfigured command on a npc

        Parameters:
            commandName: the name of the command to run
        """

        if commandName not in self.commands:
            return
        command = self.commands[commandName]

        convertedCommand = []
        for char in command:
            convertedCommand.append((char, "norecord"))

        self.character.macroState["commandKeyQueue"] = (
            convertedCommand + self.character.macroState["commandKeyQueue"]
        )
        self.character.addMessage(
            "running command for trigger: %s - %s" % (commandName, command)
        )

    # bad code: should use superclass ability
    def setCommand(self):
        """
        sets a command to run under certain conditions
        """

        self.lastAction = "setCommand"
        trigger = self.submenue.selection

        commandItem = None
        for item in self.container.getItemByPosition(
            (self.xPosition, self.yPosition - 1)
        ):
            if item.type == "Command":
                commandItem = item

        if not commandItem:
            self.character.addMessage("no command found - place command to the north")
            self.blocked = False
            return

        self.commands[trigger] = commandItem.command
        self.container.removeItem(commandItem)

        self.character.addMessage(
            "added command for %s - %s" % (trigger, commandItem.command)
        )
        self.blocked = False
        return

    # bad code: should use superclass ability
    def apply2(self):
        """
        do actions depending on earlier selection
        """

        self.lastAction = "apply2"
        character = self.character

        if self.submenue.selection == "clearInventory":
            numItems = len(character.inventory)
            character.runCommandString("Js.j"*numItems)
        if self.submenue.selection == "fillInventory":
            numItems = character.maxInventorySpace-len(character.inventory)
            character.runCommandString("Js.sj"*numItems)
        if self.submenue.selection == "storeItem":
            if not self.character.inventory:
                self.character.addMessage("nothing in inventory")
                self.blocked = False
                return

            if self.restrictStoredItemType:
                if self.storedItemType is None:
                    self.storedItemType = self.character.inventory[-1].type
                else:
                    if not self.storedItemType == self.character.inventory[-1].type:
                        self.character.addMessage("wrong item type")
                        self.runCommand("wrong")
                        self.runCommand("wrongType")
                        self.blocked = False
                        return
            if self.restrictStoredItemWalkable:
                if self.storedItemWalkable is None:
                    self.storedItemWalkable = self.character.inventory[-1].walkable
                else:
                    if not (
                        self.storedItemWalkable == self.character.inventory[-1].walkable
                    ):
                        self.character.addMessage("wrong size")
                        self.runCommand("wrong")
                        self.runCommand("wrong size")
                        self.blocked = False
                        return

            if self.xPosition % 15 == 7 and self.yPosition % 15 == 7:
                if self.numItemsStored >= 140:
                    self.character.addMessage("stockpile full")
                    self.runCommand("full")
                    self.blocked = False
                    return

                sector = self.numItemsStored // 35
                offsetX = 6 - self.numItemsStored % 35 % 6 - 1
                offsetY = 6 - self.numItemsStored % 35 // 6 - 1

                command = ""
                if sector == 0:
                    command += str(offsetY) + "w"
                    command += str(offsetX) + "a"
                    command += "La"
                    command += str(offsetX) + "d"
                    command += str(offsetY) + "s"
                elif sector == 1:
                    command += str(offsetY) + "w"
                    command += str(offsetX) + "d"
                    command += "Ld"
                    command += str(offsetX) + "a"
                    command += str(offsetY) + "s"
                elif sector == 2:
                    command += "assd"
                    command += str(offsetY) + "s"
                    command += str(offsetX) + "a"
                    command += "La"
                    command += str(offsetX) + "d"
                    command += str(offsetY) + "w"
                    command += "dwwa"
                elif sector == 3:
                    command += "assd"
                    command += str(offsetY) + "s"
                    command += str(offsetX) + "d"
                    command += "Ld"
                    command += str(offsetX) + "a"
                    command += str(offsetY) + "w"
                    command += "dwwa"
            elif (
                self.xPosition % 15
                in (
                    6,
                    8,
                )
                and self.yPosition % 15 in (6, 8)
            ):
                if self.numItemsStored >= 32:
                    self.character.addMessage("stockpile full")
                    self.runCommand("full")
                    self.blocked = False
                    return

                row = self.numItemsStored // 6

                if self.xPosition % 15 == 6 and self.yPosition % 15 == 6:
                    rowMovUp = "w"
                    rowMovDown = "s"
                    colMovUp = "a"
                    colMovDown = "d"
                    command = ""
                    commandEnd = ""
                elif self.xPosition % 15 == 8 and self.yPosition % 15 == 6:
                    rowMovUp = "w"
                    rowMovDown = "s"
                    colMovUp = "d"
                    colMovDown = "a"
                    command = ""
                    commandEnd = ""
                elif self.xPosition % 15 == 6 and self.yPosition % 15 == 8:
                    rowMovUp = "s"
                    rowMovDown = "w"
                    colMovUp = "a"
                    colMovDown = "d"
                    command = "dssa"
                    commandEnd = "awwd"
                elif self.xPosition % 15 == 8 and self.yPosition % 15 == 8:
                    rowMovUp = "s"
                    rowMovDown = "w"
                    colMovUp = "d"
                    colMovDown = "a"
                    command = "assd"
                    commandEnd = "dwwa"

                if row < 4:
                    command += str(3 - row) + rowMovUp
                    command += (
                        str(5 - self.numItemsStored % 6) + colMovUp + "L" + rowMovUp
                    )
                    command += str(5 - self.numItemsStored % 6) + colMovDown
                    command += str(3 - row) + rowMovDown
                elif self.numItemsStored >= 24 and self.numItemsStored < 28:
                    command += (
                        str(4 - (self.numItemsStored - 24) % 4)
                        + colMovUp
                        + "L"
                        + colMovUp
                    )
                    command += str(4 - (self.numItemsStored - 24) % 4) + colMovDown
                elif self.numItemsStored >= 28 and self.numItemsStored < 32:
                    command += (
                        colMovUp
                        + rowMovDown
                        + str(3 - (self.numItemsStored - 28) % 4)
                        + colMovUp
                        + "L"
                        + colMovUp
                    )
                    command += (
                        str(3 - (self.numItemsStored - 28) % 4)
                        + colMovDown
                        + rowMovUp
                        + colMovDown
                    )
                command += commandEnd
            else:
                command = ""
                pass

            self.numItemsStored += 1

            self.character.runCommandString(command)
            self.character.addMessage("running command to store item %s" % (command))
            self.blocked = False
            return

        if self.submenue.selection == "fetchItem":
            if not self.numItemsStored:
                self.character.addMessage("stockpile empty")
                self.runCommand("empty")
                self.blocked = False
                return

            if len(self.character.inventory) == 10:
                self.character.addMessage("inventory full")
                self.blocked = False
                return

            self.numItemsStored -= 1

            if self.xPosition % 15 == 7 and self.yPosition % 15 == 7:
                sector = self.numItemsStored // 35
                offsetX = 6 - self.numItemsStored % 35 % 6 - 1
                offsetY = 6 - self.numItemsStored % 35 // 6 - 1

                command = ""
                if sector == 0:
                    command += str(offsetY) + "w"
                    command += str(offsetX) + "a"
                    command += "Ka"
                    command += str(offsetX) + "d"
                    command += str(offsetY) + "s"
                elif sector == 1:
                    command += str(offsetY) + "w"
                    command += str(offsetX) + "d"
                    command += "Kd"
                    command += str(offsetX) + "a"
                    command += str(offsetY) + "s"
                elif sector == 2:
                    command += "assd"
                    command += str(offsetY) + "s"
                    command += str(offsetX) + "a"
                    command += "Ka"
                    command += str(offsetX) + "d"
                    command += str(offsetY) + "w"
                    command += "dwwa"
                elif sector == 3:
                    command += "assd"
                    command += str(offsetY) + "s"
                    command += str(offsetX) + "d"
                    command += "Kd"
                    command += str(offsetX) + "a"
                    command += str(offsetY) + "w"
                    command += "dwwa"

            elif (
                self.xPosition % 15
                in (
                    6,
                    8,
                )
                and self.yPosition % 15 in (6, 8)
            ):
                if self.numItemsStored >= 32:
                    self.character.addMessage("stockpile full")
                    self.runCommand("full")
                    self.blocked = False
                    return

                row = self.numItemsStored // 6

                if self.xPosition % 15 == 6 and self.yPosition % 15 == 6:
                    rowMovUp = "w"
                    rowMovDown = "s"
                    colMovUp = "a"
                    colMovDown = "d"
                    command = ""
                    commandEnd = ""
                elif self.xPosition % 15 == 8 and self.yPosition % 15 == 6:
                    rowMovUp = "w"
                    rowMovDown = "s"
                    colMovUp = "d"
                    colMovDown = "a"
                    command = ""
                    commandEnd = ""
                elif self.xPosition % 15 == 6 and self.yPosition % 15 == 8:
                    rowMovUp = "s"
                    rowMovDown = "w"
                    colMovUp = "a"
                    colMovDown = "d"
                    command = "dssa"
                    commandEnd = "dwwa"
                elif self.xPosition % 15 == 8 and self.yPosition % 15 == 8:
                    rowMovUp = "s"
                    rowMovDown = "w"
                    colMovUp = "d"
                    colMovDown = "a"
                    command = "assd"
                    commandEnd = "awwd"

                if row < 4:
                    command += str(3 - row) + rowMovUp
                    command += (
                        str(5 - self.numItemsStored % 6) + colMovUp + "K" + rowMovUp
                    )
                    command += str(5 - self.numItemsStored % 6) + colMovDown
                    command += str(3 - row) + rowMovDown
                elif self.numItemsStored >= 24 and self.numItemsStored < 28:
                    command += (
                        str(4 - (self.numItemsStored - 24) % 4)
                        + colMovUp
                        + "K"
                        + colMovUp
                    )
                    command += str(4 - (self.numItemsStored - 24) % 4) + colMovDown
                elif self.numItemsStored >= 28 and self.numItemsStored < 32:
                    command += (
                        colMovUp
                        + rowMovDown
                        + str(3 - (self.numItemsStored - 28) % 4)
                        + colMovUp
                        + "K"
                        + colMovUp
                    )
                    command += (
                        str(3 - (self.numItemsStored - 28) % 4)
                        + colMovDown
                        + rowMovUp
                        + colMovDown
                    )
                command += commandEnd
            else:
                pass

            convertedCommand = []
            for char in command:
                convertedCommand.append((char, "norecord"))

            self.character.macroState["commandKeyQueue"] = (
                convertedCommand + self.character.macroState["commandKeyQueue"]
            )
            self.character.addMessage("running command to fetch item")
            self.blocked = False
            return
        self.blocked = False
        return

    def fetchSpecialRegisterInformation(self):
        """
        returns some of the objects state to be stored ingame in a characters registers

        Returns:
            a dictionary containing the information
        """

        result = super().fetchSpecialRegisterInformation()
        result["numItemsStored"] = self.numItemsStored
        result["storedItemType"] = self.storedItemType
        result["storedItemWalkable"] = self.storedItemWalkable
        result["restrictStoredItemType"] = self.restrictStoredItemType
        result["restrictStoredItemWalkable"] = self.restrictStoredItemWalkable
        if self.xPosition % 15 == 7 and self.yPosition % 15 == 7:
            result["maxAmount"] = 6 * 6 * 4
        elif (
            self.xPosition % 15 in (6,8,)
            and self.yPosition % 15 in (6, 8)
        ):
            result["maxAmount"] = 4 * 6 + 2 * 4
        else:
            result["maxAmount"] = 0
        return result

src.items.addType(UniformStockpileManager)

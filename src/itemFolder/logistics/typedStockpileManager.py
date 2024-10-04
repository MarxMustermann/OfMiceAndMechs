import src


class TypedStockpileManager(src.items.Item):
    """
    ingame item that manages item storage
    items are stored near the machine
    this is intended to relieve the player from one of the more complicated autmation tasks
    supports random access to items
    """

    type = "TypedStockpileManager"

    def __init__(self):
        """
        set up the internal state
        """

        self.freeItemSlots = {}

        self.freeItemSlots[1] = []
        self.freeItemSlots[2] = []
        self.freeItemSlots[3] = []
        self.freeItemSlots[4] = []

        for x in range(1, 7):
            for y in range(1, 7):
                if x == 7 or y == 7:
                    continue
                if y in (2, 5, 9, 12):
                    continue
                if x in (6, 8) and y in (6, 8):
                    continue
                self.freeItemSlots[1].append((x, y))

        for x in range(1, 7):
            for y in range(7, 14):
                if x == 7 or y == 7:
                    continue
                if y in (2, 5, 9, 12):
                    continue
                if x in (6, 8) and y in (6, 8):
                    continue
                self.freeItemSlots[2].append((x, y))

        for x in range(7, 14):
            for y in range(1, 7):
                if x == 7 or y == 7:
                    continue
                if y in (2, 5, 9, 12):
                    continue
                if x in (6, 8) and y in (6, 8):
                    continue
                self.freeItemSlots[3].append((x, y))

        for x in range(7, 14):
            for y in range(7, 14):
                if x == 7 or y == 7:
                    continue
                if y in (2, 5, 9, 12):
                    continue
                if x in (6, 8) and y in (6, 8):
                    continue
                self.freeItemSlots[4].append((x, y))

        self.slotsByItemtype = {}
        super().__init__(display=src.canvas.displayChars.typedStockpileManager)
        self.name = "typed stockpile manager"
        self.description = "managers stockpiles with different types of items"
        self.usageInfo = """
needs to be placed in the center of a tile. The tile should be emtpy and mold free for proper function.
"""

        self.bolted = False
        self.walkable = False

    def configure(self, character):
        """
        handle a character trying to configure this machine
        by offering a selection of possible actions

        Parameters:
            character: the character trying to use the machine
        """

        self.submenue = src.menuFolder.OneKeystrokeMenu.OneKeystrokeMenu(
            "what do you want to do?\n\nj: use job order"
        )
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.configure2
        self.character = character

    def configure2(self):
        """
        handle a character having selected what configuration task should be done
        by doing the selected task
        """
        if not self.character.jobOrders:
            return

        jobOrder = self.character.jobOrders[-1]

        if jobOrder.getTask()["task"] == "generateStatusReport":
            self.character.runCommandString("se.")
            jobOrder.popTask()

    def getLongInfo(self):
        """
        return a longer than normal description text

        Returns:
            the description text
        """

        text = super().getLongInfo()

        text += f"""
slotsByItemtype
{self.slotsByItemtype}
"""
        return text

    def apply(self, character):
        """
        handle a character trying to use this item
        by offering a selection of actions to do

        Parameters:
            character: the character trying to use the item
        """

        if not (
            character.xPosition == self.xPosition
            and character.yPosition == self.yPosition - 1
        ):
            character.addMessage("this item can only be used from north")
            return

        options = [
            ("storeItem", "store item"),
            ("fetchItem", "fetch item"),
            ("fetchByJobOrder", "fetch by job order"),
        ]
        self.submenue = src.menuFolder.SelectionMenu.SelectionMenu(
            "what do you want to do?", options
        )
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.apply2
        self.character = character

    def apply2(self):
        """
        handle a character having selected a action to do
        by running the action
        """

        if self.submenue.selection == "storeItem":
            if not self.freeItemSlots:
                self.character.addMessage("no free item slot")
                return

            if not self.character.inventory:
                self.character.addMessage("no item in inventory")
                return

            for (key, value) in self.freeItemSlots.items():
                if not value:
                    continue

                slot = value.pop()
                if self.character.inventory[-1].type not in self.slotsByItemtype:
                    self.slotsByItemtype[self.character.inventory[-1].type] = []
                self.slotsByItemtype[self.character.inventory[-1].type].append(
                    (slot, key)
                )
                break

            command = ""
            if slot[1] < 7:
                if slot[1] in (6, 4):
                    command += "w"
                elif slot[1] in (3, 1):
                    command += "4w"
                if slot[0] < 7:
                    command += str(7 - slot[0]) + "a"
                else:
                    command += str(slot[0] - 7) + "d"
                command += "L"
                if slot[1] in (1, 4):
                    command += "w"
                elif slot[1] in (3, 6):
                    command += "s"
                if slot[0] < 7:
                    command += str(7 - slot[0]) + "d"
                else:
                    command += str(slot[0] - 7) + "a"
                if slot[1] in (6, 4):
                    command += "s"
                elif slot[1] in (3, 1):
                    command += "4s"
            else:
                command += "assd"
                if slot[1] in (8, 10):
                    command += "s"
                elif slot[1] in (11, 13):
                    command += "4s"
                if slot[0] < 7:
                    command += str(7 - slot[0]) + "a"
                else:
                    command += str(slot[0] - 7) + "d"
                command += "L"
                if slot[1] in (8, 11):
                    command += "w"
                elif slot[1] in (10, 13):
                    command += "s"
                if slot[0] < 7:
                    command += str(7 - slot[0]) + "d"
                else:
                    command += str(slot[0] - 7) + "a"
                if slot[1] in (8, 10):
                    command += "w"
                elif slot[1] in (11, 13):
                    command += "4w"
                command += "dwwa"

            self.character.runCommandString(command)
            self.character.addMessage("running command to store item %s" % (command))

        if self.submenue.selection == "fetchItem":
            options = []
            for key in self.slotsByItemtype:
                options.append((key, key))
            self.submenue = src.menuFolder.SelectionMenu.SelectionMenu(
                "what do you want to do?", options
            )
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.fetchItem

        if self.submenue.selection == "fetchByJobOrder":
            jobOrder = None
            for item in self.character.inventory:
                if (
                    item.type == "JobOrder"
                    and not item.done
                    and item.tasks[-1]["task"] == "place"
                ):
                    jobOrder = item
                    break

            if not jobOrder:
                self.character.addMessage("no job order found")
                return

            if jobOrder.tasks[-1]["toPlace"] not in self.slotsByItemtype:
                self.character.addMessage("no " + item.type + " in storage")

                jobOrder.tasks.append(
                    {
                        "task": "produce",
                        "toProduce": item.tasks[-1]["toPlace"],
                        "macro": "PRODUCE "
                        + item.tasks[-1]["toPlace"].upper()[:-1]
                        + item.tasks[-1]["toPlace"][-1].lower(),
                        "command": None,
                    }
                )
                return
            self.submenue.selection = item.tasks[-1]["toPlace"]
            self.fetchItem()
            return

    def fetchItem(self):
        """
        handle a character trying to fetch an item
        """

        if self.submenue.selection is None:
            return

        if not self.slotsByItemtype[self.submenue.selection]:
            self.character.addMessage("no item to fetch")
            return

        slotTuple = self.slotsByItemtype[self.submenue.selection].pop()
        slot = slotTuple[0]
        if not self.slotsByItemtype[self.submenue.selection]:
            del self.slotsByItemtype[self.submenue.selection]
        self.freeItemSlots[slotTuple[1]].append(slot)

        if not slot:
            self.character.addMessage("no item to fetch")
            return

        command = ""
        if slot[1] < 7:
            if slot[1] in (6, 4):
                command += "w"
            elif slot[1] in (3, 1):
                command += "4w"
            if slot[0] < 7:
                command += str(7 - slot[0]) + "a"
            else:
                command += str(slot[0] - 7) + "d"
            command += "K"
            if slot[1] in (1, 4):
                command += "w"
            elif slot[1] in (3, 6):
                command += "s"
            if slot[0] < 7:
                command += str(7 - slot[0]) + "d"
            else:
                command += str(slot[0] - 7) + "a"
            if slot[1] in (6, 4):
                command += "s"
            elif slot[1] in (3, 1):
                command += "4s"
        else:
            command += "assd"
            if slot[1] in (8, 10):
                command += "s"
            elif slot[1] in (11, 13):
                command += "4s"
            if slot[0] < 7:
                command += str(7 - slot[0]) + "a"
            else:
                command += str(slot[0] - 7) + "d"
            command += "K"
            if slot[1] in (8, 11):
                command += "w"
            elif slot[1] in (10, 13):
                command += "s"
            if slot[0] < 7:
                command += str(7 - slot[0]) + "d"
            else:
                command += str(slot[0] - 7) + "a"
            if slot[1] in (8, 10):
                command += "w"
            elif slot[1] in (11, 13):
                command += "4w"
            command += "dwwa"

        # abstration: should use character functionality
        self.character.runCommandString(command)
        self.character.addMessage("running command to fetch item %s" % (command))

    def fetchSpecialRegisterInformation(self):
        """
        returns some of the objects state to be stored ingame in a characters registers

        Returns:
            a dictionary containing the information
        """

        result = super().fetchSpecialRegisterInformation()
        for itemType in self.slotsByItemtype:
            result["num " + str(itemType) + " stored"] = len(
                self.slotsByItemtype[itemType]
            )
        numFreeSlots = 0
        for (_key, itemSlot) in self.freeItemSlots.items():
            numFreeSlots += len(itemSlot)
        result["num free slots"] = numFreeSlots
        maxAmount = 0
        if self.xPosition % 15 in (6, 8) and self.yPosition % 15 in (6, 8):
            maxAmount = 23
        if (self.xPosition % 15, self.yPosition % 15) == (7, 7):
            maxAmount = 23 * 4
        result["max amount"] = maxAmount
        return result

src.items.addType(TypedStockpileManager)

import src

class AutoScribe(src.items.Item):
    """
    ingame item to copy sheet based items
    is indeded to allow the player to copy automation
    """

    type = "AutoScribe"

    def __init__(self):
        """
        configure the super class
        """

        self.coolDown = 10
        self.coolDownTimer = -self.coolDown
        self.level = 1

        super().__init__(display=src.canvas.displayChars.sorter)

        self.name = "auto scribe"
        self.description = "A AutoScribe copies commands"
        self.usageInfo = """
The command to copy has to be placed to the west of the machine.
A sheet has to be placed to the north of the machine.
The copy of the command will be outputted to the east.
The original command will be outputted to the south.

The level of the copied command is the minimum level of the input command, sheet and the auto scribe itself.
"""

        self.attributesToStore.extend(["coolDown", "coolDownTimer", "level"])

    def apply(self, character):
        """
        handle a character trying touse this item to copy another item

        Parameters:
            character: the character trying to use this item
        """

        super().apply(character)

        # fetch input command or Note
        itemFound = None

        for item in self.container.getItemByPosition((self.xPosition - 1, self.yPosition,self.zPosition)):
            if item.type in ["Command", "Note", "JobOrder"]:
                itemFound = item
                break

        sheetFound = None
        for item in self.container.getItemByPosition((self.xPosition, self.yPosition -1 ,self.zPosition)):
            if item.type in ["Sheet"]:
                sheetFound = item
                break

        if src.gamestate.gamestate.tick < self.coolDownTimer + self.coolDown:
            character.addMessage(
                "cooldown not reached. Wait %s ticks"
                % (self.coolDown - (src.gamestate.gamestate.tick - self.coolDownTimer),)
            )
            return
        self.coolDownTimer = src.gamestate.gamestate.tick

        # refuse to produce without resources
        if not itemFound:
            character.addMessage("no items available")
            return
        if not sheetFound:
            character.addMessage("no sheet available")
            return

        # remove resources
        self.container.removeItem(sheetFound)
        self.container.removeItem(itemFound)

        # spawn new item
        if itemFound.type == "Command":
            new = src.items.itemMap["Command"]()
            new.command = itemFound.command
        elif itemFound.type == "Note":
            new = src.items.itemMap["Note"]()
            new.text = itemFound.text
        elif itemFound.type == "BluePrint":
            new = src.items.itemMap["BluePrint"]()
            new.setToProduce(itemFound.endProduct)
        elif itemFound.type == "JobOrder":
            new = src.items.itemMap["JobOrder"]()
            new.macro = itemFound.macro
            new.command = itemFound.command
            new.toProduce = itemFound.toProduce
        new.bolted = False

        if itemFound.type == "Command":
            new.name = itemFound.name
            new.description = itemFound.description

        if hasattr(itemFound, "level"):
            newLevel = min(itemFound.level, sheetFound.level, self.level)
            new.level = newLevel

        targetFull = False
        if (self.xPosition + 1, self.yPosition) in self.container.itemByCoordinates:
            if new.walkable:
                if (
                    len(
                        self.container.itemByCoordinates[
                            (self.xPosition + 1, self.yPosition)
                        ]
                    )
                    > 15
                ):
                    targetFull = True
                for item in self.container.itemByCoordinates[
                    (self.xPosition + 1, self.yPosition)
                ]:
                    if item.walkable == False:
                        targetFull = True
            else:
                if (
                    len(
                        self.container.itemByCoordinates[
                            (self.xPosition + 1, self.yPosition)
                        ]
                    )
                    > 1
                ):
                    targetFull = True

        if targetFull:
            character.addMessage(
                "the target area is full, the machine does not produce anything"
            )
            return

        self.container.addItem(new,(self.xPosition+1,self.yPosition,self.zPosition))
        self.container.addItem(itemFound,(self.xPosition,self.yPosition+1,self.zPosition))

    def getLongInfo(self):
        """
        return a longer than normal description text

        Returns:
            the description text
        """

        text = super().getLongInfo()
        text += """
This is a level %s item

""" % (
            self.level
        )
        return text


src.items.addType(AutoScribe)

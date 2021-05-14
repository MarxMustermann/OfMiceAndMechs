import src

"""
"""


class AutoScribe(src.items.Item):
    type = "AutoScribe"

    """
    call superclass constructor with modified parameters
    """

    def __init__(self, name="auto scribe", noId=False):
        self.coolDown = 10
        self.coolDownTimer = -self.coolDown
        self.level = 1

        super().__init__(display=src.canvas.displayChars.sorter, name=name)

        self.attributesToStore.extend(["coolDown", "coolDownTimer", "level"])

    """
    """

    def apply(self, character, resultType=None):
        super().apply(character, silent=True)

        if not self.room:
            character.addMessage("this machine can only be used within rooms")
            return

        # fetch input command or Note
        itemFound = None
        if (self.xPosition - 1, self.yPosition) in self.room.itemByCoordinates:
            for item in self.room.itemByCoordinates[
                (self.xPosition - 1, self.yPosition)
            ]:
                if item.type in ["Command", "Note", "JobOrder"]:
                    itemFound = item
                    break

        sheetFound = None
        if (self.xPosition, self.yPosition - 1) in self.room.itemByCoordinates:
            for item in self.room.itemByCoordinates[
                (self.xPosition, self.yPosition - 1)
            ]:
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
        self.room.removeItem(sheetFound)
        self.room.removeItem(itemFound)

        # spawn new item
        if itemFound.type == "Command":
            new = Command(creator=self)
            new.command = itemFound.command
        elif itemFound.type == "Note":
            new = Note(creator=self)
            new.text = itemFound.text
        elif itemFound.type == "BluePrint":
            new = BluePrint(creator=self)
            new.setToProduce(itemFound.endProduct)
        elif itemFound.type == "JobOrder":
            new = JobOrder(creator=self)
            new.macro = itemFound.macro
            new.command = itemFound.command
            new.toProduce = itemFound.toProduce
        new.xPosition = self.xPosition + 1
        new.yPosition = self.yPosition
        new.bolted = False

        if itemFound.type == "Command":
            new.name = itemFound.name
            new.description = itemFound.description

        if hasattr(itemFound, "level"):
            newLevel = min(itemFound.level, sheetFound.level, self.level)
            new.level = newLevel

        targetFull = False
        if (self.xPosition + 1, self.yPosition) in self.room.itemByCoordinates:
            if new.walkable:
                if (
                    len(
                        self.room.itemByCoordinates[
                            (self.xPosition + 1, self.yPosition)
                        ]
                    )
                    > 15
                ):
                    targetFull = True
                for item in self.room.itemByCoordinates[
                    (self.xPosition + 1, self.yPosition)
                ]:
                    if item.walkable == False:
                        targetFull = True
            else:
                if (
                    len(
                        self.room.itemByCoordinates[
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

        self.room.addItems([new])
        itemFound.xPosition = self.xPosition
        itemFound.yPosition = self.yPosition + 1
        self.room.addItems([itemFound])

    def getLongInfo(self):
        text = """
item: AutoScribe

description:
A AutoScribe copies commands.

The command to copy has to be placed to the west of the machine.
A sheet has to be placed to the north of the machine.
The copy of the command will be outputted to the east.
The original command will be outputted to the south.

The level of the copied command is the minimum level of the input command, sheet and the auto scribe itself.

This is a level %s item

""" % (
            self.level
        )
        return text


src.items.addType(AutoScribe)

import src

"""
"""


class BackTracker(src.items.Item):
    type = "BackTracker"

    """
    call superclass constructor with modified parameters
    """

    def __init__(self):
        super().__init__(display=src.canvas.displayChars.backTracker)

        self.name = "back tracker"

        self.attributesToStore.extend(["command"])

        self.tracking = False
        self.tracked = None
        self.walkable = True
        self.command = []

        self.addListener(self.registerDrop, "dropped")
        self.addListener(self.registerPickUp, "pickUp")

    def apply(self, character):

        if self.tracking:
            self.tracked.delListener(self.registerMovement, "moved")
            character.addMessage("backtracking")
            self.tracking = False

            character.addMessage("runs the stored path")
            character.runCommandString(self.command)

            self.command = []
        else:
            self.tracked = character
            self.tracked.addListener(self.registerMovement, "moved")

            character.addMessage("it starts to track")
            self.tracking = True

    def getLongInfo(self):
        text = """

This device tracks ticks since creation. You can use it to measure time.

Activate it to get a message with the number of ticks passed.

Also the number of ticks will be written to the register t.

"""
        return text

    def registerPickUp(self, param):
        if self.tracked:
            self.tracked.addMessage("pickUp")
            self.tracked.addMessage(param)

    def registerDrop(self, param):
        if self.tracked:
            self.tracked.addMessage("drop")
            self.tracked.addMessage(param)

    def registerMovement(self, param):
        if self.tracked:
            self.tracked.addMessage("mov")
            self.tracked.addMessage(param)

        mov = ""
        if param == "north":
            mov = "s"
        elif param == "south":
            mov = "w"
        elif param == "west":
            mov = "d"
        elif param == "east":
            mov = "a"
        self.command.insert(0, mov)


src.items.addType(BackTracker)

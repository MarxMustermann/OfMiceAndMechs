import src


class RoomControls(src.items.Item):
    """
    ingame item used to drive around rooms
    """

    type = "RoomControls"

    def __init__(self):
        """
        configure super class
        """
        super().__init__(display=src.canvas.displayChars.display)
        self.name = "room controls"
        self.description = "Can be used to control vehicles"
        self.usageInfo = """
Use it to take control over the vehice.

While controlling the vehicle your movement keys will be overriden.
The movement key will move the room instead of yourself.
For example pressing w will not move you to the north, but will move the room to the north.
You need enough steam generation to move

To stop using the room controls press j again.
"""

    def apply(self, character):
        """
        handle a character using this item by mapping the player controls to room movement
        """

        # handle movement keystrokes
        def moveNorth():
            """
            move room to north
            """
            self.container.moveDirection("north", force=self.container.engineStrength)

        def moveSouth():
            """
            move room to south
            """
            self.container.moveDirection("south", force=self.container.engineStrength)

        def moveWest():
            """
            move room to west
            """
            self.container.moveDirection("west", force=self.container.engineStrength)

        def moveEast():
            """
            move room to east
            """
            self.container.moveDirection("east", force=self.container.engineStrength)

        if "stealKey" not in character.macroState:
            character.macroState["stealKey"] = {}

        def disapply():
            """
            reset key mapping
            """

            del character.macroState["stealKey"]["w"]
            del character.macroState["stealKey"]["s"]
            del character.macroState["stealKey"]["a"]
            del character.macroState["stealKey"]["d"]
            del character.macroState["stealKey"]["up"]
            del character.macroState["stealKey"]["down"]
            del character.macroState["stealKey"]["right"]
            del character.macroState["stealKey"]["left"]
            del character.macroState["stealKey"]["j"]

        # map the keystrokes
        character.macroState["stealKey"]["w"] = moveNorth
        character.macroState["stealKey"]["s"] = moveSouth
        character.macroState["stealKey"]["a"] = moveWest
        character.macroState["stealKey"]["d"] = moveEast
        character.macroState["stealKey"]["up"] = moveNorth
        character.macroState["stealKey"]["down"] = moveSouth
        character.macroState["stealKey"]["left"] = moveWest
        character.macroState["stealKey"]["right"] = moveEast
        character.macroState["stealKey"]["j"] = disapply

src.items.addType(RoomControls)

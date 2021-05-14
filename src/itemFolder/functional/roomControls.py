import src

"""
should be a display, but is abused as vehicle control
bad code: use an actual vehicle control
"""


class RoomControls(src.items.Item):
    type = "RoomControls"

    """
    call superclass constructor with modified paramters
    """

    def __init__(self):
        super().__init__(display=src.canvas.displayChars.display)
        self.name = "room controls"

    """
    map player controls to room movement
    """

    def apply(self, character):
        super().apply(character, silent=True)

        if not self.room:
            character.addMessage("this machine can only be used within rooms")
            return

        # handle movement keystrokes
        """
        move room to north
        """

        def moveNorth():
            self.room.moveDirection("north", force=self.room.engineStrength)

        """
        move room to south
        """

        def moveSouth():
            self.room.moveDirection("south", force=self.room.engineStrength)

        """
        move room to west
        """

        def moveWest():
            self.room.moveDirection("west", force=self.room.engineStrength)

        """
        move room to east
        """

        def moveEast():
            self.room.moveDirection("east", force=self.room.engineStrength)

        if "stealKey" not in character.macroState:
            character.macroState["stealKey"] = {}

        """
        reset key mapping
        """

        def disapply():
            del character.macroState["stealKey"][config.commandChars.move_north]
            del character.macroState["stealKey"][config.commandChars.move_south]
            del character.macroState["stealKey"][config.commandChars.move_west]
            del character.macroState["stealKey"][config.commandChars.move_east]
            del character.macroState["stealKey"]["up"]
            del character.macroState["stealKey"]["down"]
            del character.macroState["stealKey"]["right"]
            del character.macroState["stealKey"]["left"]
            del character.macroState["stealKey"][config.commandChars.activate]

        # map the keystrokes
        character.macroState["stealKey"][config.commandChars.move_north] = moveNorth
        character.macroState["stealKey"][config.commandChars.move_south] = moveSouth
        character.macroState["stealKey"][config.commandChars.move_west] = moveWest
        character.macroState["stealKey"][config.commandChars.move_east] = moveEast
        character.macroState["stealKey"]["up"] = moveNorth
        character.macroState["stealKey"]["down"] = moveSouth
        character.macroState["stealKey"]["left"] = moveWest
        character.macroState["stealKey"]["right"] = moveEast
        character.macroState["stealKey"][config.commandChars.activate] = disapply

    def getLongInfo(self):
        text = """
item: RoomControls

description:
Room controls. Can be used to control vehicles.

Use it to take control over the vehice.

While controlling the vehicle your movement keys will be overriden.
The movement key will move the room instead of yourself.
For example pressing w will not move you to the north, but will move the room to the north.
You need enough steam generation to move

To stop using the room controls press j again.

"""
        return text


src.items.addType(RoomControls)

import src

"""
"""


class PositioningDevice(src.items.Item):
    type = "PositioningDevice"

    """
    call superclass constructor with modified parameters
    """

    def __init__(self):
        super().__init__(display=src.canvas.displayChars.positioningDevice)

        self.name = "positioning device"
        self.bolted = False
        self.walkable = True

    def apply(self, character):

        if "x" not in character.registers:
            character.registers["x"] = [0]
        character.registers["x"][-1] = character.xPosition
        if "y" not in character.registers:
            character.registers["y"] = [0]
        character.registers["y"][-1] = character.yPosition

        character.addMessage(
            "your position is %s/%s"
            % (
                character.xPosition,
                character.yPosition,
            )
        )

    def getLongInfo(self):
        text = """

this device allows you to determine your postion. Use it to get your position.

use it to determine your position. Your position will be shown as a message.

Also the position will be written to your registers.
The x-position will be written to the register x.
The y-position will be written to the register y.

"""
        return text


src.items.addType(PositioningDevice)

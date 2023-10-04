import src

"""
steam sprayer used as a prop in the vat
"""


class Spray(src.items.Item):
    type = "Spray"

    """
    call superclass constructor with modified parameters and set some state
    """

    def __init__(self, direction=None):
        # skin according to spray direction
        if direction is None:
            direction = "left"

        self.direction = direction

        super().__init__(display=src.canvas.displayChars.spray_left_inactive)
        self.name = "spray"

    def render(self):
        """
        set appearance depending on energy supply
        """
        if self.direction == "left":
            if self.terrain.tutorialMachineRoom.steamGeneration == 0:
                return src.canvas.displayChars.spray_left_inactive
            elif self.terrain.tutorialMachineRoom.steamGeneration == 1:
                return src.canvas.displayChars.spray_left_stage1
            elif self.terrain.tutorialMachineRoom.steamGeneration == 2:
                return src.canvas.displayChars.spray_left_stage2
            elif self.terrain.tutorialMachineRoom.steamGeneration == 3:
                return src.canvas.displayChars.spray_left_stage3
            return None
        else:
            if self.terrain.tutorialMachineRoom.steamGeneration == 0:
                return src.canvas.displayChars.spray_right_inactive
            elif self.terrain.tutorialMachineRoom.steamGeneration == 1:
                return src.canvas.displayChars.spray_right_stage1
            elif self.terrain.tutorialMachineRoom.steamGeneration == 2:
                return src.canvas.displayChars.spray_right_stage2
            elif self.terrain.tutorialMachineRoom.steamGeneration == 3:
                return src.canvas.displayChars.spray_right_stage3
            return None

    def getLongInfo(self):
        text = """
item: Boiler

description:
a boiler can be heated by a furnace to produce steam. Steam is the basis for energy generation.

"""
        return text


src.items.addType(Spray)

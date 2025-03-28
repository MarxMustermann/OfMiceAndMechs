import src
import random

class ImplantManipulator(src.items.Item):
    """
    """

    type = "ImplantManipulator"

    def __init__(self):
        """
        configure the superclass
        """

        super().__init__(display="IM")
        self.name = "implant manipulator"

        self.walkable = False
        self.bolted = True

    def apply(self,character):
        character.addMessage("you fix your implant and can use the throne safely now")
        src.gamestate.gamestate.stern["fixedImplant"] = True

src.items.addType(ImplantManipulator, nonManufactured=True)

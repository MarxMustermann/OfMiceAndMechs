import random

import src


class AlarmBell(src.items.Item):

    type = "AlarmBell"
    name = "AlarmBell"
    bolted = True
    walkable = False

    def __init__(self):
        """
        set up internal state
        """

        super().__init__(display="SI")

    def apply(self,character=None):
        try:
            self.container.alarm
        except:
            self.container.alarm = False

        if self.container.alarm:
            self.container.alarm = False
            if character:
                character.addMessage("you disable the alarm")
        else:
            self.container.alarm = True
            if character:
                character.addMessage("you enable the alarm")

    def getConfigurationOptions(self, character):
        """
        register the configuration options with superclass

        Parameters:
            character: the character trying to conigure the machine
        """

        options = super().getConfigurationOptions(character)
        if self.bolted:
            options["b"] = ("unbolt", self.unboltAction)
        else:
            options["b"] = ("bolt down", self.boltAction)
        return options

src.items.addType(AlarmBell)

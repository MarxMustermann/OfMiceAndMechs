import src


class Furnace(src.items.Item):
    """
    ingame item used as heat source for generating steam and similar
    """

    type = "Furnace"

    def __init__(self):
        """
        configure super class
        """

        self.activated = False
        self.boilers = []
        super().__init__(display=src.canvas.displayChars.furnace_inactive)
        self.name = "Furnace"
        self.description = "Used to generate heat. Heat is used to produce steam in boilers"
        self.usageInfo = """
You can fire the furnace by activating it with coal in your inventory.

Place the furnace next to a boiler to be able to heat up the boiler with this furnace.
"""

    def apply(self, character):
        """
        handle a character trying to fire the furnace

        Parameters:
            character: the character trying to use this item
        """

        # select fuel
        # bad pattern: the player should be able to select fuel
        # bad pattern: coal should be preferred
        foundItem = None
        for item in character.inventory:
            canBurn = False
            if hasattr(item, "canBurn"):
                canBurn = item.canBurn

            if not canBurn:
                continue
            foundItem = item

        # refuse to fire the furnace without fuel
        if not foundItem:
            # bad code: return would be preferable to if/else
            if character.watched:
                character.addMessage(
                    "you need coal to fire the furnace and you have no coal in your inventory"
                )
        else:
            # refuse to fire burning furnace
            if self.activated:
                # bad code: return would be preferable to if/else
                if character.watched:
                    character.addMessage("already burning")
            # fire the furnace
            else:
                self.activated = True

                # destroy fuel
                character.inventory.remove(foundItem)
                character.changed()

                # add fluff
                if character.watched:
                    character.addMessage("you fire the furnace")

                # get the boilers affected
                self.boilers = []
                for boiler in self.container.itemsOnFloor:
                    if isinstance(boiler, src.items.itemMap["Boiler"]) and (
                        (
                            boiler.xPosition
                            in [
                                self.xPosition,
                                self.xPosition - 1,
                                self.xPosition + 1,
                            ]
                            and boiler.yPosition == self.yPosition
                        )
                        or boiler.yPosition
                        in [self.yPosition - 1, self.yPosition + 1]
                        and boiler.xPosition == self.xPosition
                    ):
                        self.boilers.append(boiler)

                # heat up boilers
                for boiler in self.boilers:
                    boiler.startHeatingUp()

                # make the furnace stop burning after some time
                event = src.events.FurnaceBurnoutEvent(
                    self.container.timeIndex + 30
                )
                event.furnace = self
                self.container.addEvent(event)

                # notify listeners
                self.changed()

    def render(self):
        """
        render the furnace depending on it burning or not

        Returns:
           what the furnace should look like
        """
        if self.activated:
            return src.canvas.displayChars.furnace_active
        else:
            return src.canvas.displayChars.furnace_inactive

src.items.addType(Furnace)

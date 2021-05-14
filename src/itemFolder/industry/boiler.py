import src

"""
produces steam from heat
bad code: sets the rooms steam generation directly without using pipes
"""


class Boiler(src.items.Item):
    type = "Boiler"

    """
    call superclass constructor with modified paramters and set some state
    """

    def __init__(self, name="boiler", creator=None, noId=False):
        super().__init__(display=src.canvas.displayChars.boiler_inactive)
        self.isBoiling = False
        self.isHeated = False
        self.startBoilingEvent = None
        self.stopBoilingEvent = None
        self.name = "boiler"

        # set metadata for saving
        self.attributesToStore.extend(["isBoiling", "isHeated"])

        self.objectsToStore.append("startBoilingEvent")
        self.objectsToStore.append("stopBoilingEvent")

    """
    start producing steam after a delay
    """

    def startHeatingUp(self):

        # do not heat up heated items
        if self.isHeated:
            return

        # flag self as heated
        self.isHeated = True

        # abort cooling down
        if self.stopBoilingEvent:
            self.room.removeEvent(self.stopBoilingEvent)
            self.stopBoilingEvent = None

        # schedule the steam generation
        if not self.startBoilingEvent and not self.isBoiling:
            # schedule the event
            event = src.events.StartBoilingEvent(self.room.timeIndex + 5, creator=self)
            event.boiler = self
            self.room.addEvent(event)

        # notify listeners
        self.changed()

    """
    stop producing steam after a delay
    """

    def stopHeatingUp(self):
        # don't do cooldown on cold boilers
        if not self.isHeated:
            return

        # flag self as heated
        self.isHeated = False

        # abort any heating up
        if self.startBoilingEvent:
            self.room.removeEvent(self.startBoilingEvent)
            self.startBoilingEvent = None
        if not self.stopBoilingEvent and self.isBoiling:

            event = src.events.StopBoilingEvent(self.room.timeIndex + 5, creator=self)
            event.boiler = self
            self.room.addEvent(event)

        # notify listeners
        self.changed()

    def getLongInfo(self):
        text = (
            """
a boiler can be heated by a furnace to produce steam. Steam is the basis for energy generation.

"""
            + self.id
        )
        return text

    """
    set state from dict
    """

    def setState(self, state):
        super().setState(state)

        if self.isBoiling:
            self.display = src.canvas.displayChars.boiler_active


src.items.addType(Boiler)

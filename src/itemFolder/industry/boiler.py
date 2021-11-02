import src


# bad code: sets the rooms steam generation directly without using pipes
class Boiler(src.items.Item):
    """
    produces steam from heat
    is intended to be part of an energy management system
    """

    type = "Boiler"
    attributesToStore = []
    objectsToStore = []

    def __init__(self):
        """
        configure super class
        """

        super().__init__(display=src.canvas.displayChars.boiler_inactive)
        self.isBoiling = False
        self.isHeated = False
        self.startBoilingEvent = None
        self.stopBoilingEvent = None
        self.name = "boiler"

        # set metadata for saving
        if not self.attributesToStore:
            self.attributesToStore.extend(super().attributesToStore)
            self.attributesToStore.extend(["isBoiling", "isHeated"])

        if not self.objectsToStore:
            self.objectsToStore.extend(super().objectsToStore)
            self.objectsToStore.append("startBoilingEvent")
            self.objectsToStore.append("stopBoilingEvent")


    def startHeatingUp(self):
        """
        start producing steam after a delay
        """

        # do not heat up heated items
        if self.isHeated:
            return

        # flag self as heated
        self.isHeated = True

        # abort cooling down
        if self.stopBoilingEvent:
            self.container.removeEvent(self.stopBoilingEvent)
            self.stopBoilingEvent = None

        # schedule the steam generation
        if not self.startBoilingEvent and not self.isBoiling:
            # schedule the event
            event = src.events.StartBoilingEvent(self.container.timeIndex + 5)
            event.boiler = self
            self.container.addEvent(event)

        # notify listeners
        self.changed()


    def stopHeatingUp(self):
        """
        stop producing steam after a delay
        """

        # don't do cooldown on cold boilers
        if not self.isHeated:
            return

        # flag self as heated
        self.isHeated = False

        # abort any heating up
        if self.startBoilingEvent:
            self.container.removeEvent(self.startBoilingEvent)
            self.startBoilingEvent = None
        if not self.stopBoilingEvent and self.isBoiling:

            event = src.events.StopBoilingEvent(self.container.timeIndex + 5)
            event.boiler = self
            self.container.addEvent(event)

        # notify listeners
        self.changed()

    def getLongInfo(self):
        """
        returns a longer than normal desription text

        Returns:
            the description text
        """

        text = super().getLongInfo()
        text += """
a boiler can be heated by a furnace to produce steam. Steam is the basis for energy generation.

"""
        return text

    # bad code: should be replaced with render()
    def setState(self, state):
        """
        set state from semi serilised form
        """

        super().setState(state)

        if self.isBoiling:
            self.display = src.canvas.displayChars.boiler_active


src.items.addType(Boiler)

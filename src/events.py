"""
Events and event related code belong here
bad code: not all events are here yet
"""

# import basic libs
import json
import random
import time


# import basic internal libs
import src.canvas

class Event:
    """
    base class for events
    """

    type = "Event"

    def __init__(self, tick):
        """
        initialises internal state

        Parameters:
            tick: the time the event should trigger
        """

        super().__init__()

        self.tick = tick

    def callIndirect(self, callback, extraParams={}):
        """
        call a callback that is stored in a savable format

        Parameters:
            callback: the callback to call
            extraParams: some additional parameters
        """

        if not isinstance(callback, dict):
            # bad code: direct function calls are deprecated, but not completely removed
            callback()
        else:
            if "container" not in callback:
                return
            container = callback["container"]
            function = getattr(container, callback["method"])

            if "params" in callback:
                callback["params"].update(extraParams)
                function(callback["params"])
            else:
                function()

    def handleEvent(self):
        """
        do nothing
        """
        pass

# bad code: almost identical to RunCallbackEvent
class RunFunctionEvent(Event):
    """
    event that calls a function when triggering

    Parameters:
        tick: the time the event should trigger
    """

    def __init__(self, tick):
        """
        initialises internal state

        Parameters:
            tick: the time the event should trigger
        """

        super().__init__(tick=tick)

    def setFunction(self, function):
        self.function = function

    def handleEvent(self):
        self.function()

class RunCallbackEvent(Event):
    """
    the event for calling a callback
    """

    def __init__(self, tick):
        """
        initialises internal state

        Parameters:
            tick: the time the event should trigger
        """

        super().__init__(tick)
        self.type = "RunCallbackEvent"
        self.callback = None

    def setCallback(self, callback):
        """
        set a callback to call

        Parameters:
            callback: the callback to store
        """

        self.callback = callback

    def handleEvent(self):
        """
        call the callback
        """

        try:
            self.callback
        except:
            return
        if self.callback:
            self.callIndirect(self.callback)
        else:
            pass

# obsolete: only used in old story mode
class ShowMessageEvent(Event):
    """
    event for adding a message
    """

    def __init__(self, tick, message=""):
        """
        initialises internal state

        Parameters:
            tick: the time the event should trigger
            message: the message to show
        """

        super().__init__(tick)
        self.type = "ShowMessageEvent"
        self.message = message

    def handleEvent(self):
        """
        add message
        """

        messages.append(self.message)

# obsolete: only used in old story mode
class ShowCinematicEvent(Event):
    """
    event for showing a cinematic
    """

    def __init__(self, tick, cinematic=None):
        """
        initialises internal state

        Parameters:
            tick: the time the event should trigger
            cinematic: the cinematic to show
        """

        super().__init__(tick)
        self.type = "ShowCinematicEvent"
        self.cinematic = cinematic

    def handleEvent(self):
        """
        start cinematic
        """

        # bad code: a wrapper should be called here
        import src.cinematics
        import src.interaction

        src.cinematics.cinematicQueue.append(self.cinematic)
        src.interaction.loop.set_alarm_in(0.0, src.interaction.callShow_or_exit, "~")

# bad code: doesn't at all do what it promises to do
class EndQuestEvent(Event):
    """
    the event for automatically terminating the quest
    (doesn't actually do that)
    """

    type = "EndQuestEvent"

    def __init__(self, tick, callback=None):
        """
        initialises internal state

        Parameters:
            tick: the time the event should trigger
            callback: a callback to call
        """

        super().__init__(tick)
        self.callback = callback

    def handleEvent(self):
        """
        call callback
        """

        if self.callback:
            self.callIndirect(self.callback)
        else:
            pass

# obsolete: only used in old story mode
# bad code: should be an abstract event calling a method
class FurnaceBurnoutEvent(Event):
    """
    the event for stopping to burn after a while
    """

    def __init__(self, tick):
        """
        initialises internal state

        Parameters:
            tick: the time the event should trigger
        """

        self.furnace = None
        super().__init__(tick)
        self.type = "FurnaceBurnoutEvent"

        self.tick = tick

    def handleEvent(self):
        """
        stop burning
        """

        # stop burning
        self.furnace.activated = False

        # get the boilers affected
        self.furnace.boilers = []
        # for boiler in self.room.boilers:
        for boiler in self.furnace.room.itemsOnFloor:
            if isinstance(boiler, src.items.Boiler):
                if (
                    (
                        boiler.xPosition
                        in [
                            self.furnace.xPosition,
                            self.furnace.xPosition - 1,
                            self.furnace.xPosition + 1,
                        ]
                        and boiler.yPosition == self.furnace.yPosition
                    )
                    or boiler.yPosition
                    in [self.furnace.yPosition - 1, self.furnace.yPosition + 1]
                    and boiler.xPosition == self.furnace.xPosition
                ):
                    self.furnace.boilers.append(boiler)

        # stop heating the boilers
        for boiler in self.furnace.boilers:
            boiler.stopHeatingUp()

        # notify listeners
        self.furnace.changed()

# obsolete: only used in old story mode
# bad code: should be an abstract event calling a method
class StopBoilingEvent(Event):
    """
    the event for stopping to boil
    """

    def __init__(self, tick):
        """
        initialises internal state

        Parameters:
            tick: the time the event should trigger
        """

        self.boiler = None
        super().__init__(tick)
        self.type = "StopBoilingEvent"

        self.tick = tick

    def handleEvent(self):
        """
        start producing steam
        """

        # add noises
        mainChar.addMessage("*unboil*")

        # set own state
        self.boiler.display = src.canvas.displayChars.boiler_inactive
        self.boiler.isBoiling = False
        self.boiler.stopBoilingEvent = None
        self.boiler.changed()

        # change rooms steam production
        self.boiler.room.steamGeneration -= 1
        self.boiler.room.changed()

# obsolete: only used in old story mode
# bad code: should be an abstract event calling a method
class StartBoilingEvent(Event):
    """
    the event for starting to boil
    """

    def __init__(self, tick):
        """
        initialises internal state

        Parameters:
            tick: the time the event should trigger
        """

        self.boiler = None
        super().__init__(tick)

        self.type = "StartBoilingEvent"

        self.tick = tick

    def handleEvent(self):
        """
        start producing steam
        """

        # add noises
        # bad pattern: should only make noise for nearby things
        # set own state
        self.boiler.display = src.canvas.displayChars.boiler_active
        self.boiler.isBoiling = True
        self.boiler.startBoilingEvent = None
        self.boiler.changed()

        # change rooms steam production
        self.boiler.container.steamGeneration += 1
        self.boiler.container.changed()


# supply a mapping from strings to events
# bad pattern: has to be extendable
eventMap = {
    "Event": Event,
    "ShowMessageEvent": ShowMessageEvent,
    "ShowCinematicEvent": ShowCinematicEvent,
    "FurnaceBurnoutEvent": FurnaceBurnoutEvent,
    "EndQuestEvent": EndQuestEvent,
    "StopBoilingEvent": StopBoilingEvent,
    "StartBoilingEvent": StartBoilingEvent,
    "RunCallbackEvent": RunCallbackEvent,
}

"""
Events and event related code belong here
bad code: not all events are here yet
"""

# import basic libs
import json

# import basic internal libs
import src.saveing
import src.canvas

class Event(src.saveing.Saveable):
    """
    base class for events
    """

    def __init__(self, tick):
        """
        initialises internal state

        Parameters:
            tick: the time the event should trigger
        """

        super().__init__()
        self.type = "Event"

        import uuid

        self.id = uuid.uuid4().hex

        # set meta information for saving
        self.attributesToStore.extend(["tick", "type"])

        self.tick = tick

        # self initial state
        self.initialState = self.getState()


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

        # set meta information for saving
        self.callbacksToStore.append("callback")

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

        super().__init__(tick):
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

<<<<<<< HEAD
        super().__init__(tick)
=======
        super().__init__(tick):
>>>>>>> fcbc20953464bd3b5dd52adc8ee750cc983ff285
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

# obsolete: only used in old story mode
# bad code: doesn't at all do what it promises to do
class EndQuestEvent(Event):
    """
    the event for automatically terminating the quest
    (doesn't actually do that)
    """

    def __init__(self, tick, callback=None):
        """
        initialises internal state

        Parameters:
            tick: the time the event should trigger
            callback: a callback to call
        """

        super().__init__(tick, creator=creator)
        self.type = "EndQuestEvent"
        self.callback = callback

        # set meta information for saving
        self.callbacksToStore.append("callback")

    def handleEvent(self):
        """
        call callback
        """

        if self.callback:
            self.callIndirect(self.callback)
        else:
            pass

# obsolete: only used in old story mode
# bad code: should be an abstact event calling a method
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

        # set meta information for saving
        self.objectsToStore.append("furnace")

        # self initial state
        self.initialState = self.getState()


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
        super().__init__(tick):
        self.type = "StopBoilingEvent"

        self.tick = tick

        # set meta information for saving
        self.objectsToStore.append("boiler")

        # self initial state
        self.initialState = self.getState()

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
# bad code: should be an abstact event calling a method
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

        # set meta information for saving
        self.objectsToStore.append("boiler")

        # self initial state
        self.initialState = self.getState()

    def handleEvent(self):
        """
        start producing steam
        """

        # add noises
        # bad pattern: should only make noise for nearby things
        mainChar.addMessage("*boil*")

        # set own state
        self.boiler.display = src.canvas.displayChars.boiler_active
        self.boiler.isBoiling = True
        self.boiler.startBoilingEvent = None
        self.boiler.changed()

        # change rooms steam production
        self.boiler.room.steamGeneration += 1
        self.boiler.room.changed()


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

def getEventFromState(state):
    """
    create an event from a semi serialised state

    Parameters:
        state: the state
    """
    event = eventMap[state["type"]](state["tick"])
    event.setState(state)
    src.saveing.loadingRegistry.register(event)
    return event

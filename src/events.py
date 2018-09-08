#bad code: global state
cinematics = None
messages = None
callShow_or_exit = None
loop = None

'''
base class for events
'''
class Event(object):
    def __init__(self,tick):
        self.id = "Event"
        self.type = "Event"
        self.tick = tick

    def handleEvent(self):
        pass

    def getDiffState(self):
        return self.getState()
       
    def getState(self):
        return {
                 "id":self.id,
                 "tick":self.tick,
                 "type":self.type,
               }

    def setState(self, state):
        if "id" in state:
            self.id = state["id"]
        if "tick" in state:
            self.tick = state["tick"]
        if "type" in state:
            self.type = state["type"]

'''
straigthforward adding a message
'''
class ShowMessageEvent(Event):
    def __init__(self,tick,message):
        super().__init__(tick)
        self.id = "ShowMessageEvent"
        self.type = "ShowMessageEvent"
        self.message = message

    def handleEvent(self):
        messages.append(self.message)

'''
straigthforward showing a cinematic
'''
class ShowCinematicEvent(Event):
    def __init__(self,tick,cinematic):
        super().__init__(tick)
        self.id = "ShowCinematicEvent"
        self.type = "ShowCinematicEvent"
        self.cinematic = cinematic

    def handleEvent(self):
        # bad code: a wrapper should be called here
        cinematics.cinematicQueue.append(self.cinematic)
        loop.set_alarm_in(0.0, callShow_or_exit, '~')


'''
the event for stopping to burn after a while
bad code: should be an abstact event calling a method
'''
class FurnaceBurnoutEvent(Event):
    '''
    straightforward state initialization
    '''
    def __init__(self,tick):
        super().__init__(tick)
        self.id = "FurnaceBurnoutEvent"
        self.type = "FurnaceBurnoutEvent"
        self.furnace = None

        self.tick = tick

    '''
    stop burning
    '''
    def handleEvent(self):
        # stop burning
        self.furnace.activated = False
        self.furnace.display = displayChars.furnace_inactive

        # stop heating the boilers
        for boiler in self.furnace.boilers:
            boiler.stopHeatingUp()

        # notify listeners
        self.furnace.changed()

    def setState(self,state):
        if "furnace" in state:
           if state["furnace"]:
               def setFurnace(furnace):
                   self.furnace = furnace
               loadingRegistry.callWhenAvailable(state["furnace"],setFurnace)
           else:
               self.furnace = None

       
    def getState(self):
        state = super().getState()
        if self.furnace:
            state["furnace"] = self.furnace.id
        else:
            state["furnace"] = None
        return state

eventMap = {
             "Event":Event,
             "ShowMessageEvent":ShowMessageEvent,
             "ShowCinematicEvent":ShowCinematicEvent,
             "FurnaceBurnoutEvent":FurnaceBurnoutEvent,
           }

def getEventFromState(state):
    event = eventMap[state["type"]](state["tick"])
    event.setState(state)
    return event


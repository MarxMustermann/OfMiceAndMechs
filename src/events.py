#########################################################################################################################
###
##      Events and event related code belong here
#       bad code: not all events are here yet
#
#########################################################################################################################

# import basic libs
import json

# import basic internal libs
import src.saveing

#bad code: global state
cinematics = None
messages = None
callShow_or_exit = None
loop = None

'''
base class for events
'''
class Event(src.saveing.Saveable):
    '''
    basic state setting
    '''
    def __init__(self,tick,creator=None):
        super().__init__()
        self.type = "Event"

        # set id
        self.id = {
                    "counter":creator.getCreationCounter(),
                    "type": self.type,
                  }
        self.id["creator"] = creator.id
        self.id = json.dumps(self.id, sort_keys=True).replace("\\","")

        # set meta information for saving
        self.attributesToStore.extend(["tick","type"])

        self.tick = tick

        # self initial state
        self.initialState = self.getState()

    def getDiffState(self):
        state = super().getDiffState()
        state["type"] = self.type
        state["tick"] = self.tick
        return state

    '''
    do nothing
    '''
    def handleEvent(self):
        pass

    def getState(self):
        state = super().getState()
        state["objType"] = self.type
        return state

class RunFunctionEvent(Event):
    def __init__(self,tick,creator=None):
        super().__init__(tick=tick,creator=creator)

    def setFunction(self,function):
        self.function = function

    def handleEvent(self):
        self.function()

'''
the event for automatically terminating the quest
'''
class RunCallbackEvent(Event):
    '''
    straightforward state setting
    '''
    def __init__(self,tick,creator=None):
        super().__init__(tick,creator=creator)
        self.type = "RunCallbackEvent"
        self.callback = None

        # set meta information for saving
        self.callbacksToStore.append("callback")

    def setCallback(self,callback):
        self.callback = callback

    '''
    terminate the quest
    '''
    def handleEvent(self):
        try:
            self.callback
        except:
            return
        if (self.callback):
            self.callIndirect(self.callback)
        else:
            pass

'''
straightforward adding a message
'''
class ShowMessageEvent(Event):
    '''
    basic state setting
    '''
    def __init__(self,tick,message,creator=None):
        super().__init__(tick,creator=creator)
        self.type = "ShowMessageEvent"
        self.message = message

    '''
    add message
    '''
    def handleEvent(self):
        messages.append(self.message)

'''
straigthforward showing a cinematic
'''
class ShowCinematicEvent(Event):
    '''
    basic state setting
    '''
    def __init__(self,tick,cinematic,creator=None):
        super().__init__(tick,creator=creator)
        self.type = "ShowCinematicEvent"
        self.cinematic = cinematic

    '''
    start cinematic
    '''
    def handleEvent(self):
        # bad code: a wrapper should be called here
        cinematics.cinematicQueue.append(self.cinematic)
        loop.set_alarm_in(0.0, callShow_or_exit, '~')


'''
the event for automatically terminating the quest
'''
class EndQuestEvent(Event):
    '''
    straightforward state setting
    '''
    def __init__(self,tick,callback=None,creator=None):
        super().__init__(tick,creator=creator)
        self.type = "EndQuestEvent"
        self.callback = callback

        # set meta information for saving
        self.callbacksToStore.append("callback")

    '''
    terminate the quest
    '''
    def handleEvent(self):
        if (self.callback):
            self.callIndirect(self.callback)
        else:
            pass


'''
the event for stopping to burn after a while
bad code: should be an abstact event calling a method
'''
class FurnaceBurnoutEvent(Event):
    '''
    straightforward state initialization
    '''
    def __init__(self,tick,creator=None):
        self.furnace = None
        super().__init__(tick,creator=creator)
        self.type = "FurnaceBurnoutEvent"

        self.tick = tick

        # set meta information for saving
        self.objectsToStore.append("furnace")

        # self initial state
        self.initialState = self.getState()

    '''
    stop burning
    '''
    def handleEvent(self):
        # stop burning
        self.furnace.activated = False

        # get the boilers affected
        self.furnace.boilers = [] 
        #for boiler in self.room.boilers:
        for boiler in self.furnace.room.itemsOnFloor:
            if isinstance(boiler, src.items.Boiler):
                if ((boiler.xPosition in [self.furnace.xPosition,self.furnace.xPosition-1,self.furnace.xPosition+1] and boiler.yPosition == self.furnace.yPosition) or boiler.yPosition in [self.furnace.yPosition-1,self.furnace.yPosition+1] and boiler.xPosition == self.furnace.xPosition):
                    self.furnace.boilers.append(boiler)

        # stop heating the boilers
        for boiler in self.furnace.boilers:
            boiler.stopHeatingUp()

        # notify listeners
        self.furnace.changed()

    def setState(self,state):
        super().setState(state)

'''
the event for stopping to boil
bad code: should be an abstract event calling a method
'''
class StopBoilingEvent(Event):

    '''
    straightforward state initialization
    '''
    def __init__(self,tick,creator=None):
        self.boiler = None
        super().__init__(tick,creator=creator)
        self.type = "StopBoilingEvent"

        self.tick = tick

        # set meta information for saving
        self.objectsToStore.append("boiler")

        # self initial state
        self.initialState = self.getState()

    '''
    start producing steam
    '''
    def handleEvent(self):
        # add noises
        messages.append("*unboil*")

        # set own state
        self.boiler.display = displayChars.boiler_inactive
        self.boiler.isBoiling = False
        self.boiler.stopBoilingEvent = None
        self.boiler.changed()

        # change rooms steam production
        self.boiler.room.steamGeneration -= 1
        self.boiler.room.changed()

'''
the event for starting to boil
bad code: should be an abstact event calling a method
'''
class StartBoilingEvent(Event):
    '''
    straightforward state initialization
    '''
    def __init__(self,tick,creator=None):
        self.boiler = None
        super().__init__(tick,creator=creator)

        self.type = "StartBoilingEvent"

        self.tick = tick

        # set meta information for saving
        self.objectsToStore.append("boiler")

        # self initial state
        self.initialState = self.getState()

    '''
    start producing steam
    '''
    def handleEvent(self):
        # add noises
        # bad pattern: should only make noise for nearby things
        messages.append("*boil*")

        # set own state
        self.boiler.display = displayChars.boiler_active
        self.boiler.isBoiling = True
        self.boiler.startBoilingEvent = None
        self.boiler.changed()

        # change rooms steam production
        self.boiler.room.steamGeneration += 1
        self.boiler.room.changed()

# supply a mapping from strings to events
# bad pattern: has to be extendable
eventMap = {
             "Event":Event,
             "ShowMessageEvent":ShowMessageEvent,
             "ShowCinematicEvent":ShowCinematicEvent,
             "FurnaceBurnoutEvent":FurnaceBurnoutEvent,
             "EndQuestEvent":EndQuestEvent,
             "StopBoilingEvent":StopBoilingEvent,
             "StartBoilingEvent":StartBoilingEvent,
             "RunCallbackEvent":RunCallbackEvent,
           }

'''
create an event from a state dict
'''
def getEventFromState(state):
    event = eventMap[state["type"]](state["tick"],creator=void)
    event.setState(state)
    loadingRegistry.register(event)
    return event


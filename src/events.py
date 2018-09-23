#########################################################################################################################
###
##      Events and event related code belong here
#       bad code: not all events are here yet
#
#########################################################################################################################

# import basic libs
import json

# import basic internal libs
# bad code: should not use shorthand
import src.saveing as saveing

#bad code: global state
cinematics = None
messages = None
callShow_or_exit = None
loop = None

'''
base class for events
'''
class Event(saveing.Saveable):
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

        self.tick = tick

        # self initial state
        self.initialState = self.getState()

    '''
    do nothing
    '''
    def handleEvent(self):
        pass

    '''
    get state difference since creation
    bad code: returns state without creating a diff
    '''
    def getDiffState(self):
        return self.getState()
       
    '''
    get state as dict
    '''
    def getState(self):
        return {
                 "id":self.id,
                 "tick":self.tick,
                 "type":self.type,
               }

    '''
    set state from dict
    '''
    def setState(self, state):
        # set attribute
        # bad code: repetetive code
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
    '''
    basic state setting
    '''
    def __init__(self,tick,message,creator=None):
        super().__init__(tick,creator=creator)
        self.id = "ShowMessageEvent"
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
        self.id = "ShowCinematicEvent"
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
        self.id = "FurnaceBurnoutEvent"
        self.type = "FurnaceBurnoutEvent"

        self.tick = tick

    '''
    stop burning
    '''
    def handleEvent(self):
        # stop burning
        self.furnace.activated = False

        # stop heating the boilers
        for boiler in self.furnace.boilers:
            boiler.stopHeatingUp()

        # notify listeners
        self.furnace.changed()

    '''
    set state from dict
    '''
    def setState(self,state):
        # load target furnace
        if "furnace" in state:
           if state["furnace"]:
               '''
               set value
               '''
               def setFurnace(furnace):
                   self.furnace = furnace
               loadingRegistry.callWhenAvailable(state["furnace"],setFurnace)
           else:
               self.furnace = None

    '''
    get state as dict
    '''
    def getState(self):
        # store target furnace
        state = super().getState()
        if self.furnace:
            state["furnace"] = self.furnace.id
        else:
            state["furnace"] = None
        return state

'''
the event for automatically terminating the quest
'''
class EndQuestEvent(Event):
    '''
    straightforward state setting
    '''
    def __init__(subself,tick,callback=None,creator=None):
        super().__init__(tick,creator=creator)
        subself.type = "EndQuestEvent"
        subself.callback = callback

        subself.callbacksToStore.append("callback")

    '''
    terminate the quest
    '''
    def handleEvent(subself):
        if (subself.callback):
            subself.callIndirect(subself.callback)
        else:
            pass

# supply a mapping from strings to events
# bad pattern: has to be extendable
eventMap = {
             "Event":Event,
             "ShowMessageEvent":ShowMessageEvent,
             "ShowCinematicEvent":ShowCinematicEvent,
             "FurnaceBurnoutEvent":FurnaceBurnoutEvent,
             "EndQuestEvent":EndQuestEvent,
           }

'''
create an event from a dict
'''
def getEventFromState(state):
    event = eventMap[state["type"]](state["tick"],creator=void)
    event.setState(state)
    return event


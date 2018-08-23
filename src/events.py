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
        self.tick = tick

    def handleEvent(self):
        pass

'''
straigthforward adding a message
'''
class ShowMessageEvent(Event):
    def __init__(self,tick,message):
        super().__init__(tick)
        self.message = message

    def handleEvent(self):
        messages.append(self.message)

'''
straigthforward showing a cinematic
'''
class ShowCinematicEvent(Event):
    def __init__(self,tick,cinematic):
        super().__init__(tick)
        self.cinematic = cinematic

    def handleEvent(self):
		# bad code: a wrapper should be called here
        cinematics.cinematicQueue.append(self.cinematic)
        loop.set_alarm_in(0.0, callShow_or_exit, '~')


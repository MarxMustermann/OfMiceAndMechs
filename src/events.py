cinematics = None

class Event(object):
    def __init__(self,tick):
        self.tick = tick

    def handleEvent(subself):
        pass

class ShowCinematicEvent(Event):
    def __init__(self,tick,cinematic):
        super().__init__(tick)
        self.cinematic = cinematic

    def handleEvent(self):
        cinematics.cinematicQueue.append(self.cinematic)


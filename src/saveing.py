class Saveable(object):
    creationCounter = 0

    '''
    get the difference of a list between existing and initial state
    '''
    def getDiffList(self,current,orig,exclude=[]):
        # the to be result
        states = {}
        newThingsList = []
        changedThingsList = []
        removedThingsList = []

        # helper state
        currentThingsList = []

        # handle things that exist right now
        for thing in current:
            # skip excludes
            if thing.id in exclude:
                continue

            # register thing as existing
            currentState = thing.getState()
            currentThingsList.append(thing.id)

            if thing.id in orig:
                # handle changed things
                if not currentState == thing.initialState:
                    diffState = thing.getDiffState()
                    if diffState: # bad code: this should not be neccessary
                        changedThingsList.append(thing.id)
                        states[thing.id] = diffState
            else:
                # handle new things
                newThingsList.append(thing.id)
                states[thing.id] = thing.getState()

        # handle removed things
        for thingId in orig:
            if thingId in exclude:
                continue
            if not thingId in currentThingsList:
                removedThingsList.append(thingId)

        return (states,changedThingsList,newThingsList,removedThingsList)

'''
the creator that should be used if there is no valid creator object
basically supply ids for unique ids
'''
class Void(Saveable):
    id = "void**#"

    '''
    supply a counter to allow unique id creation
    '''
    def getCreationCounter(self):
        self.creationCounter += 1
        return self.creationCounter


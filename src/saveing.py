'''
a registry to allow resoving references during loading
'''
class LoadingRegistry(object):
    registered = {}
    delayedCalls = {}

    '''
    register a new id and call backlog
    '''
    def register(self,thing):
        self.registered[thing.id] = thing
        if thing.id in self.delayedCalls:
            for callback in self.delayedCalls[thing.id]:
                callback(thing)

    '''
    trigger a call or register as backlog
    '''
    def callWhenAvailable(self,thingId,callback):
        if thingId in self.registered:
            callback(self.registered[thingId])
        else:
            if not thingId in self.delayedCalls:
                self.delayedCalls[thingId] = []
            self.delayedCalls[thingId].append(callback)

class Saveable(object):
    creationCounter = 0
    attributesToStore = ["id","creationCounter"]

    '''
    get state as dict
    '''
    def getState(self):
        state = {}
        for attribute in self.attributesToStore:
            state[attribute] = getattr(self,attribute)
        return state

    '''
    load list of instances from list
    '''
    def loadFromList(self,info,target,creationFunction):
        if "changed" in info:
            for item in target:
                if item.id in info["states"]:
                    item.setState(info["states"][item.id])
        if "removed" in info:
            for item in target:
                if item.id in info["removed"]:
                    target.remove(item)
        if "new" in info:
            for itemId in info["new"]:
                itemState = info["states"][itemId]
                item = creationFunction(itemState)
                item.setState(itemState)
                target.append(item)
            
    '''
    get difference in state since creation
    '''
    def getDiffState(self):
        result = {}
        for attribute in self.attributesToStore:
            currentValue = getattr(self,attribute)
            if not currentValue == self.initialState[attribute]:
                result[attribute] = currentValue
        return result

    '''
    set state as dict
    '''
    def setState(self,state):
        for attribute in self.attributesToStore:
            if attribute in state:
                setattr(self,attribute,state[attribute])

    '''
    get a list of ids an a dict of their states from a list of objects
    '''
    def storeStateList(self,sourceList,exclude=[]):
        ids = []
        states = {}

        for thing in sourceList:
            if thing.id in exclude:
                continue
            ids.append(thing.id)
            states[thing.id] = thing.getDiffState()

        return (states,ids)

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
    get a new creation counter
    '''
    def getCreationCounter(self):
        self.creationCounter += 1
        return self.creationCounter

'''
the creator that should be used if there is no valid creator object
basically supply ids for unique ids
'''
class Void(Saveable):
    id = "void"


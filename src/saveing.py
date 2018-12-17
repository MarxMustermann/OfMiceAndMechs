
'''
a registry to allow resolving references during loading
'''
class LoadingRegistry(object):
    registered = {}
    delayedCalls = {}
    params = {}

    '''
    register a new id and call callback accumulated for this thing
    '''
    def register(self,thing):
        self.registered[thing.id] = thing

        if not thing.id in self.delayedCalls:
            return

        length = len(self.delayedCalls[thing.id])
        counter = 0
        while counter < length:
            callback = self.delayedCalls[thing.id][counter]
            param = self.params[thing.id][counter]

            if param:
                callback(thing,param)
            else:
                callback(thing)
            counter += 1

    '''
    trigger a call or register as backlog
    '''
    def callWhenAvailable(self,thingId,callback,param=None):
        if thingId in self.registered:
            if param:
                callback(self.registered[thingId],param)
            else:
                callback(self.registered[thingId])
        else:
            if not thingId in self.delayedCalls:
                self.delayedCalls[thingId] = []
            if not thingId in self.params:
                self.params[thingId] = []
            self.delayedCalls[thingId].append(callback)
            self.params[thingId].append(param)

    '''
    getter that ensures only one object for an id is used
    '''
    def fetchThroughRegistry(self,thing):
        if thing.id in self.registered:
            return self.registered[thing.id]
        else:
            return thing

# instanziate the registry
loadingRegistry = LoadingRegistry()

'''
abstract class for saving something. It is intended to keep most saving related stuff away from the game code
'''
class Saveable(object):
    creationCounter = 0

    '''
    basic state setting
    '''
    def __init__(self):
        super().__init__()
        self.attributesToStore = ["id","creationCounter"]
        self.callbacksToStore = []
        self.objectsToStore = []

    '''
    exposes a fetcher from th loading registry
    bad code: this doesn't belong here
    '''
    def fetchThroughRegistry(self,thing):
        return loadingRegistry.fetchThroughRegistry(thing)

    '''
    helper function to serialize callbacks
    '''
    def serializeCallback(self,callback):
        if callback:
            if isinstance(callback,dict):
                # serialize and store callback
                serializedCallback = {}
                serializedCallback["container"] = callback["container"].id
                serializedCallback["method"] = callback["method"]
            else:
                # save callback info in unusable format
                # bad code: cannot be loaded, intended for debugging
                serializedCallback = str(callback)
        else:
            # save None as callback
            serializedCallback = None

        return serializedCallback

    '''
    helper function to deserialize callbacks
    '''
    def deserializeCallback(self,state,callback=None):
        if not callback:
            callback = {}

        # update callback attributes
        if "method" in state:
            callback["method"] = state["method"]
        if "container" in state:
            '''
            set value
            '''
            def setContainer(thing):
                callback["container"] = thing
            loadingRegistry.callWhenAvailable(state["container"],setContainer)
        return callback

    '''
    get state as dict
    '''
    def getState(self):
        state = {}

        # store attributes
        for attribute in self.attributesToStore:
            if hasattr(self,attribute):
                state[attribute] = getattr(self,attribute)
            else:
                state[attribute] = None

        # store callbacks
        for callbackName in self.callbacksToStore:
            # get raw callback
            if hasattr(self,attribute):
                callback = getattr(self,callbackName)
            else:
                callback = None

            # store serialized callback
            state[callbackName] = self.serializeCallback(callback)

        # store objects
        for objectName in self.objectsToStore:
            if hasattr(self,objectName) and getattr(self,objectName):
                state[objectName] = getattr(self,objectName).id
            else:
                state[objectName] = None

        return state

    '''
    load list of instances from list
    '''
    def loadFromList(self,info,target,creationFunction):
        # update changed things
        if "changed" in info:
            for item in target:
                if item.id in info["states"]:
                    item.setState(info["states"][item.id])

        # remove removed things
        if "removed" in info:
            for item in target:
                if item.id in info["removed"]:
                    target.remove(item)

        # create missing things
        if "new" in info:
            for itemId in info["new"]:
                itemState = info["states"][itemId]
                item = creationFunction(itemState)
                item.setState(itemState)
                target.append(item)
            
    '''
    get difference in state since creation
    bad code: callbacks are not handled
    '''
    def getDiffState(self):
        result = {}

        # diff attributes
        for attribute in self.attributesToStore:
            if hasattr(self,attribute):
                currentValue = getattr(self,attribute)
            else:
                currentValue = None

            if not currentValue == self.initialState[attribute]:
                result[attribute] = currentValue

        # diff objects
        for objectName in self.objectsToStore:
            value = None
            if hasattr(self,objectName) and getattr(self,objectName):
                value = getattr(self,objectName).id
            if not value == self.initialState[objectName]:
                result[objectName] = value
               
        return result

    '''
    set state as dict
    '''
    def setState(self,state):
        # set attributes
        for attribute in self.attributesToStore:
            if attribute in state:
                setattr(self,attribute,state[attribute])

        # set callbacks
        for callbackName in self.callbacksToStore:
            if callbackName in state:
                if state[callbackName]:
                    # get basic callback dict
                    callback = getattr(self,callbackName)
                    callback = self.deserializeCallback(state[callbackName],callback)

                    # set callback
                    setattr(self,callbackName,callback)
                else:
                    # set callback to None
                    setattr(self,callbackName,None)

        # set objects
        for objectName in self.objectsToStore:
            if objectName in state:
                if state[objectName]:
                    '''
                    set value
                    '''
                    def setValue(value,name):
                        setattr(self,name,value)
                    loadingRegistry.callWhenAvailable(state[objectName],setValue,(objectName))
                else:
                    setattr(self,objectName,None)

    '''
    get a list of ids and a dict of their states from a list of objects
    '''
    def storeStateList(self,sourceList,exclude=[]):
        ids = []
        states = {}

        # fill result
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
    call a callback in savable format
    '''
    def callIndirect(self,callback):
        if not isinstance(callback,dict):
            # bad code: direct function calls are deprecated, but not completely removed
            callback()
        else:
            container = callback["container"]
            function = getattr(container,callback["method"])
            function()

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


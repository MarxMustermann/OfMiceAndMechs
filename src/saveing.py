"""
a registry to allow resolving references during loading
"""


class LoadingRegistry(object):
    registered = {}
    delayedCalls = {}
    params = {}

    """
    register a new id and call callback accumulated for this thing
    """

    def register(self, thing):
        self.registered[thing.id] = thing

        if not thing.id in self.delayedCalls:
            return

        length = len(self.delayedCalls[thing.id])
        counter = 0
        while counter < length:
            callback = self.delayedCalls[thing.id][counter]
            param = self.params[thing.id][counter]

            if param:
                callback(thing, param)
            else:
                callback(thing)
            counter += 1
        del self.delayedCalls[thing.id]

    """
    trigger a call or register as backlog
    """

    def callWhenAvailable(self, thingId, callback, param=None):
        if thingId in self.registered:
            if param:
                callback(self.registered[thingId], param)
            else:
                callback(self.registered[thingId])
        else:
            if not thingId in self.delayedCalls:
                self.delayedCalls[thingId] = []
            if not thingId in self.params:
                self.params[thingId] = []
            self.delayedCalls[thingId].append(callback)
            self.params[thingId].append(param)

    """
    getter that ensures only one object for an id is used
    """

    def fetchThroughRegistry(self, thing):
        if thing.id in self.registered:
            return self.registered[thing.id]
        else:
            return thing


# instantiate the registry
loadingRegistry = LoadingRegistry()

"""
abstract class for saving something. It is intended to keep most saving related stuff away from the game code
"""


class Saveable(object):
    creationCounter = 0

    """
    basic state setting
    """

    def __init__(self):
        super().__init__()
        self.attributesToStore = ["id", "creationCounter"]
        self.callbacksToStore = []
        self.objectsToStore = []
        self.tupleDictsToStore = []
        self.tupleListsToStore = []

    """
    exposes a fetcher from th loading registry
    bad code: this doesn't belong here
    """

    def fetchThroughRegistry(self, thing):
        return loadingRegistry.fetchThroughRegistry(thing)

    """
    helper function to serialize callbacks
    """

    def serializeCallback(self, callback):
        if callback:
            if isinstance(callback, dict):
                # serialize and store callback
                serializedCallback = {}
                if not "container" in callback:
                    return
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

    """
    helper function to deserialize callbacks
    """

    def deserializeCallback(self, state, callback=None):
        if not callback:
            callback = {}

        # update callback attributes
        if "method" in state:
            callback["method"] = state["method"]
        if "container" in state:
            """
            set value
            """

            def setContainer(thing):
                callback["container"] = thing

            loadingRegistry.callWhenAvailable(state["container"], setContainer)
        return callback

    """
    get state as dict
    """

    def getState(self):
        state = {}

        # store tuple dicts
        for tupleDictName in self.tupleDictsToStore:
            if hasattr(self, tupleDictName):
                tupleDict = getattr(self, tupleDictName)
                convertedDict = []
                for (key, value) in tupleDict.items():
                    convertedDict.append([list(key), value])

                state[tupleDictName] = convertedDict

        # store tuple dicts
        for tupleListName in self.tupleListsToStore:
            if hasattr(self, tupleListName):
                tupleList = getattr(self, tupleListName)
                convertedList = []
                for item in tupleList:
                    convertedList.append(list(item))

                state[tupleListName] = convertedList

        # store attributes
        for attribute in self.attributesToStore:
            if hasattr(self, attribute):
                state[attribute] = getattr(self, attribute)
            else:
                state[attribute] = None

        # store callbacks
        for callbackName in self.callbacksToStore:
            # get raw callback
            if hasattr(self, attribute):
                callback = getattr(self, callbackName)
            else:
                callback = None

            # store serialized callback
            state[callbackName] = self.serializeCallback(callback)

        # store objects
        for objectName in self.objectsToStore:
            if hasattr(self, objectName) and getattr(self, objectName):
                state[objectName] = getattr(self, objectName).id
            else:
                state[objectName] = None

        return state

    """
    load list of instances from list
    """

    def loadFromList(self, info, target, creationFunction):
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

    """
    set state as dict
    """

    def setState(self, state):
        # set tuple dicts
        for tupleDictName in self.tupleDictsToStore:
            if tupleDictName in state:
                convertedDict = {}

                for pair in state[tupleDictName]:
                    convertedDict[tuple(pair[0])] = pair[1]

                setattr(self, tupleDictName, convertedDict)

        for tupleListName in self.tupleListsToStore:
            if tupleListName in state:
                convertedList = []
                for item in state[tupleListName]:
                    convertedList.append(tuple(item))

                setattr(self, tupleListName, convertedList)

        # set attributes
        for attribute in self.attributesToStore:
            if attribute in state:
                setattr(self, attribute, state[attribute])

        # set callbacks
        for callbackName in self.callbacksToStore:
            if callbackName in state:
                if state[callbackName]:
                    # get basic callback dict
                    callback = getattr(self, callbackName)
                    callback = self.deserializeCallback(state[callbackName], callback)

                    # set callback
                    setattr(self, callbackName, callback)
                else:
                    # set callback to None
                    setattr(self, callbackName, None)

        # set objects
        for objectName in self.objectsToStore:
            if objectName in state:
                if state[objectName]:
                    """
                    set value
                    """

                    def setValue(value, name):
                        setattr(self, name, value)

                    loadingRegistry.callWhenAvailable(
                        state[objectName], setValue, (objectName)
                    )
                else:
                    setattr(self, objectName, None)

    """
    call a callback in savable format
    """

    def callIndirect(self, callback):
        if not isinstance(callback, dict):
            # bad code: direct function calls are deprecated, but not completely removed
            callback()
        else:
            if not "container" in callback:
                return
            container = callback["container"]
            function = getattr(container, callback["method"])
            if "params" in callback:
                function(callback["params"])
            else:
                function()

    """
    get a new creation counter
    """

    def getCreationCounter(self):
        self.creationCounter += 1
        return self.creationCounter

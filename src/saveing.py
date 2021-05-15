
class LoadingRegistry(object):
    """
    a registry to allow resolving references during loading
    """

    registered = {}
    delayedCalls = {}
    params = {}

    def register(self, thing):
        """
        register a new id and call callbacks accumulated for this thing

        Parameters:
            thing: the thing to register
        """

        self.registered[thing.id] = thing

        if thing.id not in self.delayedCalls:
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

    def callWhenAvailable(self, thingId, callback, param=None):
        """
        call a callback when a thing is available
        if the thing is not available yet call it later

        Parameters:
            thingId: the id of the thing that should be available
            callback: the callback to call
            param: additional data passed to the callback
        """

        if thingId in self.registered:
            if param:
                callback(self.registered[thingId], param)
            else:
                callback(self.registered[thingId])
        else:
            if thingId not in self.delayedCalls:
                self.delayedCalls[thingId] = []
            if thingId not in self.params:
                self.params[thingId] = []
            self.delayedCalls[thingId].append(callback)
            self.params[thingId].append(param)

# instantiate the registry
loadingRegistry = LoadingRegistry()

class Saveable(object):
    """
    abstract class for something that can be saved. 
    It is intended to keep most saving related stuff away from the game code.
    special saving can be done by overwriting getState/setState
    attributes that should be saved need to be registered as such
    """

    creationCounter = 0

    def __init__(self):
        """
        basic state setting
        """

        super().__init__()
        self.attributesToStore = ["id", "creationCounter"]
        self.callbacksToStore = []
        self.objectsToStore = []
        self.tupleDictsToStore = []
        self.tupleListsToStore = []


    def serializeCallback(self, callback):
        """
        helper function to serialize callbacks

        Parameters:
            callback: the callback to serialize
        Returns:
            the serialized callback
        """

        if callback:
            if isinstance(callback, dict):
                # serialize and store callback
                serializedCallback = {}
                if "container" not in callback:
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

    def deserializeCallback(self, state, callback=None):
        """
        helper function to deserialize callbacks

        Parameters:
            state: the state of the serialized callback
            callback: a existing callback to integrate into
        Returns:
            the deserialized callback
        """

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

    def getState(self):
        """
        prepares writing the gamestate to disc by breaking down objects to simple data structures

        Returns:
            the objects state expressed as a dicts, lists and other simple data
        """

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

    def setState(self, state):
        """
        set the objects state by loading a quasi serialized state

        Parameters:
            state: the state to load
        """

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
                        state[objectName], setValue, objectName
                    )
                else:
                    setattr(self, objectName, None)

    def callIndirect(self, callback, extraParams={}):
        """
        call a callback that is stored in a savable format

        Parameters:
            callback: the callback to call
            extraParams: some additional parameters
        """

        if not isinstance(callback, dict):
            # bad code: direct function calls are deprecated, but not completely removed
            callback()
        else:
            if "container" not in callback:
                return
            container = callback["container"]
            function = getattr(container, callback["method"])

            if "params" in callback:
                callback["params"].update(extraParams)
                function(callback["params"])
            else:
                function()

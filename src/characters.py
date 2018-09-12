import src.items as items
import src.saveing as saving
import src.quests
import json

# bad code: containers for global state
characters = None
calculatePath = None
roomsOnMap = None

"""
this is the class for characters meaning both npc and pcs. 
all characters except the pcs always have automated = True to
make them to things on their own
"""
class Character(saving.Saveable):
    '''
    sets basic info AND adds default behaviour/items
    bad code: adding the default behaviour/items here makes it harder to create instances with fixed state
    '''
    def __init__(self,display="＠",xPosition=0,yPosition=0,quests=[],automated=True,name="Person",creator=None):
        super().__init__()

        # set basic state
        self.display = display # bad code: the character should have a rendering+chaching caching method instead of attrbute
        self.automated = automated
        self.quests = []
        self.name = name
        self.inventory = []
        self.watched = False
        self.listeners = {"default":[]}
        self.path = []
        self.subordinates = []
        self.reputation = 0
        self.events = []
        self.room = None
        self.terrain = None
        self.xPosition = xPosition
        self.yPosition = yPosition
        self.satiation = 1000
        self.dead = False
        self.deathReason = None
        self.questsToDelegate = []
        self.unconcious = False
        self.displayOriginal = display
        self.id = {
                   "other":"character",
                   "xPosition":xPosition,
                   "yPosition":yPosition,
                   "counter":creator.getCreationCounter()
                  }
        self.id["creator"] = creator.id
        self.id = json.dumps(self.id, sort_keys=True).replace("\\","")

        self.attributesToStore.extend([
               "gotBasicSchooling","gotMovementSchooling","gotInteractionSchooling","gotExamineSchooling",
               "xPosition","yPosition","name","satiation","unconcious","reputation","tutorialStart"])

        # bad code: story specific state
        self.serveQuest = None
        self.tutorialStart = 0
        self.gotBasicSchooling = False
        self.gotMovementSchooling = False
        self.gotInteractionSchooling = False
        self.gotExamineSchooling = False

        #TODO: this approach is fail, but works for now. There has to be a better way
        self.basicChatOptions = []

        # default items
        self.assignQuest(src.quests.SurviveQuest(creator=self))
        for quest in quests:
            self.assignQuest(quest)
        self.inventory.append(items.GooFlask(creator=self))

        # save state and register
        self.initialState = self.getState()
        loadingRegistry.register(self)

    '''
    almost straightforward adding of events to the characters event queue
    ensures that the events are added in proper order
    '''
    def addEvent(self,event):
        index = 0
        for existingEvent in self.events:
            if event.tick < existingEvent.tick:
                break
            index += 1
        self.events.insert(index,event)

    def recalculatePath(self):
        self.setPathToQuest(self.quests[0])

    '''
    straightforward removeing of events from the characters event queue
    '''
    def removeEvent(self,event):
        self.events.remove(event)

    '''
    almost straightforward getter for chat options
    # bad code: adds default chat options
    '''
    def getChatOptions(self,partner):
        chatOptions = self.basicChatOptions[:]
        if not self in partner.subordinates:
            chatOptions.append(interaction.RecruitChat)
            pass
        return chatOptions

    '''
    get the changes in state since creation
    '''
    def getDiffState(self):
        # the to be result
        result = super().getDiffState()

        if not self.path == self.initialState["path"]:
            result["path"] = self.path

        # bad code: repetetive handling of non-or-id serialization
        serveQuest = None
        if self.serveQuest:
            serveQuest = self.serveQuest.id
        if not serveQuest == self.initialState["serveQuest"]:
            result["serveQuest"] = serveQuest

        # save inventory
        (itemStates,changedItems,newItems,removedItems) = self.getDiffList(self.inventory,self.initialState["inventory"]["inventoryIds"])
        inventory = {}
        if changedItems:
            inventory["changed"] = changedItems
        if newItems:
            inventory["new"] = newItems
        if removedItems:
            inventory["removed"] = removedItems
        if itemStates:
            inventory["states"] = itemStates
        if itemStates or removedItems:
            result["inventory"] = inventory

        # save quests
        (questStates,changedQuests,newQuests,removedQuests) = self.getDiffList(self.quests,self.initialState["quests"]["questIds"])
        quests = {}
        if changedQuests:
            quests["changed"] = changedQuests
        if newQuests:
            quests["new"] = newQuests
        if removedQuests:
            quests["removed"] = removedQuests
        if questStates:
            quests["states"] = questStates
        if questStates or removedQuests:
            result["quests"] = quests

        # store events diff
        (eventStates,changedEvents,newEvents,removedEvents) = self.getDiffList(self.events,self.initialState["eventIds"])
        if changedEvents:
            result["changedEvents"] = changedEvents
        if newEvents:
            result["newEvents"] = newEvents
        if removedEvents:
            result["removedEvents"] = removedEvents
        if eventStates:
            result["eventStates"] = eventStates

        # save chat options
        # bad code: storing the Chat options as class instead of object complicates things
        chatOptions = []
        for chat in self.basicChatOptions:
            if not isinstance(chat,dict):
                chatOptions.append(chat.id)
            else:
                option = {}
                option["chat"] = chat["chat"].id
                option["dialogName"] = chat["dialogName"]
                option["params"] = {}
                if "params" in chat:
                    for key, value in chat["params"].items():
                        option["params"][key] = value.id
                chatOptions.append(option)
        result["chatOptions"] = chatOptions

        return result

    '''
    getter for the players state
    '''
    def getState(self):
        state = super().getState()

        state.update({ 
                 "inventory": {},
                 "quests": {},
                 "path":self.path,
               })
                 
        # store inventory
        inventory = []
        for item in self.inventory:
            inventory.append(item.id)
        state["inventory"]["inventoryIds"] = inventory

        # store quests
        quests = []
        for quest in self.quests:
            quests.append(quest.id)
        state["quests"]["questIds"] = quests

        # store room
        # bad code: else case not handled
        if self.room:
            state["room"] = self.room.id

        # store serve quest
        # bad code: story specific code
        if self.serveQuest:
            state["serveQuest"] = self.serveQuest.id
        else:
            state["serveQuest"] = None

        (eventIds,eventStates) = self.storeStateList(self.events)
        state["eventIds"] = eventIds

        # store serve quest
        # bad code: storing the Chat options as class instead of object complicates things
        chatOptions = []
        for chat in self.basicChatOptions:
            if not isinstance(chat,dict):
                chatOptions.append(chat.id)
            else:
                option = {}
                option["chat"] = chat["chat"].id
                option["dialogName"] = chat["dialogName"]
                option["params"] = {}
                if "params" in chat:
                    for key, value in chat["params"].items():
                        option["params"][key] = value.id
                    chatOptions.append(option)
        state["chatOptions"] = chatOptions

        return state

    '''
    setter for the players state
    '''
    def setState(self,state):
        super().setState(state)

        if "unconcious" in state:
            if self.unconcious:
                self.fallUnconcious()
                self.display = displayChars.unconciousBody

        if "path" in state:
            self.path = state["path"]

        if "serveQuest" in state:
            if state["serveQuest"]:
                '''
                set value
                '''
                def setServeQuest(quest):
                    self.serveQuest = quest
                loadingRegistry.callWhenAvailable(state["serveQuest"],setServeQuest)
            else:
                self.serveQuest = None

        # set inventory
        if "inventory" in state:
            self.loadFromList(state["inventory"],self.inventory,items.getItemFromState)

        # set quests
        if "quests" in state:
            self.loadFromList(state["quests"],self.quests,quests.getQuestFromState)

        # set chat options
        # bad code: storing the Chat options as class instead of object complicates things
        if "chatOptions" in state:
            chatOptions = []
            for chatType in state["chatOptions"]:
                if not isinstance(chatType,dict):
                    chatOptions.append(chats.chatMap[chatType])
                else:
                    option = {}
                    option["chat"] = chats.chatMap[chatType["chat"]]
                    option["dialogName"] = chatType["dialogName"]
                    if "params" in chatType:
                        params = {}
                        for (key,value) in chatType["params"].items():
                            '''
                            set value
                            '''
                            def setParam(instance):
                                params[key] = instance
                            loadingRegistry.callWhenAvailable(value,setParam)
                        option["params"] = params
                    chatOptions.append(option)
            self.basicChatOptions = chatOptions

        # add new events
        if "newEvents" in state:
            for eventId in state["newEvents"]:
                eventState = state["eventStates"][eventId]
                event = events.getEventFromState(eventState)
                self.addEvent(event)

        return state

    '''
    bad code: this should be handled with a get quest quest
    TODO: delete this
    '''
    def getQuest(self):
        if self.room and self.room.quests:
            return self.room.quests.pop()
        else:
            return None

    '''
    starts the next quest in the quest list
    bad code: this is kind of incompatible with the meta quests
    '''
    def startNextQuest(self):
        if len(self.quests):
            self.quests[0].recalculate()
            try:
                self.setPathToQuest(self.quests[0])
            except:
                # bad pattern: exceptions should be logged
                pass

    '''
    straightforward getting a string with a detailed info about the character
    '''
    def getDetailedInfo(self):
        return "\nname: "+str(self.name)+"\nroom: "+str(self.room)+"\ncoordinate: "+str(self.xPosition)+" "+str(self.yPosition)+"\nsubordinates: "+str(self.subordinates)+"\nsat: "+str(self.satiation)+"\nreputation: "+str(self.reputation)

    '''
    adds a quest to the characters quest list
    bad code: this is kind of incompatible with the meta quests
    '''
    def assignQuest(self,quest,active=False):
            if active:
                self.quests.insert(0,quest)
            else:
                self.quests.append(quest)
            quest.assignToCharacter(self)
            quest.activate()
            if (active or len(self.quests) == 1):
                try:
                    if self.quests[0] == quest:
                        self.setPathToQuest(quest)
                except:
                    # bad pattern: exceptions should be logged
                    pass

    '''
    set the path to a quest
    bad pattern: this should be determined by a quests solver
    bad pattern: the walking should be done in a quest solver so this method should removed on the long run
    '''
    def setPathToQuest(self,quest):
        if hasattr(quest,"dstX") and hasattr(quest,"dstY"):
            # bad code: room and terrain should be unified into a container object
            if self.room:
                self.path = self.room.calculatePath(self.xPosition,self.yPosition,quest.dstX,quest.dstY,self.room.walkingPath)
            elif self.terrain:
                self.path = self.terrain.findPath((self.xPosition,self.yPosition),(quest.dstX,quest.dstY))
            else:
                debugMessages.append("this should not happen, character tried to go sowhere but is nowhere")
                self.path = []
        else:
            self.path = []

    '''
    straightforward adding to inventory
    '''
    def addToInventory(self,item):
        self.inventory.append(item)

    '''
    this wrapper converts a character centred call to a solver centered call
    '''
    def applysolver(self,solver):
        if not self.unconcious and not self.dead:
            solver(self)

    '''
    set state and display to unconcious
    '''
    def fallUnconcious(self):
        self.unconcious = True
        self.display = displayChars.unconciousBody

    '''
    set state and display to not unconcious
    '''
    def wakeUp(self):
        self.unconcious = False
        self.display = self.displayOriginal

    '''
    kill the character and do a bit of extra stuff like placing corpses
    '''
    def die(self,reason=None):
        # replace charcter with corpse
        # terain and room should be unified in container object
        if self.room:
            room = self.room
            room.removeCharacter(self)
            corpse = items.Corpse(self.xPosition,self.yPosition,creator=self)
            room.addItems([corpse])
        elif self.terrain:
            terrain = self.terrain
            terrain.removeCharacter(self)
            corpse = items.Corpse(self.xPosition,self.yPosition,creator=self)
            terrain.addItems([corpse])
        else:
            messages.append("this chould not happen, charcter died without beeing somewhere")

        # set attributes
        self.dead = True
        if reason:
            self.deathReason = reason
        self.path = []

        # notify listeners
        self.changed()

    '''
    walk the predetermined path
    return:
        True when done
        False when not done

    bad pattern: should be contained in quest solver
    '''
    def walkPath(self):
        # bad code: a dead charactor should not try to walk
        # bad pattern: this should be a logging assertion
        if self.dead:
            return

        # bad code: a charactor should not try to walk if it has no path
        # bad pattern: this should be a logging assertion
        if not self.path:
            self.setPathToQuest(self.quests[0])

        # move along the predetermined path
        currentPosition = (self.xPosition,self.yPosition)
        if self.path and not self.path == [currentPosition]:
            nextPosition = self.path[0]

            item = None
            if self.room:
                # move naively within a room
                # bad code: repetitive code
                if nextPosition[0] == currentPosition[0]:
                    if nextPosition[1] < currentPosition[1]:
                        item = self.room.moveCharacterDirection(self,"north")
                    elif nextPosition[1] > currentPosition[1]:
                        item = self.room.moveCharacterDirection(self,"south")
                    else:
                        # smooth over impossible state
                        if not debug:
                            # resorting to teleport
                            debugMessages.append("character moved on non continious path")
                            self.xPosition = nextPosition[0]
                            self.yPosition = nextPosition[1]
                            self.changed()
                elif nextPosition[0] == currentPosition[0]-1 and nextPosition[1] == currentPosition[1]:
                    item = self.room.moveCharacterDirection(self,"west")
                elif nextPosition[0] == currentPosition[0]+1 and nextPosition[1] == currentPosition[1]:
                    item = self.room.moveCharacterDirection(self,"east")
                else:
                    # smooth over impossible state
                    if not debug:
                        # resorting to teleport
                        debugMessages.append("character moved on non continious path")
                        self.xPosition = nextPosition[0]
                        self.yPosition = nextPosition[1]
                        self.changed()
            else:
                # check if a room was entered
                # basically checks if a walkable space/door within a room on the coordinate the chracter walks on. If there is
                # an item it will be saved for interaction
                # bad code: repetition of the movement code is bad
                # bad pattern: collision detection and room teleportation should be done in terrain

                for room in self.terrain.rooms:
                    # check north
                    # bad code repetetive code

                    # handle the character moving into the rooms boundaries
                    if room.yPosition*15+room.offsetY+room.sizeY == nextPosition[1]+1:
                        if room.xPosition*15+room.offsetX < self.xPosition and room.xPosition*15+room.offsetX+room.sizeX > self.xPosition:
                            # get the characters entry point in localizes coordinates
                            localisedEntry = (self.xPosition%15-room.offsetX,nextPosition[1]%15-room.offsetY)
                            if localisedEntry in room.walkingAccess:
                                # check whether the chracter walked into something
                                if localisedEntry in room.itemByCoordinates:
                                    for listItem in room.itemByCoordinates[localisedEntry]:
                                        if not listItem.walkable:
                                            item = listItem
                                            break
                                if item:
                                    break
                                else:
                                    # move the chracter into the room
                                    room.addCharacter(self,localisedEntry[0],localisedEntry[1])
                                    self.terrain.characters.remove(self)
                                    self.terrain = None
                                    self.changed()
                                    break
                            else:
                                # show message the character bumped into a wall
                                # bad pattern: why restrict the player to standard entry points?
                                messages.append("you cannot move there (N)")
                                break
                    # check south
                    # bad code repetetive code

                    # handle the character moving into the rooms boundaries
                    if room.yPosition*15+room.offsetY == nextPosition[1]:
                        if room.xPosition*15+room.offsetX < self.xPosition and room.xPosition*15+room.offsetX+room.sizeX > self.xPosition:
                            # get the characters entry point in localizes coordinates
                            localisedEntry = ((self.xPosition-room.offsetX)%15,((nextPosition[1]-room.offsetY)%15))
                            if localisedEntry in room.walkingAccess:
                                # check whether the chracter walked into something
                                if localisedEntry in room.itemByCoordinates:
                                    for listItem in room.itemByCoordinates[localisedEntry]:
                                        if not listItem.walkable:
                                            item = listItem
                                            break
                                if item:
                                    break
                                else:
                                    # move the chracter into the room
                                    room.addCharacter(self,localisedEntry[0],localisedEntry[1])
                                    self.terrain.characters.remove(self)
                                    self.terrain = None
                                    self.changed()
                                    break
                            else:
                                # show message the character bumped into a wall
                                # bad pattern: why restrict the player to standard entry points?
                                messages.append("you cannot move there (S)")
                                break
                    # check east
                    # bad code repetetive code

                    # handle the character moving into the rooms boundaries
                    if room.xPosition*15+room.offsetX+room.sizeX == nextPosition[0]+1:
                        if room.yPosition*15+room.offsetY < self.yPosition and room.yPosition*15+room.offsetY+room.sizeY > self.yPosition:
                            # get the characters entry point in localizes coordinates
                            localisedEntry = ((nextPosition[0]-room.offsetX)%15,(self.yPosition-room.offsetY)%15)
                            if localisedEntry in room.walkingAccess:
                                # check whether the chracter walked into something
                                if localisedEntry in room.itemByCoordinates:
                                    for listItem in room.itemByCoordinates[localisedEntry]:
                                        if not listItem.walkable:
                                            item = listItem
                                            break
                                if item:
                                    break
                                else:
                                    # move the chracter into the room
                                    room.addCharacter(self,localisedEntry[0],localisedEntry[1])
                                    self.terrain.characters.remove(self)
                                    self.terrain = None
                                    self.changed()
                                    break
                            else:
                                # show message the character bumped into a wall
                                # bad pattern: why restrict the player to standard entry points?
                                messages.append("you cannot move there (E)")
                    # check west
                    # bad code repetetive code

                    # handle the character moving into the rooms boundaries
                    if room.xPosition*15+room.offsetX == nextPosition[0]:
                        if room.yPosition*15+room.offsetY < self.yPosition and room.yPosition*15+room.offsetY+room.sizeY > self.yPosition:
                            # get the characters entry point in localizes coordinates
                            localisedEntry = ((nextPosition[0]-room.offsetX)%15,(self.yPosition-room.offsetY)%15)
                            if localisedEntry in room.walkingAccess:
                                # check whether the chracter walked into something
                                if localisedEntry in room.itemByCoordinates:
                                    for listItem in room.itemByCoordinates[localisedEntry]:
                                        if not listItem.walkable:
                                            item = listItem
                                            break
                                if item:
                                    break
                                else:
                                    # move the chracter into the room
                                    room.addCharacter(self,localisedEntry[0],localisedEntry[1])
                                    self.terrain.characters.remove(self)
                                    self.terrain = None
                                    self.changed()
                                    break
                            else:
                                messages.append("you cannot move there (W)")
                                break
                else:
                    # move the char to the next position on path
                    self.xPosition = nextPosition[0]
                    self.yPosition = nextPosition[1]
                    self.changed()
            
            if item:
                # open doors
                # bad pattern: this should not happen here
                if isinstance(item,items.Door):
                    item.apply(self)
                return False
            else:
                # smooth ovor impossible state
                if not debug:
                    if not self.path or not nextPosition == self.path[0]:
                        return False

                # remove last step from path
                if (self.xPosition == nextPosition[0] and self.yPosition == nextPosition[1]):
                    self.path = self.path[1:]
            return False
        else:
            return True

    """
    almost straightforward dropping of items
    """
    def drop(self,item):
        self.inventory.remove(item)
        item.xPosition = self.xPosition
        item.yPosition = self.yPosition
        # bad pattern: room and terrain should be combined into a container object
        if self.room:
            self.room.addItems([item])
        else:
            self.terrain.addItems([item])
        item.changed()
        self.changed()

    """
    advance the character one tick
    """
    def advance(self):
        # handle events
        while self.events and gamestate.tick > self.events[0].tick:
            event = self.events[0]
            debugMessages.append("something went wrong and event"+str(event)+"was skipped")
            self.events.remove(event)
        while self.events and gamestate.tick == self.events[0].tick:
            event = self.events[0]
            event.handleEvent()
            self.events.remove(event)

        # handle satiation
        self.satiation -= 1
        if self.satiation < 0:
            self.die(reason="you starved. This happens when your satiation falls below 0\nPrevent this by drinking using the "+commandChars.drink+" key")
            return

        # call the autosolver
        if self.automated:
            if len(self.quests):
                self.applysolver(self.quests[0].solver)
                self.changed()

    '''
    registering for notifications
    '''
    def addListener(self,listenFunction,tag="default"):
        if not tag in self.listeners:
            self.listeners[tag] = []

        if not listenFunction in self.listeners[tag]:
            self.listeners[tag].append(listenFunction)

    '''
    deregistering for notifications
    '''
    def delListener(self,listenFunction,tag="default"):
        if listenFunction in self.listeners[tag]:
            self.listeners[tag].remove(listenFunction)

        if not self.listeners[tag]:
            del self.listeners[tag]

    '''
    sending notifications
    bad code: probably misnamed
    '''
    def changed(self,tag="default",info=None):
        if not tag == "default":
            if not tag in self.listeners:
                return

            for listenFunction in self.listeners[tag]:
                listenFunction(info)
        for listenFunction in self.listeners["default"]:
            listenFunction()

"""
bad code: animals should not be characters. This means it is possible to chat with a mouse 
"""
class Mouse(Character):
    def __init__(self,display="🝆 ",xPosition=0,yPosition=0,quests=[],automated=True,name="Mouse",creator=None):
        super().__init__(display, xPosition, yPosition, quests, automated, name, creator=creator)

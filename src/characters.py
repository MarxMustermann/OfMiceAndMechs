import src.items as items
import src.quests
import json

# bad code: containers for global state
characters = None
calculatePath = None
roomsOnMap = None

"""
this is the class for characters meaning both npc and pcs. 
all characters except the pcs always have automated = True to
make them to things
"""
class Character():
    '''
    sets basic info AND adds default behaviour/items
    bad code: adding the default behaviour/items here makes it harder to create instances with fixed state
    '''
    def __init__(self,display="＠",xPosition=0,yPosition=0,quests=[],automated=True,name="Person",creator=None):
        if creator == "void":
            creator = void
        self.creationCounter = 0

        # set basic state
        self.display = display
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
        self.serveQuest = None
        self.tutorialStart = 0
        self.id = {
                   "other":"character",
                   "xPosition":xPosition,
                   "yPosition":yPosition,
                   "counter":creator.getCreationCounter()
                  }
        self.id["creator"] = creator.id
        self.id = json.dumps(self.id, sort_keys=True).replace("\\","")

        # bad code: story specific state
        self.gotBasicSchooling = False
        self.gotMovementSchooling = False
        self.gotInteractionSchooling = False
        self.gotExamineSchooling = False

        #TODO: this approach is fail, but works for now. There has to be a better way
        self.basicChatOptions = []

        # bad code: story specific state
        self.assignQuest(src.quests.SurviveQuest(creator=self))
        for quest in quests:
            self.assignQuest(quest)
        self.inventory.append(items.GooFlask(creator=self))

        self.initialState = self.getState()
        loadingRegistry.register(self)

    def getCreationCounter(self):
        self.creationCounter += 1
        return self.creationCounter

    '''
    almost straightforward adding of events to the characters event queue
    '''
    def addEvent(self,event):
        index = 0
        for existingEvent in self.events:
            if event.tick < existingEvent.tick:
                break
            index += 1
        self.events.insert(index,event)

    '''
    straightforward removeing of events from the characters event queue
    '''
    def removeEvent(self,event):
        self.events.remove(event)

    '''
    almost straightforward getter for chat options
    '''
    def getChatOptions(self,partner):
        chatOptions = self.basicChatOptions[:]
        if not self in partner.subordinates:
            chatOptions.append(interaction.RecruitChat)
            pass
        
        return chatOptions

    def getDiffState(self):
        result = {}

        def getDiffList(toDiff,toCompare,exclude=[]):
            currentThingsList = []
            states = {}
            newThingsList = []
            changedThingsList = []
            removedThingsList = []

            for thing in toDiff:
                if thing.id in exclude:
                    continue
                currentState = thing.getState()
                currentThingsList.append(thing.id)

                if thing.id in toCompare:
                    if not currentState == thing.initialState:
                        diffState = thing.getDiffState()
                        if diffState:
                            changedThingsList.append(thing.id)
                            states[thing.id] = diffState
                else:
                    newThingsList.append(thing.id)
                    states[thing.id] = thing.getState()

            for thingId in toCompare:
                if thingId in exclude:
                    continue
                if not thingId in currentThingsList:
                    removedThingsList.append(thingId)

            return (states,changedThingsList,newThingsList,removedThingsList)

        if not self.gotBasicSchooling == self.initialState["gotBasicSchooling"]:
            result["gotBasicSchooling"] = self.gotBasicSchooling
        if not self.gotMovementSchooling == self.initialState["gotMovementSchooling"]:
            result["gotMovementSchooling"] = self.gotMovementSchooling
        if not self.gotInteractionSchooling == self.initialState["gotInteractionSchooling"]:
            result["gotInteractionSchooling"] = self.gotInteractionSchooling
        if not self.gotExamineSchooling == self.initialState["gotExamineSchooling"]:
            result["gotExamineSchooling"] = self.gotExamineSchooling
        if not self.xPosition == self.initialState["xPosition"]:
            result["xPosition"] = self.xPosition
        if not self.yPosition == self.initialState["yPosition"]:
            result["yPosition"] = self.yPosition
        if not self.name == self.initialState["name"]:
            result["name"] = self.name
        if not self.satiation == self.initialState["satiation"]:
            result["satiation"] = self.satiation
        if not self.unconcious == self.initialState["unconcious"]:
            result["unconcious"] = self.unconcious
        if not self.reputation == self.initialState["reputation"]:
            result["reputation"] = self.reputation
        if not self.tutorialStart == self.initialState["tutorialStart"]:
            result["tutorialStart"] = self.tutorialStart
        if not self.creationCounter == self.initialState["creationCounter"]:
            result["creationCounter"] = self.creationCounter
        if not self.path == self.initialState["path"]:
            result["path"] = self.path
        serveQuest = None
        if self.serveQuest:
            serveQuest = self.serveQuest.id
        if not serveQuest == self.initialState["serveQuest"]:
            result["serveQuest"] = serveQuest

        (itemStates,changedItems,newItems,removedItems) = getDiffList(self.inventory,self.initialState["inventory"]["inventoryIds"])
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

        (questStates,changedQuests,newQuests,removedQuests) = getDiffList(self.quests,self.initialState["quests"]["questIds"])
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

        chatOptions = []
        for chat in self.basicChatOptions:
            chatOptions.append(chat.id)
        result["chatOptions"] = chatOptions

        return result

    '''
    mostly non working getter for the players state
    bad code: this state is basicall useless
    '''
    def getState(self):
        state = { 
                 "id": self.id,
                 "gotBasicSchooling": self.gotBasicSchooling,
                 "gotMovementSchooling": self.gotMovementSchooling,
                 "gotInteractionSchooling": self.gotInteractionSchooling,
                 "gotExamineSchooling": self.gotExamineSchooling,
                 "xPosition": self.xPosition,
                 "yPosition": self.yPosition,
                 "name": self.name,
                 "satiation": self.satiation,
                 "unconcious": self.unconcious,
                 "reputation": self.reputation,
                 "inventory": {},
                 "quests": {},
                 "creationCounter":self.creationCounter,
                 "tutorialStart":self.tutorialStart,
                 "path":self.path,
               }
                 
        inventory = []
        for item in self.inventory:
            inventory.append(item.id)
        state["inventory"]["inventoryIds"] = inventory

        quests = []
        for quest in self.quests:
            quests.append(quest.id)
        state["quests"]["questIds"] = quests

        if self.room:
            state["room"] = self.room.id

        if self.serveQuest:
            state["serveQuest"] = self.serveQuest.id
        else:
            state["serveQuest"] = None

        chatOptions = []
        for chat in self.basicChatOptions:
            chatOptions.append(chat.id)
        state["chatOptions"] = chatOptions

        return state

    '''
    mostly non working setter for the players state
    bad code: this state is basicall useless
    '''
    def setState(self,state):
        if "creationCounter" in state:
            self.creationCounter = state["creationCounter"]

        if "id" in state:
            self.id = state["id"]
        if "gotBasicSchooling" in state:
            self.gotBasicSchooling = state["gotBasicSchooling"]
        if "gotMovementSchooling" in state:
            self.gotMovementSchooling = state["gotMovementSchooling"]
        if "gotInteractionSchooling" in state:
            self.gotInteractionSchooling = state["gotInteractionSchooling"]
        if "gotExamineSchooling" in state:
            self.gotExamineSchooling = state["gotExamineSchooling"]
        if "yPosition" in state:
            self.yPosition = state["yPosition"]
        if "xPosition" in state:
            self.xPosition = state["xPosition"]
        if "name" in state:
            self.name = state["name"]
        if "satiation" in state:
            self.satiation = state["satiation"]
        if "unconcious" in state:
            self.unconcious = state["unconcious"]
            if self.unconcious:
                self.fallUnconcious()
                self.display = displayChars.unconciousBody
        if "reputation" in state:
            self.reputation = state["reputation"]
        if "tutorialStart" in state:
            self.tutorialStart = state["tutorialStart"]
        if "path" in state:
            self.path = state["path"]

        if "serveQuest" in state:
            if state["serveQuest"]:
                def setServeQuest(quest):
                    self.serveQuest = quest
                loadingRegistry.callWhenAvailable(state["serveQuest"],setServeQuest)
            else:
                self.serveQuest = None

        if "inventory" in state:
            if "changed" in state["inventory"]:
                for item in self.inventory:
                    if item.id in state["inventory"]["changed"]:
                        item.setState(state["inventory"]["states"][item.id])
            if "removed" in state["inventory"]:
                for item in self.inventory:
                    if item.id in state["inventory"]["removed"]:
                        self.inventory.remove(item)
            if "new" in state["inventory"]:
                for itemId in state["inventory"]["new"]:
                    itemState = state["inventory"]["states"][itemId]
                    item = items.getItemFromState(itemState)
                    item.setState(itemState)
                    self.inventory.append(item)

        if "quests" in state:
            if "changed" in state["quests"]:
                for item in self.quests:
                    if item.id in state["quests"]["states"]:
                        item.setState(state["quests"]["states"][item.id])
            if "removed" in state["quests"]:
                for item in self.quests:
                    if item.id in state["quests"]["removed"]:
                        self.quests.remove(item)
            if "new" in state["quests"]:
                for itemId in state["quests"]["new"]:
                    itemState = state["quests"]["states"][itemId]
                    item = quests.getQuestFromState(itemState)
                    item.setState(itemState)
                    self.quests.append(item)

        if "chatOptions" in state:
            chatOptions = []
            for chatType in state["chatOptions"]:
                chatOptions.append(chats.chatMap[chatType])
            self.basicChatOptions = chatOptions

        return state

    '''
    bad code: this should be handled with a get quest quest
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
                pass

    '''
    straightforward getting a string with a detailed info about the character
    '''
    def getDetailedInfo(self):
        return "\nname: "+str(self.name)+"\nroom: "+str(self.room)+"\ncoord: "+str(self.xPosition)+" "+str(self.yPosition)+"\nsubs: "+str(self.subordinates)+"\nsat: "+str(self.satiation)+"\nreputation: "+str(self.reputation)+"\npath: "+str(self.path)

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
                    pass

    '''
    set the path to a quest
    bad code: this should be determined by a quests solver
    '''
    def setPathToQuest(self,quest):
        if hasattr(quest,"dstX") and hasattr(quest,"dstY"):
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

    def fallUnconcious(self):
        self.unconcious = True
        self.display = displayChars.unconciousBody

    def wakeUp(self):
        self.unconcious = False
        self.display = self.displayOriginal

    '''
    kill the character and do a bit of extra stuff like placing corpses
    '''
    def die(self,reason=None):
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

        self.dead = True
        if reason:
            self.deathReason = reason
        self.path = []
        self.changed()

    '''
    walk the predetermined path
    '''
    def walkPath(self):
        # bad code: a dead charactor should not try to walk
        if self.dead:
            return

        # bad code: a charactor should not try to walk if it has no path
        if not self.path:
            self.setPathToQuest(self.quests[0])

        # move along the predetermined path
        currentPosition = (self.xPosition,self.yPosition)
        if self.path and not self.path == [currentPosition]:
            nextPosition = self.path[0]

            item = None
            if self.room:
                # move naively within a room
                if nextPosition[0] == currentPosition[0]:
                    if nextPosition[1] < currentPosition[1]:
                        item = self.room.moveCharacterDirection(self,"north")
                    elif nextPosition[1] > currentPosition[1]:
                        item = self.room.moveCharacterDirection(self,"south")
                    else:
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

                for room in self.terrain.rooms:
                    # check north
                    if room.yPosition*15+room.offsetY+room.sizeY == nextPosition[1]+1:
                        if room.xPosition*15+room.offsetX < self.xPosition and room.xPosition*15+room.offsetX+room.sizeX > self.xPosition:
                            localisedEntry = (self.xPosition%15-room.offsetX,nextPosition[1]%15-room.offsetY)
                            if localisedEntry in room.walkingAccess:
                                if localisedEntry in room.itemByCoordinates:
                                    for listItem in room.itemByCoordinates[localisedEntry]:
                                        if not listItem.walkable:
                                            item = listItem
                                            break
                                if item:
                                    break
                                else:
                                    room.addCharacter(self,localisedEntry[0],localisedEntry[1])
                                    self.terrain.characters.remove(self)
                                    self.terrain = None
                                    self.changed()
                                    break
                            else:
                                messages.append("you cannot move there (N)")
                                break
                    # check south
                    if room.yPosition*15+room.offsetY == nextPosition[1]:
                        if room.xPosition*15+room.offsetX < self.xPosition and room.xPosition*15+room.offsetX+room.sizeX > self.xPosition:
                            localisedEntry = ((self.xPosition-room.offsetX)%15,((nextPosition[1]-room.offsetY)%15))
                            if localisedEntry in room.walkingAccess:
                                if localisedEntry in room.itemByCoordinates:
                                    for listItem in room.itemByCoordinates[localisedEntry]:
                                        if not listItem.walkable:
                                            item = listItem
                                            break
                                if item:
                                    break
                                else:
                                    room.addCharacter(self,localisedEntry[0],localisedEntry[1])
                                    self.terrain.characters.remove(self)
                                    self.terrain = None
                                    self.changed()
                                    break
                            else:
                                messages.append("you cannot move there (S)")
                                break
                    # check east
                    if room.xPosition*15+room.offsetX+room.sizeX == nextPosition[0]+1:
                        if room.yPosition*15+room.offsetY < self.yPosition and room.yPosition*15+room.offsetY+room.sizeY > self.yPosition:
                            localisedEntry = ((nextPosition[0]-room.offsetX)%15,(self.yPosition-room.offsetY)%15)
                            if localisedEntry in room.walkingAccess:
                                if localisedEntry in room.itemByCoordinates:
                                    for listItem in room.itemByCoordinates[localisedEntry]:
                                        if not listItem.walkable:
                                            item = listItem
                                            break
                                if item:
                                    break
                                else:
                                    room.addCharacter(self,localisedEntry[0],localisedEntry[1])
                                    self.terrain.characters.remove(self)
                                    self.terrain = None
                                    self.changed()
                                    break
                            else:
                                messages.append("you cannot move there (E)")
                    # check west
                    if room.xPosition*15+room.offsetX == nextPosition[0]:
                        if room.yPosition*15+room.offsetY < self.yPosition and room.yPosition*15+room.offsetY+room.sizeY > self.yPosition:
                            localisedEntry = ((nextPosition[0]-room.offsetX)%15,(self.yPosition-room.offsetY)%15)
                            if localisedEntry in room.walkingAccess:
                                if localisedEntry in room.itemByCoordinates:
                                    for listItem in room.itemByCoordinates[localisedEntry]:
                                        if not listItem.walkable:
                                            item = listItem
                                            break
                                if item:
                                    break
                                else:
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
                if isinstance(item,items.Door):
                    item.apply(self)
                return False
            else:
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
        while self.events and gamestate.tick >  self.events[0].tick:
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
    def __init__(self,display="🝆 ",xPosition=0,yPosition=0,quests=[],automated=True,name="Mouse"):
        super().__init__(display, xPosition, yPosition, quests, automated, name)

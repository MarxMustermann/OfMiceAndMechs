import src.items as items
import src.quests

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
    def __init__(self,display="＠",xPosition=0,yPosition=0,quests=[],automated=True,name="Person"):
        # set basic state
        self.display = display
        self.automated = automated
        self.quests = []
        self.name = name
        self.inventory = []
        self.watched = False
        self.listeners = {"default":[],"activate":[]}
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

        # bad code: story specific state
        self.gotBasicSchooling = False
        self.gotMovementSchooling = False
        self.gotInteractionSchooling = False
        self.gotExamineSchooling = False

        #TODO: this approach is fail, but works for now. There has to be a better way
        self.basicChatOptions = []

        # bad code: story specific state
        self.assignQuest(src.quests.SurviveQuest())
        for quest in quests:
            self.assignQuest(quest)
        self.inventory.append(items.GooFlask())

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

    '''
    mostly non working getter for the players state
    bad code: this state is basicall useless
    '''
    def getState(self):
        return { "gotBasicSchooling": self.gotBasicSchooling,
                 "gotMovementSchooling": self.gotMovementSchooling,
                 "gotInteractionSchooling": self.gotInteractionSchooling,
                 "gotExamineSchooling": self.gotExamineSchooling,
               }

    '''
    mostly non working setter for the players state
    bad code: this state is basicall useless
    '''
    def setState(self,state):
        self.gotBasicSchooling = state["gotBasicSchooling"]
        self.gotMovementSchooling = state["gotMovementSchooling"]
        self.gotInteractionSchooling = state["gotInteractionSchooling"]
        self.gotExamineSchooling = state["gotExamineSchooling"]

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
        return "\nname: "+str(self.name)+"\nroom: "+str(self.room)+"\ncoord: "+str(self.xPosition)+" "+str(self.yPosition)+"\nsubs: "+str(self.subordinates)+"\nsat: "+str(self.satiation)+"\nreputation: "+str(self.reputation)

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
    bad code: i think this shouldn't be an extra method
    '''
    def applysolver(self,solver):
        solver(self)

    '''
    kill the character and do a bit of extra stuff like placing corpses
    '''
    def die(self,reason=None):
        if self.room:
            room = self.room
            room.removeCharacter(self)
            corpse = items.Corpse(self.xPosition,self.yPosition)
            room.addItems([corpse])
        elif self.terrain:
            terrain = self.terrain
            terrain.removeCharacter(self)
            corpse = items.Corpse(self.xPosition,self.yPosition)
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
                        item = self.room.moveCharacterNorth(self)
                    elif nextPosition[1] > currentPosition[1]:
                        item = self.room.moveCharacterSouth(self)
                    else:
                        if not debug:
                            # resorting to teleport
                            debugMessages.append("character moved on non continious path")
                            self.xPosition = nextPosition[0]
                            self.yPosition = nextPosition[1]
                            self.changed()
                elif nextPosition[0] == currentPosition[0]-1 and nextPosition[1] == currentPosition[1]:
                    item = self.room.moveCharacterWest(self)
                elif nextPosition[0] == currentPosition[0]+1 and nextPosition[1] == currentPosition[1]:
                    item = self.room.moveCharacterEast(self)
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
        if not listenFunction in self.listeners[tag]:
            self.listeners[tag].append(listenFunction)

    '''
    deregistering for notifications
    '''
    def delListener(self,listenFunction,tag="default"):
        if listenFunction in self.listeners[tag]:
            self.listeners[tag].remove(listenFunction)

    '''
    sending notifications
    bad code: probably misnamed
    '''
    def changed(self,tag="default",info=None):
        if not tag == "default":
            for listenFunction in self.listeners[tag]:
                if tag == "activate":
                    listenFunction(info)
                else:
                    listenFunction()
        for listenFunction in self.listeners["default"]:
            listenFunction()

"""
bad code: animals should not be characters. This means it is possible to chat with a mouse 
"""
class Mouse(Character):
    def __init__(self,display="🝆 ",xPosition=0,yPosition=0,quests=[],automated=True,name="Mouse"):
        super().__init__(display, xPosition, yPosition, quests, automated, name)

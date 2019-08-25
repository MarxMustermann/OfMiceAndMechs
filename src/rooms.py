#############################################################################
###
##    rooms and room related code belong here
#
#############################################################################

# import basic libs
import json

# import basic internal libs
import src.items
import src.quests
import src.saveing

# bad code: global state
Character = None
mainChar = None
characters = None
messages = None
debugMessages = None
calculatePath = None
displayChars = None

'''
the base class for all rooms
'''
class Room(src.saveing.Saveable):
    '''
    state initialization
    bad code: too many attributes
    '''
    def __init__(self,layout,xPosition,yPosition,offsetX,offsetY,desiredPosition=None,creator=None):
        super().__init__()

        # initialize attributes
        self.desiredPosition = desiredPosition
        self.desiredSteamGeneration = None
        self.layout = layout
        self.hidden = True
        self.itemsOnFloor = []
        self.characters = []
        self.doors = []
        self.xPosition = None
        self.yPosition = None
        self.name = "Room"
        self.open = False
        self.terrain = None
        self.shownQuestmarkerLastRender = False
        self.sizeX = None
        self.sizeY = None
        self.timeIndex = 0
        self.delayedTicks = 0
        self.events = []
        self.floorDisplay = [displayChars.floor]
        self.lastMovementToken = None
        self.chainedTo = []
        self.engineStrength = 0
        self.boilers = []
        self.growthTanks = []
        self.furnaces = []
        self.pipes = []
        self.sprays = []
        self.piles = []
        self.steamGeneration = 0
        self.firstOfficer = None
        self.secondOfficer = None
        self.offsetX = offsetX
        self.offsetY = offsetY
        self.xPosition = xPosition
        self.yPosition = yPosition
        self.lastRender = None
        self.isContainment = False
        self.listeners = {"default":[]}

        # set id
        self.id = {
                   "other":"room",
                   "xPosition":xPosition,
                   "yPosition":yPosition,
                   "counter":creator.getCreationCounter()
                  }
        self.id["creator"] = creator.id
        self.id = json.dumps(self.id, sort_keys=True).replace("\\","")
            
        self.itemByCoordinates = {}

        # generate the items the room consists of from definition
        # bad code: lot of redundant code
        self.walkingAccess = []
        lineCounter = 0
        itemsOnFloor = []
        for line in self.layout[1:].split("\n"):
            rowCounter = 0
            for char in line:
                if char in (" ","."):
                    # skip non items
                    pass
                elif char in ("@",):
                    # add default npcs
                    if (not self.firstOfficer) or (not self.secondOfficer):
                        if not self.firstOfficer:
                            # add first officer
                            npc = characters.Character(xPosition=5,yPosition=3,creator=self,seed=self.xPosition+2*self.offsetY+self.offsetX+2*self.yPosition)
                            self.addCharacter(npc,rowCounter,lineCounter)
                            npc.terrain = self.terrain
                            self.firstOfficer = npc
                            quest = src.quests.RoomDuty(creator=self)
                            npc.assignQuest(quest,active=True)
                        else:
                            # add second officer
                            npc = characters.Character(xPosition=6,yPosition=4,creator=self,seed=self.yPosition+2*self.offsetX+self.offsetY+2*self.xPosition)
                            self.addCharacter(npc,rowCounter,lineCounter)
                            npc.terrain = self.terrain
                            self.secondOfficer = npc
                            quest = src.quests.RoomDuty(creator=self)
                            npc.assignQuest(quest,active=True)
                elif char in ("X","&"):
                    # add wall
                    itemsOnFloor.append(src.items.Wall(rowCounter,lineCounter,creator=self))
                elif char == "$":
                    # add door and mark position as entry point
                    door = src.items.Door(rowCounter,lineCounter,creator=self)
                    itemsOnFloor.append(door)
                    self.walkingAccess.append((rowCounter,lineCounter))
                    self.doors.append(door)
                elif char == "P":
                    # add pile and save to list
                    item = src.items.Pile(rowCounter,lineCounter,creator=self)
                    itemsOnFloor.append(item)
                    self.piles.append(item)
                elif char == "F":
                    # add furnace and save to list
                    item = src.items.Furnace(rowCounter,lineCounter,creator=self)
                    itemsOnFloor.append(item)
                    self.furnaces.append(item)
                elif char == "#":
                    # add pipe and save to list
                    item = src.items.Pipe(rowCounter,lineCounter,creator=self)
                    itemsOnFloor.append(item)
                    self.pipes.append(item)
                elif char == "D":
                    # add display
                    itemsOnFloor.append(src.items.Display(rowCounter,lineCounter,creator=self))
                elif char == "v":
                    # to be bin
                    itemsOnFloor.append(src.items.Item(displayChars.binStorage,rowCounter,lineCounter,creator=self))
                elif char == "O":
                    # add pressure Tank
                    item = src.items.Boiler(rowCounter,lineCounter,creator=self)
                    itemsOnFloor.append(item)
                    self.boilers.append(item)
                elif char == "8":
                    # to be chains
                    itemsOnFloor.append(src.items.Item(displayChars.chains,rowCounter,lineCounter,creator=self))
                elif char == "I":
                     #to be commlink
                    itemsOnFloor.append(src.items.Commlink(rowCounter,lineCounter,creator=self))
                elif char in ["H","'"]:
                    # add hutch
                    # bad code: handle state some other way
                    mapping = {"H":False,"'":True}
                    itemsOnFloor.append(src.items.Hutch(rowCounter,lineCounter,creator=self,activated=mapping[char]))
                elif char == "o":
                    #to be grid
                    itemsOnFloor.append(src.items.Item(displayChars.grid,rowCounter,lineCounter,creator=self))
                elif char == "a":
                    #to be acid
                    item = src.items.Item(displayChars.acids[((2*rowCounter)+lineCounter)%5],rowCounter,lineCounter,creator=self)
                    item.walkable = True
                    itemsOnFloor.append(item)
                elif char == "b":
                    # to be foodstuffs
                    itemsOnFloor.append(src.items.Item(displayChars.foodStuffs[((2*rowCounter)+lineCounter)%6],rowCounter,lineCounter,creator=self))
                elif char == "m":
                    # to be machinery
                    itemsOnFloor.append(src.items.Item(displayChars.machineries[((2*rowCounter)+lineCounter)%5],rowCounter,lineCounter,creator=self))
                elif char == "h":
                    # add steam hub
                    itemsOnFloor.append(src.items.Item(displayChars.hub,rowCounter,lineCounter,creator=self))
                elif char == "i":
                    # add ramp
                    itemsOnFloor.append(src.items.Item(displayChars.ramp,rowCounter,lineCounter,creator=self))
                elif char in ["q","r","s","t","u","z"]:
                    # add special pipe
                    # bad code: pipe connection should be done some other way
                    mapping = {"q":displayChars.pipe_lr,"r":displayChars.pipe_lrd,"s":displayChars.pipe_ld,"t":displayChars.pipe_lu,"u":displayChars.pipe_ru,"z":displayChars.pipe_ud}
                    item = src.items.Item(mapping[char],rowCounter,lineCounter,creator=self)
                    item.walkable = True
                    itemsOnFloor.append(item)
                elif char in ["w","x"]:
                    # add spray
                    # bad code: handle orientation some other way
                    mapping = {"w":"right","x":"left"}
                    item = src.items.Spray(rowCounter,lineCounter,direction=mapping[char],creator=self)
                    itemsOnFloor.append(item)
                    self.sprays.append(item)
                elif char == "y":
                    # to be outlet
                    itemsOnFloor.append(src.items.Item(displayChars.outlet,rowCounter,lineCounter,creator=self))
                elif char == "j":
                    # to be vat snake
                    itemsOnFloor.append(src.items.Item(displayChars.vatSnake,rowCounter,lineCounter,creator=self))
                elif char == "c":
                    # add corpse
                    item = src.items.Corpse(rowCounter,lineCounter,creator=self)
                    itemsOnFloor.append(item)
                elif char in ["Ö","ö"]:
                    # add growth tank
                    # bad code: specal chars should not be used in code
                    # bad code: handle state some other way
                    mapping = {"Ö":True,"ö":False}
                    item = src.items.GrowthTank(rowCounter,lineCounter,filled=mapping[char],creator=self)
                    self.growthTanks.append(item)
                    itemsOnFloor.append(item)
                elif char == "B":
                    # add to be barricade
                    item = src.items.Item(displayChars.barricade,rowCounter,lineCounter,creator=self)
                    item.walkable = True
                    itemsOnFloor.append(item)
                else:
                    # add undefined stuff
                    itemsOnFloor.append(src.items.Item(displayChars.randomStuff2[((2*rowCounter)+lineCounter)%10],rowCounter,lineCounter,creator=self))
                rowCounter += 1
                self.sizeX = rowCounter
            lineCounter += 1
        self.sizeY = lineCounter-1

        # extract waypoints for default path from layout
        rawWalkingPath = []
        lineCounter = 0
        for line in self.layout[1:].split("\n"):
            rowCounter = 0
            for char in line:
                if char == ".":
                    rawWalkingPath.append((rowCounter,lineCounter))
                rowCounter += 1
            lineCounter += 1

        # start path with first waypoint
        self.walkingPath = []
        startWayPoint = rawWalkingPath[0]
        endWayPoint = rawWalkingPath[0]
        self.walkingPath.append(rawWalkingPath[0])
        rawWalkingPath.remove(rawWalkingPath[0])

        # add remaining waypoints to path
        while (1==1):
            # get neighbour positions
            # bad code: should be in position object
            endWayPoint = self.walkingPath[-1]
            east = (endWayPoint[0]+1,endWayPoint[1])
            west = (endWayPoint[0]-1,endWayPoint[1])
            south = (endWayPoint[0],endWayPoint[1]+1)
            north = (endWayPoint[0],endWayPoint[1]-1)

            # extend path
            if east in rawWalkingPath:
                self.walkingPath.append(east)
                rawWalkingPath.remove(east)
            elif west in rawWalkingPath:
                self.walkingPath.append(west)
                rawWalkingPath.remove(west)
            elif south in rawWalkingPath:
                self.walkingPath.append(south)
                rawWalkingPath.remove(south)
            elif north in rawWalkingPath:
                self.walkingPath.append(north)
                rawWalkingPath.remove(north)
            else:
                break

        # add the items generated earlier
        self.addItems(itemsOnFloor)

        # set meta information for saving
        self.attributesToStore.extend([
              "yPosition","xPosition","offsetX","offsetY"
                ])

        self.initialState = self.getState()
        loadingRegistry.register(self)

    '''
    registering for notifications
    bad code: should be in extra class
    '''
    def addListener(self,listenFunction,tag="default"):
        if not tag in self.listeners:
            self.listeners[tag] = []

        if not listenFunction in self.listeners[tag]:
            self.listeners[tag].append(listenFunction)

    '''
    deregistering for notifications
    bad code: should be in extra class
    '''
    def delListener(self,listenFunction,tag="default"):
        if listenFunction in self.listeners[tag]:
            self.listeners[tag].remove(listenFunction)

        if not self.listeners[tag]:
            del self.listeners[tag]

    '''
    sending notifications
    bad code: probably misnamed
    bad code: should be in extra class
    '''
    def changed(self,tag="default",info=None):
        self.requestRedraw()
        if not tag == "default":
            if not tag in self.listeners:
                return

            for listenFunction in self.listeners[tag]:
                listenFunction(info)
        for listenFunction in self.listeners["default"]:
            listenFunction()

    '''
    get the difference in state since creation
    '''
    def getDiffState(self):
        result = super().getDiffState()

        # store item diff
        (itemStates,changedItems,newItems,removedItems) = self.getDiffList(self.itemsOnFloor,self.initialState["itemIds"])
        if changedItems:
            result["changedItems"] = changedItems
        if newItems:
            result["newItems"] = newItems
        if removedItems:
            result["removedItems"] = removedItems
        if itemStates:
            result["itemStates"] = itemStates

        # store characters diff
        exclude = []
        if mainChar:
            exclude.append(mainChar.id)
        (charStates,changedChars,newChars,removedChars) = self.getDiffList(self.characters,self.initialState["characterIds"],exclude=exclude)
        if changedChars:
            result["changedChars"] = changedChars
        if newChars:
            result["newChars"] = newChars
        if removedChars:
            result["removedChars"] = removedChars
        if charStates:
            result["charStates"] = charStates

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

        return result

    '''
    get semi serialised room state
    '''
    def getState(self):
        state = super().getState()

        # get states from lists
        (eventIds,eventStates) = self.storeStateList(self.events)
        (itemIds,itemStates) = self.storeStateList(self.itemsOnFloor)
        (charIds,charStates) = self.storeStateList(self.characters)

        # store the substates
        state["eventIds"] = eventIds
        state["eventStates"] = eventStates
        state["itemIds"] = itemIds
        state["itemStates"] = itemStates
        state["characterIds"] = charIds
        state["characterStates"] = charStates

        return state

    '''
    construct state from semi serialised form
    bad code: incomplete
    '''
    def setState(self,state):
        # move room to correct position
        xPosition = None
        yPosition = None
        if "xPosition" in state and not "yPosition" in state:
            xPosition = state["xPosition"]
            yPosition = self.yPosition
        if not "xPosition" in state and "yPosition" in state:
            xPosition = self.xPosition
            yPosition = state["yPosition"]
        if "xPosition" in state and "yPosition" in state:
            xPosition = state["xPosition"]
            yPosition = state["yPosition"]

        if not xPosition == None and not yPosition == None:
            self.terrain.teleportRoom(self,(xPosition,yPosition))

        super().setState(state)

        # update changed items
        if "changedItems" in state:
            for item in self.itemsOnFloor[:]:
                if item.id in state["changedItems"]:
                    self.removeItem(item)
                    item.setState(state["itemStates"][item.id])
                    self.addItems([item])

        # remove items
        if "removedItems" in state:
            for item in self.itemsOnFloor[:]:
                if item.id in state["removedItems"]:
                    self.removeItem(item)
            
        # add new items
        if "newItems" in state:
            for itemId in state["newItems"]:
                itemState = state["itemStates"][itemId]
                item = src.items.getItemFromState(itemState)
                self.addItems([item])

        # update changed chars
        if "changedChars" in state:
            for char in self.characters:
                if char.id in state["changedChars"]:
                    char.setState(state["charStates"][char.id])

        # remove chars
        if "removedChars" in state:
            for char in self.characters[:]:
                if char.id in state["removedChars"]:
                    self.removeCharacter(char)
            
        # add new chars
        if "newChars" in state:
            for charId in state["newChars"]:
                charState = state["charStates"][charId]
                char = characters.Character(creator=void)
                char.setState(charState)
                loadingRegistry.register(char)
                self.addCharacter(char,charState["xPosition"],charState["yPosition"])

        # add new events
        if "newEvents" in state:
            for eventId in state["newEvents"]:
                eventState = state["eventStates"][eventId]
                event = events.getEventFromState(eventState)
                self.addEvent(event)

        self.forceRedraw()

    '''
    get physical resistance against beeing moved
    '''
    def getResistance(self):
        return self.sizeX*self.sizeY

    '''
    open all doors
    bad code: this method seems to be very specialised/kind of useless
    '''
    def openDoors(self):
        for door in self.doors:
            door.open()
            self.open = True

    '''
    close all doors
    bad code: this method seems to be very specialised/kind of useless
    '''
    def closeDoors(self):
        for door in self.doors:
            door.close()
            self.open = False

    def findPath(self, start, end):
        return self.calculatePath(start[0],start[1],end[0],end[1],self.walkingPath)

    '''
    forward naive path calculation
    bad code: should have proper pathfinding
    '''
    def calculatePath(self,x,y,dstX,dstY,walkingPath):
        path = calculatePath(x,y,dstX,dstY,walkingPath)
        return path

    '''
    render the room
    '''
    def render(self):
        # skip rendering
        if self.lastRender:
            return self.lastRender
        
        # render room
        if not self.hidden:
            # fill the area with floor tiles
            chars = []
            fixedChar = None
            if len(self.floorDisplay) == 1:
                fixedChar = self.floorDisplay[0]
            for i in range(0,self.sizeY):
                subChars = []
                for j in range(0,self.sizeX):
                    if fixedChar:
                        subChars.append(fixedChar)
                    else:
                        subChars.append(self.floorDisplay[(j+i+self.timeIndex*2)%len(self.floorDisplay)])
                chars.append(subChars)
            
            # draw items
            for item in self.itemsOnFloor:
                chars[item.yPosition][item.xPosition] = item.display

            # draw characters
            for character in self.characters:
                if character.yPosition < len(chars) and character.xPosition < len(chars[character.yPosition]):
                    chars[character.yPosition][character.xPosition] = character.display
                else:
                    debugMessages.append("chracter is rendered outside of room")

            # draw quest markers
            # bad code: should be an overlay
            if mainChar.room == self:
                if len(mainChar.quests):
                        # show the questmarker every second turn for blinking effect
                        if not self.shownQuestmarkerLastRender:
                            self.shownQuestmarkerLastRender = True

                            # mark the target of each quest
                            # bad code: does not work with meta quests
                            for quest in mainChar.quests:
                                if not quest.active:
                                    continue

                                # mark secondary quest targets using background colour
                                try:
                                    import urwid
                                    display = chars[quest.dstY][quest.dstX]
                                    chars[quest.dstY][quest.dstX] = displayChars.questTargetMarker
                                    if isinstance(display, int):
                                        display = displayChars.indexedMapping[display]
                                    if isinstance(display, str):
                                        display = (urwid.AttrSpec("default","black"),display)
                                    chars[quest.dstY][quest.dstX] = (urwid.AttrSpec(display[0].foreground,"#323"),display[1])
                                except:
                                    pass

                                # mark primary quest target with the target marker
                                try:
                                    chars[mainChar.quests[0].dstY][mainChar.quests[0].dstX] = displayChars.questTargetMarker
                                except:
                                    pass

                            # highlight the path to the quest target using background color
                            try:
                                path = self.calculatePath(mainChar.xPosition,mainChar.yPosition,mainChar.quests[0].dstX,mainChar.quests[0].dstY,self.walkingPath)
                                for item in path:
                                    import urwid
                                    display = chars[item[1]][item[0]]
                                    if isinstance(display, int):
                                        display = displayChars.indexedMapping[display]
                                    if isinstance(display, str):
                                        display = (urwid.AttrSpec("default","black"),display)
                                    chars[item[1]][item[0]] = (urwid.AttrSpec(display[0].foreground,"#333"),display[1])
                            except:
                                pass
                        #  don't show the questmarker every second turn for blinking effect
                        else:
                            self.shownQuestmarkerLastRender = False

            # draw main char
            if mainChar in self.characters:
                if mainChar.yPosition < len(chars) and mainChar.xPosition < len(chars[mainChar.yPosition]):
                    chars[mainChar.yPosition][mainChar.xPosition] = mainChar.display
                else:
                    debugMessages.append("chracter is rendered outside of room")

        # show dummy of the room
        else:
            # fill the rooms inside with invisibility char
            chars = []
            for i in range(0,self.sizeY):
                subChars = []
                for j in range(0,self.sizeX):
                    subChars.append(displayChars.invisibleRoom)
                chars.append(subChars)

            # render rooms outline
            for item in self.itemsOnFloor:
                if item.xPosition == 0 or item.xPosition == self.sizeX-1 or item.yPosition == 0 or item.yPosition == self.sizeY-1:
                    chars[item.yPosition][item.xPosition] = item.display

        # cache rendering result
        self.lastRender = chars

        return chars

    '''
    drop rendering cache
    '''
    def forceRedraw(self):
        self.lastRender = None

    '''
    maybe drop rendering cache
    '''
    def requestRedraw(self):
        if not self.hidden:
            self.lastRender = None

    '''
    teleport character into the room
    '''
    def addCharacter(self,character,x,y):
        self.characters.append(character)
        character.room = self
        character.xPosition = x
        character.yPosition = y
        character.path = []
        self.changed("entered room",character)

    '''
    teleport character out of the room
    '''
    def removeCharacter(self,character):
        self.changed("left room",character)
        character.changed("left room",self)
        self.characters.remove(character)
        character.room = None

    '''
    add items to internal structure
    '''
    def addItems(self,items):
        # add the items to the item list
        self.itemsOnFloor.extend(items)

        # add the items to the easy access map
        for item in items:
            item.room = self
            item.terrain = None
            if (item.xPosition,item.yPosition) in self.itemByCoordinates:
                self.itemByCoordinates[(item.xPosition,item.yPosition)].append(item)
            else:
                self.itemByCoordinates[(item.xPosition,item.yPosition)] = [item]

    '''
    remove item from internal structure
    bad pattern: should be removeItems
    '''
    def removeItem(self,item):
        # remove items from easy access map
        if (item.xPosition,item.yPosition) in self.itemByCoordinates and item in self.itemByCoordinates[(item.xPosition,item.yPosition)]:
            self.itemByCoordinates[(item.xPosition,item.yPosition)].remove(item)
            if not self.itemByCoordinates[(item.xPosition,item.yPosition)]:
                del self.itemByCoordinates[(item.xPosition,item.yPosition)]

        # remove item from the list of items
        if item in self.itemsOnFloor:
            self.itemsOnFloor.remove(item)

    '''
    move the room a step into some direction
    '''
    def moveDirection(self,direction,force=1,initialMovement=True,movementBlock=set()):
        # move items the room collided with
        # bad code: crashes when moved items were destroyed already 
        if initialMovement:
            # collect the things that would be affected by the movement
            movementBlock = set()
            movementBlock.add(self)
            self.getAffectedByMovementDirection(direction,force=force,movementBlock=movementBlock)

            # calculate total resistance against beeing moved
            totalResistance = 0
            for thing in movementBlock:
                totalResistance += thing.getResistance()

            # refuse to move 
            if totalResistance > force:
                messages.append("*CLUNK*")
                return

            # move affected items
            for thing in movementBlock:
                if not thing == self:
                    thing.moveDirection(direction,initialMovement=False)
        
        # actually move the room
        self.terrain.moveRoomDirection(direction,self)
        messages.append("*RUMBLE*")

    '''
    get the things that would be afftected by a room movement
    '''
    def getAffectedByMovementDirection(self,direction,force=1,movementBlock=set()):

        # gather things that would be affected on terrain level
        self.terrain.getAffectedByRoomMovementDirection(self,direction,force=force,movementBlock=movementBlock)

        # gather things chained to the room
        for thing in self.chainedTo:
            if thing not in movementBlock:
                movementBlock.add(thing)
                thing.getAffectedByMovementDirection(direction,force=force,movementBlock=movementBlock)

        return movementBlock

    '''
    move a character into some direction within or out of a room
    '''
    def moveCharacterDirection(self,character,direction):

        # check whether movement is contained in the room
        innerRoomMovement = True
        if direction == "south" and character.yPosition == self.sizeY-1:
            innerRoomMovement = False
        elif direction == "north" and not character.yPosition:
            innerRoomMovement = False
        elif direction == "west" and not character.xPosition:
            innerRoomMovement = False
        elif direction == "east" and character.xPosition == self.sizeX-1:
            innerRoomMovement = False

        # move inside the room
        if innerRoomMovement:
            # move character
            newPosition = [character.xPosition,character.yPosition]
            if direction == "south":
                newPosition[1] += 1
            elif direction == "north":
                newPosition[1] -= 1
            elif direction == "west":
                newPosition[0] -= 1
            elif direction == "east":
                newPosition[0] += 1
            else:
                debugMessages.append("invalid movement direction")
            return self.moveCharacter(character,tuple(newPosition))
        
        # move onto terrain
        newYPos = character.yPosition+character.room.yPosition*15+character.room.offsetY
        newXPos = character.xPosition+character.room.xPosition*15+character.room.offsetX
        if direction == "south":
            newYPos += 1
        elif direction == "north":
            newYPos -= 1
        elif direction == "west":
            newXPos -= 1
        elif direction == "east":
            newXPos += 1
        else:
            debugMessages.append("invalid movement direction")
        self.removeCharacter(character)
        self.terrain.addCharacter(character,newXPos,newYPos)
        return

    '''
    move a character to a new position within room
    '''
    def moveCharacter(self,character,newPosition):

        # check if target position can be walked on
        if newPosition in self.itemByCoordinates:
            for item in self.itemByCoordinates[newPosition]:
                if not item.walkable:
                    return item

        # teleport character to new position
        character.xPosition = newPosition[0]
        character.yPosition = newPosition[1]

        character.changed()
        return None

    '''
    advance the room to current tick
    '''
    def applySkippedAdvances(self):
        while self.delayedTicks > 0:
            for character in self.characters:
                character.advance()
            self.delayedTicks -= 1

    '''
    add an event to internal structure
    bad code: should be in extra class
    '''
    def addEvent(self,event):
        index = 0
        for existingEvent in self.events:
            if event.tick < existingEvent.tick:
                break
            index += 1
        self.events.insert(index,event)

    '''
    remove an event from internal structure
    bad code: should be in extra class
    '''
    def removeEvent(self,event):
        self.events.remove(event)

    '''
    remove items of a certain type from internal structure
    bad code: should be in extra class
    bad code: this is no real good use case
    '''
    def removeEventsByType(self,eventType):
        for event in self.events:
            if type(event) == eventType:
                self.events.remove(event)

    '''
    advance the room one step
    '''
    def advance(self):

        # change own state
        self.timeIndex += 1
        self.requestRedraw()

        # log events that were not handled properly
        while self.events and self.timeIndex >  self.events[0].tick:
            event = self.events[0]
            debugMessages.append("something went wrong and event"+str(event)+"was skipped")
            self.events.remove(event)

        # handle events
        while self.events and self.timeIndex == self.events[0].tick:
            event = self.events[0]
            event.handleEvent()
            self.events.remove(event)

        # do next step new
        # bad code: sneakily diabled the mechanism for delaying calculations
        if not self.hidden or 1 == 1:
            # redo delayed calculation
            if self.delayedTicks > 0:
                self.applySkippedAdvances()
            
            # advance each character
            for character in self.characters:
                character.advance()
        # do next step later
        else:
            self.delayedTicks += 1
    
'''
the machine room used in the tutorial
bad pattern: should be abstracted
bad code: name and classname do not agree
'''
class TutorialMachineRoom(Room):
    '''
    create room and add special items
    '''
    def __init__(self,xPosition=0,yPosition=1,offsetX=4,offsetY=0,desiredPosition=None,creator=None):
        roomLayout = """
X#XX$XXX#X
X#Pv vID#X
X#......#X
X .@@  . X
X .HHHH. X
X ...... X
XFFFFFFFFX
XOOOOOOOOX
X#########
XXXXXXXXXX
"""
        super().__init__(roomLayout,xPosition,yPosition,offsetX,offsetY,desiredPosition,creator=creator)
        self.name = "Boilerroom"

        # generate special items
        self.lever1 = src.items.Lever(1,5,"engine control",creator=self)
        self.lever2 = src.items.Lever(8,5,"boarding alarm",creator=self)
        coalPile1 = src.items.Pile(8,3,"coal Pile1",src.items.Coal,creator=self)
        coalPile2 = src.items.Pile(8,4,"coal Pile2",src.items.Coal,creator=self)
        coalPile3 = src.items.Pile(1,3,"coal Pile1",src.items.Coal,creator=self)
        coalPile4 = src.items.Pile(1,4,"coal Pile2",src.items.Coal,creator=self)

        # actually add items
        self.addItems([self.lever1,self.lever2,coalPile1,coalPile2,coalPile3,coalPile4])

        self.furnaceQuest = None

        # save initial state and register
        self.initialState = self.getState()
        loadingRegistry.register(self)

    '''
    move from training to mocked up day to day activity
    bad code: this should happen in story
    '''
    def endTraining(self):

        '''
        event for changing the requirements regulary
        '''
        class ChangeRequirements(object):
            
            '''
            state initialization
            '''
            def __init__(subself,tick):
                subself.tick = tick
                self.loop = [0,1,2,7,4,3,5,6]

            '''
            change the requirement and shedule next event
            '''
            def handleEvent(subself):
                # change the requirement
                index = self.loop.index(self.desiredSteamGeneration)
                index += 1
                if index < len(self.loop):
                    messages.append("*comlink*: changed orders. please generate "+str(self.loop[index])+" power")
                    self.desiredSteamGeneration = self.loop[index]
                else:
                    self.desiredSteamGeneration = self.loop[0]
                    
                # shedule more changes
                self.changed()
                self.addEvent(ChangeRequirements(self.timeIndex+50))

        # add production requirement and shedule changes
        self.desiredSteamGeneration = 0
        self.changed()
        self.addEvent(ChangeRequirements(self.timeIndex+20))
        
    '''
    handle changed steam production/demand
    '''
    def changed(self,tag="default",info=None):
        super().changed(tag,info)

        # notify vat
        # bad code: vat should listen
        if self.terrain:
            self.terrain.tutorialVatProcessing.recalculate()

        # bad code: should hav an else branch
        if self.desiredSteamGeneration:
            # reset quest for firing the furnaces
            if not self.desiredSteamGeneration == self.steamGeneration:
                # reset order for firering the furnaces
                if self.secondOfficer:
                    if self.furnaceQuest:
                        self.furnaceQuest.deactivate()
                        self.furnaceQuest.postHandler()
                    self.furnaceQuest = src.quests.KeepFurnacesFiredMeta(self.furnaces[:self.desiredSteamGeneration])
                    self.secondOfficer.assignQuest(self.furnaceQuest,active=True)
            # acknowledge success
            else:
                # bad pattern: tone is way too happy
                messages.append("we did it! "+str(self.desiredSteamGeneration)+" instead of "+str(self.steamGeneration))

'''
a room to waste cpu power. used for performance testing
bad code: does not actually work
'''
class CpuWasterRoom(Room):
    '''
    create room and add patroling npcs
    '''
    def __init__(self,xPosition,yPosition,offsetX,offsetY,creator=None):
        self.roomLayout = """
XX$XXXXXXX
Xv vD????X
X?......PX
X?.PPPP.PX
X?.????.#X
X?.???P.#X
X?.?X??.#X
X?......#X
X? XXXXX#X
XXXXXXXXXX
"""
        super().__init__(self.roomLayout,xPosition,yPosition,offsetX,offsetY,desiredPosition=None,creator=creator)
        self.name = "CpuWasterRoom"

        '''
        add a patrolling npc
        '''
        def addNPC(x,y):
            # generate quests
            # bad code: replace with patrol quest since it's actually bugging
            quest1 = src.quests.MoveQuestMeta(self,2,2,creator=self)
            quest2 = src.quests.MoveQuestMeta(self,2,7,creator=self)
            quest3 = src.quests.MoveQuestMeta(self,7,7,creator=self)
            quest4 = src.quests.MoveQuestMeta(self,7,2,creator=self)
            quest1.followUp = quest2
            quest2.followUp = quest3
            quest3.followUp = quest4

            # add npc
            npc = characters.Character(xPosition=x,yPosition=y,creator=self,seed=self.yPosition+3*x+self.offsetY+4*y)
            self.addCharacter(npc,x,y)
            npc.room = self
            npc.assignQuest(quest1)
            return npc

        # add a bunch of npcs
        addNPC(2,2)
        addNPC(3,2)
        addNPC(4,2)
        addNPC(5,2)
        addNPC(6,2)
        addNPC(7,2)
        addNPC(7,3)
        addNPC(7,4)
        addNPC(7,5)
        addNPC(7,6)
        
        self.initialState = self.getState()
        loadingRegistry.register(self)

'''
the living space for soldiers
'''
class InfanteryQuarters(Room):
    '''
    create room
    '''
    def __init__(self,xPosition,yPosition,offsetX,offsetY,desiredPosition=None,creator=None):
        self.roomLayout = """
XX$X&&XXXXX
XX PPPPPPXX
X@.......DX
X'.''@''.IX
X'.'' ''.|X
X'.'' ''.|X
X'.'' ''.IX
X .......DX
XXXXXXXXXXX
"""
        super().__init__(self.roomLayout,xPosition,yPosition,offsetX,offsetY,desiredPosition,creator=creator)
        self.name = "Infanteryquarters"

        # make personal military personal
        self.firstOfficer.isMilitary = True
        self.secondOfficer.isMilitary = True
        self.onMission = False

        # set up monitoring for doors
        for item in self.itemsOnFloor:

            # ignore non doors
            if not isinstance(item,src.items.Door):
                continue

            thisRoundsItem = item # nontrivial: this forces a different namespace each run of the loop

            '''
            scold non military personal opening the door and close it again
            '''
            def handleDoorOpened():

                # ensure the rooms personal doesn't scold itself
                # bad code: doesn't actually check who opens the door
                if self.onMission:
                    return

                # only to something if door is open
                if not thisRoundsItem.walkable:
                    return

                # scold/punish the player
                # bad code: assumes the player opened the door
                messages.append(self.firstOfficer.name+"@"+self.secondOfficer.name+": close the door")
                mainChar.revokeReputation(amount=5,reason="disturbing a military area")
                messages.append(self.firstOfficer.name+": military area. Do not enter.")

                # make second officer close the door and return to start position
                quest = src.quests.MoveQuestMeta(self,5,3,creator=self)
                self.secondOfficer.assignQuest(quest,active=True)
                quest = src.quests.ActivateQuestMeta(thisRoundsItem,creator=self)
                self.secondOfficer.assignQuest(quest,active=True)

            # start watching door
            item.addListener(handleDoorOpened)

        '''
        kill non miltary personal entering the room
        '''
        def enforceMilitaryRestriction(character):
            # do nothing if character is military
            if character.isMilitary:
                return

            # make senćond officer kill the intruder
            quest = src.quests.MurderQuest(character,creator=self)
            self.secondOfficer.assignQuest(quest,active=True)

            # show fluff
            messages.append(self.firstOfficer.name+"@"+self.secondOfficer.name+": perimeter breached. neutralize threat.")

            # punish player
            character.revokeReputation(amount=100,reason="breaching a military area")

            '''
            stop running after character left the room
            '''
            def abort(characterLeaving):
                # check it the target left the room
                if not characterLeaving == character:
                    return

                # show fluff
                messages.append(self.firstOfficer.name+"@"+self.secondOfficer.name+": stop persuit. return to position.")

                # remove self from listeners
                self.delListener(abort,"left room")

                # remove kill quest
                # bad code: actually just removes the first quest
                quest = self.secondOfficer.quests[0]
                quest.deactivate()
                self.secondOfficer.quests.remove(quest)

                # make officer move back to position
                quest = src.quests.MoveQuestMeta(self,5,3,creator=self)
                self.secondOfficer.assignQuest(quest,active=True)

            # make second officer kill character
            quest = src.quests.MurderQuest(character,creator=self)
            self.secondOfficer.assignQuest(quest,active=True)

            # try make character kill self
            quest = src.quests.MurderQuest(character,creator=self)
            character.assignQuest(quest,active=True)

            # watch for character leaving the room
            self.addListener(abort,"left room")

        # watch for character entering the room
        self.addListener(enforceMilitaryRestriction,"entered room")
    
    '''
    kill characters wandering the terrain without floor permit
    '''
    def enforceFloorPermit(self,character):
        # do nothing if character has floor permit
        if character.hasFloorPermit:
            return

        # show fluff
        # bad code: produces an anouncment for each room
        messages.append("O2 military please enforce floor permit")

        # make second officer move back to position after kill
        quest = src.quests.MoveQuestMeta(self,5,3,creator=self)
        self.secondOfficer.assignQuest(quest,active=True)

        # make second officer kill character
        quest = src.quests.MurderQuest(character,creator=self)
        self.secondOfficer.assignQuest(quest,active=True)

        # try to make second kill self
        quest = src.quests.MurderQuest(character,creator=self)
        character.assignQuest(quest,active=True)
        self.onMission = True

'''
the room where raw goo is processed into eatable form
bad code: has no actual function yet
'''
class VatProcessing(Room):
    '''
    create room and add special item
    '''
    def __init__(self,xPosition,yPosition,offsetX,offsetY,desiredPosition=None,creator=None):
        self.roomLayout = """
XXXXXXXXXX
XaaaaaaaaX
#prqqrqqsX
XazayzayzX
XauwauwxtX
XaaayaayaX
#psBBBBBBX
Xmhm ...DX
Xmmmv.v.IX
XXXXX$XXXX
"""
        super().__init__(self.roomLayout,xPosition,yPosition,offsetX,offsetY,desiredPosition,creator=creator)

        # add special items
        self.gooDispenser = src.items.GooDispenser(6,7,creator=self)
        self.addItems([self.gooDispenser])
        self.name = "vat processing"

        # save initial state and register
        self.initialState = self.getState()
        loadingRegistry.register(self)

    '''
    recalculate sprayer state
    bad code: sprayer should be listening
    '''
    def recalculate(self):
        for spray in self.sprays:
            spray.recalculate()

'''
the room where organic material is fermented to raw goo
bad code: has no actual function yet
'''
class VatFermenting(Room):
    '''
    create room and set some state
    '''
    def __init__(self,xPosition,yPosition,offsetX,offsetY,desiredPosition=None,creator=None):
        self.roomLayout = """
XXXXXXXXXX
X   b jjjX
X  ......X
X b.b bb.X
X .. c b.X
X .b  j .X
X .. b b.X
X@b. ....X
## ...v ##
XXXXX$XXXX
"""
        super().__init__(self.roomLayout,xPosition,yPosition,offsetX,offsetY,desiredPosition,creator=creator)
        self.isContainment = True
        self.floorDisplay = displayChars.acids
        self.name = "Vat fermenting"

        # save initial state and register
        self.initialState = self.getState()
        loadingRegistry.register(self)

'''
the armor plates of a mech
'''
class MechArmor(Room):
    '''
    create room
    '''
    def __init__(self,xPosition,yPosition,offsetX,offsetY,desiredPosition=None,creator=None):
        self.roomLayout = """
XXXXXXXXXXXXXXX
XX X X X X X XX
X X X X X X X X
XXXXXXXXXXXXXXX
XX X X X X X XX
XXXXXXXXXXXXXXX
XX X X X X X XX
X X X X X X X X
XXXXXXXXXXXXXXX
XX X X X X X XX
X X X X X X X X
XXXXXXXXXXXXXXX
XX X X X X X XX
X X X X.X X X.X
XXXXXXX$XXXXXXX
"""
        super().__init__(self.roomLayout,xPosition,yPosition,offsetX,offsetY,desiredPosition,creator=creator)
        self.floorDisplay = [displayChars.nonWalkableUnkown]
        self.name = "MechArmor"

'''
a mini mech to drive around with. including boiler and coal storage and furnace fireing npc
'''
class MiniMech(Room):
    '''
    create the room and add the npc
    '''
    def __init__(self,xPosition,yPosition,offsetX,offsetY,desiredPosition=None,creator=None):
        self.roomLayout = """
XX$XXX
XD..@X
X  . X
XOF.PX
Xmm.PX
XXXXXX
"""
        super().__init__(self.roomLayout,xPosition,yPosition,offsetX,offsetY,desiredPosition,creator=creator)
        self.floorDisplay = [displayChars.nonWalkableUnkown]
        self.engineStrength = 0
        self.name = "MiniMech"

        # add npc
        self.npc = characters.Character(xPosition=3,yPosition=3,creator=self,seed=self.yPosition+3*3+self.offsetY+4*12)
        self.addCharacter(self.npc,3,3)
        self.npc.room = self

        quest = None

        # add dialog options
        self.npc.basicChatOptions.append({"dialogName":"fire the furnaces","chat":chats.StartChat})
        self.initialState = self.getState()
        loadingRegistry.register(self)

    '''
    recalculate engine strength
    bad code: should be recalculate
    '''
    def changed(self,tag="default",info=None):
        super().changed(tag,info)
        self.engineStrength = 250*self.steamGeneration

'''
a room sized base for small off mech missions
bad code: serves no real function yet
'''
class MiniBase(Room):
    '''
    create room and add special items
    '''
    def __init__(self,xPosition,yPosition,offsetX,offsetY,desiredPosition=None,creator=None):
        self.roomLayout = """
XXXXXXXXXXXXX
X           X
X           X
X           X
X           X
X          vX
X  .........$
X          vX
X           X
X           X
X           X
X           X
XXXXXXXXXXXXX
"""
        super().__init__(self.roomLayout,xPosition,yPosition,offsetX,offsetY,desiredPosition,creator=creator)
        self.artwork = src.items.ProductionArtwork(4,1,creator=creator)
        self.compactor = src.items.ScrapCompactor(6,1,creator=creator)
        self.addItems([self.artwork,self.compactor])
        self.initialState = self.getState()
        loadingRegistry.register(self)

'''
a lab for behaviour testing
bad code: is basically not implemented yet
bad code: is misused as a target/source for transportation jobs
'''
class ChallengeRoom(Room):
    '''
    create room and add special items
    '''
    def __init__(self,xPosition,yPosition,offsetX,offsetY,desiredPosition=None,creator=None,seed=0):
        self.roomLayout = """
XXXXXXXXXX
X XX  @  X
XXXX.... X
X XX.  . X
XXXX.  . X
X XX.  . X
XXXX.... X
X XX     X
XXXX   @ X
X        X
X        X
X        X
$        X
XXXXXXXXXX
"""
        super().__init__(self.roomLayout,xPosition,yPosition,offsetX,offsetY,desiredPosition,creator=creator)

        # bad code: the markers are not used anywhere
        self.bean = src.items.MarkerBean(4,2,creator=self)
        beanPile = src.items.Pile(4,1,"markerPile",src.items.MarkerBean,creator=self)
        self.addItems([self.bean,beanPile])

        self.name = "Challenge"

        # unbolt all items in the room
        for item in self.itemsOnFloor:
            if item.xPosition == 0 or item.yPosition == 0:
               continue
            if item.xPosition == self.sizeX-1 or item.yPosition == self.sizeY-1:
               continue
            item.bolted = False

        self.firstOfficer.basicChatOptions.append({"dialogName":"I need to leave this room, can you help?","chat":chats.ConfigurableChat,"params":{
                "text":"yes",
                "info":[]}})
        self.secondOfficer.basicChatOptions.append({"dialogName":"I need to leave this room, can you help?","chat":chats.ConfigurableChat,"params":{
                "text":"I dont know how to help you with this",
                "info":[]
            }})

        firstOfficerDialog = {"dialogName":"Do you need more equipment?","chat":chats.ConfigurableChat,"params":{
                "text":"yes",
                "info":[
                    ]
            }}
        firstOfficerDialog["params"]["info"].append({"name":"I want to use my tokens","text":"Done","type":"text","trigger":{"container":self,"method":"removeTokensFirstOfficer"}})
        self.firstOfficer.basicChatOptions.append(firstOfficerDialog)

        secondOfficerDialog = {"dialogName":"Do you need more equipment?","chat":chats.ConfigurableChat,"params":{
                "text":"yes",
                "info":[
                    ]
            }}

        self.secondOfficerRemovesPipes = False
        self.secondOfficerRemovesGooFlasks = False
        self.secondOfficerRemovesTokens = False

        self.secondOfficerRemovesPipes = True
        if seed%3 == 2 or seed%7 == 0:
            self.secondOfficerRemovesGooFlasks = True
        if seed%2 == 0 or seed%5 == 2:
            self.secondOfficerRemovesTokens = True

        if self.secondOfficerRemovesPipes:
            secondOfficerDialog["params"]["info"].append({"name":"Please take my pipes","text":"Offer accepted","type":"text","trigger":{"container":self,"method":"removePipesSecondOfficer"}})
        if self.secondOfficerRemovesGooFlasks:
            secondOfficerDialog["params"]["info"].append({"name":"Please take my goo flasks","text":"Offer accepted","type":"text","trigger":{"container":self,"method":"removeGooFlaskSecondOfficer"}})
        if self.secondOfficerRemovesTokens:
            secondOfficerDialog["params"]["info"].append({"name":"I want to use my tokens","text":"Done","type":"text","trigger":{"container":self,"method":"removeTokensSecondOfficer"}})
        secondOfficerDialog["params"]["info"].append({"name":"Take anything you like","text":"Offer accepted","type":"text","trigger":{"container":self,"method":"removeEverythingSecondOfficer"}})
        self.secondOfficer.basicChatOptions.append(secondOfficerDialog)

        items = []
        yPosition = 1
        item = src.items.Furnace(1,yPosition,creator=self)
        items.append(item)
        yPosition += 2
        if seed%5 == 3:
            item = src.items.Furnace(1,yPosition,creator=self)
            items.append(item)
            yPosition += 2
        if seed%3 == 1:
            item = src.items.Furnace(1,yPosition,creator=self)
            items.append(item)
            yPosition += 2
        if seed%2 == 1:
            item = src.items.Furnace(1,yPosition,creator=self)
            items.append(item)
            yPosition += 2
        self.addItems(items)

        positions = []
        self.labyrinthWalls = []
        counter = 0
        xPosition = 5
        yPosition = 3
        numItems = 15+seed%17
        while counter < numItems:
            xPosition = 1+(counter*2+seed+yPosition)%20%8
            yPosition = 9+(counter+seed+xPosition)%17%4

            if counter in [2,5]:
                item = src.items.GooFlask(xPosition,yPosition,creator=self)
                item.charges = 1
            if (xPosition,yPosition) in positions:
                seed = seed+1
                continue
            else:
                positions.append((xPosition,yPosition))
            if counter in [1]:
                item = src.items.GooFlask(xPosition,yPosition,creator=self)
                item.charges = 1
            elif counter%5 == 1:
                if counter%3 == 0:
                    token = src.items.Token(xPosition,yPosition,creator=self)
                    self.addItems([token])
                item = src.items.Pipe(xPosition,yPosition,creator=self)
            else:
                if counter%7 == 5:
                    token = src.items.Token(xPosition,yPosition,creator=self)
                    self.addItems([token])
                item = src.items.Wall(xPosition,yPosition,creator=self)
            item.bolted = False
            self.labyrinthWalls.append(item)
            counter += 1
        self.addItems(self.labyrinthWalls)

        numItems = seed%9
        counter = 0
        while (counter < numItems):
            item = src.items.GooFlask(None,None,creator=self)
            self.secondOfficer.inventory.append(item)
            counter += 1

        # save initial state and register
        self.initialState = self.getState()
        loadingRegistry.register(self)

    def removePipesSecondOfficer(self):
        toRemove = []
        for item in mainChar.inventory:
            if isinstance(item,src.items.Pipe):
                toRemove.append(item)
        for item in toRemove:
            if len(self.secondOfficer.inventory) < 10:
                mainChar.inventory.remove(item)
                self.secondOfficer.inventory.append(item)

    def removeGooFlaskSecondOfficer(self):
        toRemove = []
        for item in mainChar.inventory:
            if isinstance(item,src.items.GooFlask):
                toRemove.append(item)
        for item in toRemove:
            if len(self.secondOfficer.inventory) < 10:
                mainChar.inventory.remove(item)
                self.secondOfficer.inventory.append(item)

    def removeTokensFirstOfficer(self):
        toRemove = []
        numTokens = 0
        for item in mainChar.inventory:
            if isinstance(item,src.items.Token):
                toRemove.append(item)
                numTokens += 1
        for item in toRemove:
            if len(self.firstOfficer.inventory) < 10:
                mainChar.inventory.remove(item)
                self.firstOfficer.inventory.append(item)

    def removeTokensSecondOfficer(self):
        toRemove = []
        numTokens = 0
        for item in mainChar.inventory:
            if isinstance(item,src.items.Token):
                toRemove.append(item)
                numTokens += 1
        for item in mainChar.inventory:
            if numTokens == 0:
                break
            if isinstance(item,src.items.Wall):
                toRemove.append(item)
                numTokens -= 1
        for item in toRemove:
            if len(self.secondOfficer.inventory) < 10:
                mainChar.inventory.remove(item)
                self.secondOfficer.inventory.append(item)

    def removeEverythingSecondOfficer(self):
        if self.secondOfficerRemovesPipes:
            self.removePipesSecondOfficer()
        if self.secondOfficerRemovesGooFlasks:
            self.removeGooFlaskSecondOfficer()
        if self.secondOfficerRemovesTokens:
            self.removeTokensSecondOfficer()

'''
a lab for behaviour testing
bad code: is basically not implemented yet
bad code: is misused as a target/source for transportation jobs
'''
class LabRoom(Room):
    '''
    create room and add special items
    '''
    def __init__(self,xPosition,yPosition,offsetX,offsetY,desiredPosition=None,creator=None):
        self.roomLayout = """
XXXXXXXXXX
X     @@ X
X ...... X
X .    . X
X .    . X
$ .    . X
X .    . X
X ...... X
X        X
X########X
XXXXXXXXXX
XOOOOOOOOX
XFFFFFFFFX
XXXXXXXXXX
"""
        super().__init__(self.roomLayout,xPosition,yPosition,offsetX,offsetY,desiredPosition,creator=creator)

        # bad code: the markers are not used anywhere
        bean = src.items.MarkerBean(1,2,creator=self)
        beanPile = src.items.Pile(1,1,"markerPile",src.items.MarkerBean,creator=self)
        self.addItems([bean,beanPile])

        self.name = "Lab"

        # unbolt all items in the room
        for item in self.itemsOnFloor:
            if item.xPosition == 0 or item.yPosition == 0:
               continue
            if item.xPosition == self.sizeX-1 or item.yPosition == self.sizeY-1:
               continue
            item.bolted = False

        # save initial state and register
        self.initialState = self.getState()
        loadingRegistry.register(self)

'''
cargo storage for tightly packing items
'''
class CargoRoom(Room):
    '''
    create room, set storage order and fill with items
    '''
    def __init__(self,xPosition,yPosition,offsetX,offsetY,desiredPosition=None,itemTypes=[src.items.Pipe,src.items.Wall,src.items.Furnace,src.items.Boiler],amount=80,creator=None):
        self.roomLayout = """
XXXXXXXXXX
X        X
X       .$
X        X
X        X
X        X
X        X
X        X
X        X
X        X
X        X
X        X
X        X
XXXXXXXXXX
"""
        super().__init__(self.roomLayout,xPosition,yPosition,offsetX,offsetY,desiredPosition,creator=creator)
        self.floorDisplay = [displayChars.nonWalkableUnkown]
        self.name = "CargoRoom"

        # generate items with the supplied item types
        self.storedItems = []
        counter = 0
        length = len(itemTypes)
        for i in range(1,amount):
            i = i+i%3+i%10*2
            if i%2:
                counter += 1
            elif i%4:
                counter += 2
            elif i%8:
                counter += 3
            else:
                counter += 4
            self.storedItems.append(itemTypes[counter%length](creator=self))

        # determine in what order storage space should be used
        counter = 0
        self.storageSpace = []
        for j in range(1,2):
            for i in range(1,self.sizeX-1):
                self.storageSpace.append((i,j))
        j = self.sizeY-2
        while j > 1:
            for i in range(1,self.sizeX-1):
                self.storageSpace.append((i,j))
            j -= 1

        # map items to storage spaces
        counter = 0
        for item in self.storedItems:
            item.xPosition = self.storageSpace[counter][0]
            item.yPosition = self.storageSpace[counter][1]
            item.mayContainMice = True
            item.bolted = False
            counter += 1

        # add mice inhabiting the room on about every fifth room
        if (self.xPosition + yPosition*2 - offsetX - offsetY)%5 == 0:
            # place mice
            mice = []
            mousePositions = [(2,2),(2,4),(4,2),(4,4),(8,3)]
            for mousePosition in mousePositions:
                mouse = characters.Mouse(creator=self)
                self.addCharacter(mouse,mousePosition[0],mousePosition[1])
                mice.append(mouse)

            '''
            kill characters entering the room
            bad code: should be a quest
            '''
            def killInvader(character):
                for mouse in mice:
                    quest = src.quests.MurderQuest(character,creator=self)
                    mouse.assignQuest(quest,active=True)
                '''
                stop hunting characters that left the room
                '''
                def vanish(characterLeaving):
                    # check whether the correct character left the room
                    if not character == characterLeaving:
                        return

                    counter = 0
                    for mouse in mice:
                        # stop hunting the character
                        # bad code: assumes first quest is kill quest
                        mouse.quests[0].deactivate()
                        mouse.quests.remove(mouse.quests[0])
                        
                        # move back to position
                        quest = src.quests.MoveQuestMeta(self,mousePositions[counter][0],mousePositions[counter][1],creator=self)
                        mouse.assignQuest(quest,active=True)
                        counter += 1

                # watch for characters leaving the room
                self.addListener(vanish,"left room")

            # watch for characters entering the room
            self.addListener(killInvader,"entered room")

        # actually add the items
        self.addItems(self.storedItems)

        # save initial state and register
        self.initialState = self.getState()
        loadingRegistry.register(self)

'''
storage for storing items in an accessible way
'''
class StorageRoom(Room):
    '''
    create room, set storage order 
    '''
    def __init__(self,xPosition,yPosition,offsetX,offsetY,desiredPosition=None,creator=None):
        self.roomLayout = """
XXXXXXXXXX
X        X
X........$
X        X
X        X
X        X
X        X
X        X
X        X
X        X
X        X
X        X
X        X
XXXXXXXXXX
"""
        self.storedItems = []
        self.storageSpace = []

        super().__init__(self.roomLayout,xPosition,yPosition,offsetX,offsetY,desiredPosition,creator=creator)
        self.floorDisplay = [displayChars.nonWalkableUnkown]
        self.name = "StorageRoom"

        # determine what positions should be used for storage
        counter = 0
        for j in range(1,2):
            for i in range(1,self.sizeX-1):
                self.storageSpace.append((i,j))
        i = self.sizeX-2
        offset = 2
        while i > 1:
            for j in range(3,self.sizeY-1):
                self.storageSpace.append((i,j))
            i -= offset
            if offset == 1:
                offset = 2
            else:
                offset = 1

        # map items on storage space
        # bad code: no items to place
        counter = 0
        for item in self.storedItems:
            item.xPosition = self.storageSpace[counter][0]
            item.yPosition = self.storageSpace[counter][1]
            item.bolted = False
            counter += 1

        # actually add the items
        self.addItems(self.storedItems)
        self.initialState = self.getState()
        loadingRegistry.register(self)

    '''
    use specialised pathfinding
    bad code: doesn't work properly
    '''
    def calculatePath(self,x,y,dstX,dstY,walkingPath):
        # handle impossible state
        if dstY == None or dstX == None:
            debugMessages.append("pathfinding without target")
            return []

        path = []

        # go to secondary path
        if not y in (1,2) and x in (2,5,8,3,6):
            if x in (2,5,8):
                x = x-1
            elif (x) in (3,6):
                x = x+1
            path.append((x,y))

        # go to main path
        while y<2:
            y = y+1
            path.append((x,y))
        while y>2:
            y = y-1
            path.append((x,y))

        # go main path to secondary path
        tmpDstX = dstX
        if dstX in (2,5,8,3,6) and not dstY in (1,2):
            if dstX in (2,5,8):
                tmpDstX = dstX-1
            elif dstX in (3,6):
                tmpDstX = dstX+1
        while x<tmpDstX:
            x = x+1
            path.append((x,y))
        while x>tmpDstX:
            x = x-1
            path.append((x,y))

        # go to end of secondary path
        while y<dstY:
            y = y+1
            path.append((x,y))
        while y>dstY:
            y = y-1
            path.append((x,y))

        # go to end of path
        while x<dstX:
            x = x+1
            path.append((x,y))
        while x>dstX:
            x = x-1
            path.append((x,y))
        import src.gameMath as gameMath
        return gameMath.removeLoops(path)

    '''
    add items and manage storage spaces
    '''
    def addItems(self,items):
        super().addItems(items)
        for item in items:
            pos = (item.xPosition,item.yPosition)
            if pos in self.storageSpace:
                self.storedItems.append(item)
                self.storageSpace.remove(pos)

    '''
    remove item and manage storage spaces
    '''
    def removeItem(self,item):
        if item in self.storedItems:
            self.storedItems.remove(item)
            pos = (item.xPosition,item.yPosition)
            self.storageSpace.append(pos)
        super().removeItem(item)

'''
the room where characters are grown and born
'''
class WakeUpRoom(Room):
    '''
    create room and add special items
    '''
    def __init__(self,xPosition,yPosition,offsetX,offsetY,desiredPosition=None,creator=None):
        self.roomLayout = """
XXXXXXXX
Xö    vX
XÖ ... $
XÖ . .vX
XÖ . .@X
XÖ . . X
XÖ . . X
XÖ . . X
XÖ ... X
XÖ     X
XXXXXXXX
"""
        super().__init__(self.roomLayout,xPosition,yPosition,offsetX,offsetY,desiredPosition,creator=creator)
        self.name = "WakeUpRoom"

        # generate special items
        self.lever1 = src.items.Lever(3,1,"training lever",creator=self)
        self.objectDispenser = src.items.OjectDispenser(4,1,creator=self)
        self.gooDispenser = src.items.GooDispenser(5,9,creator=self)
        self.furnace = src.items.Furnace(4,9,creator=self)
        self.pile = src.items.Pile(6,9,creator=self)

        '''
        create goo flask
        '''
        def activateDispenser(dispenser):
            self.objectDispenser.dispenseObject()

        # connect lever
        self.lever1.activateAction = activateDispenser

        # actually add items
        self.addItems([self.lever1,self.gooDispenser,self.objectDispenser,self.furnace,self.pile])

        # watch growth tanks and door
        # bad code: should be a quest
        for item in self.itemsOnFloor:
            if isinstance(item,src.items.GrowthTank):
                def forceNewnamespace(var): # HACK: brute force approach to get a new namespace
                    def callHandler(char):
                        self.handleUnexpectedGrowthTankActivation(char,var)
                    return callHandler
                item.addListener(forceNewnamespace(item),"activated")
            if isinstance(item,src.items.Door):
                item.addListener(self.handleDoorOpening,"activated")

        # start spawning hoppers periodically
        self.addEvent(events.EndQuestEvent(8000,{"container":self,"method":"spawnNewHopper"},creator=self))

        # save initial state and register
        self.initialState = self.getState()
        loadingRegistry.register(self)

    '''
    warn character about leaving the room
    '''
    def handleDoorOpening(self,character):
        # should be a guard
        if self.firstOfficer and not character.hasFloorPermit:
            messages.append(self.firstOfficer.name+": moving through this door will be your death.")
            character.revokeReputation(amount=1,reason="beeing impatient")
    
    '''
    move player to vat
    '''
    def handleUnexpectedGrowthTankActivation(self,character,item):
        # bad pattern; player only function
        if not character == mainChar:
            return

        # only act if there is somebody to act
        if not self.firstOfficer:
            return

        if not item.filled:
            return

        # scold player
        messages.append(self.firstOfficer.name+": Now will have to take care of this body.")
        messages.append(self.firstOfficer.name+": Please move on to your next assignment immediatly.")

        # remove all quests
        for quest in mainChar.quests:
            quest.deactivate()
        mainChar.quests = []

        # cancel cinematics
        # bad code: should happen in a more structured way
        cinematics.cinematicQueue = []

        # give floor permit
        character.hasFloorPermit = True

        # start vat phase
        phase = story.VatPhase()
        phase.start()

    '''
    periodically spawn new hoppers
    '''
    def spawnNewHopper(self):
        # do nothing if there is nobody to do anything
        if not self.firstOfficer:
            return

        # eject player from growth tank
        character = None
        for item in self.itemsOnFloor:
            if isinstance(item,src.items.GrowthTank):
                if item.filled:
                    character = item.eject()
                    break

        # abort if no player was generated
        if not character:
            return

        # add character as hopper
        # bad pattern: should be a story or quest
        character.wakeUp()
        character.hasFloorPermit = True
        self.terrain.waitingRoom.addAsHopper(character)

        # shedule next spawn
        self.addEvent(events.EndQuestEvent(gamestate.tick+10000,{"container":self,"method":"spawnNewHopper"},creator=self))

'''
the room where hoppers wait for jobs
'''
class WaitingRoom(Room):
    '''
    create room and add hoppers
    '''
    def __init__(self,xPosition,yPosition,offsetX,offsetY,desiredPosition=None,creator=None):
        self.roomLayout = """
XXXXXXXXXXX
X         X
X  .....  X
X  .   .  X
X  . @ .  $
X  . @ . IX
X  ..... DX
X         X
X         X
XXXXXXXXXXX
"""
        self.quests = []
        super().__init__(self.roomLayout,xPosition,yPosition,offsetX,offsetY,desiredPosition,creator=creator)
        self.name = "WaitingRoom"
        self.hoppers = []

        # add hoppers
        npc = self.fetchThroughRegistry(characters.Character(xPosition=4,yPosition=4,creator=self,seed=self.yPosition+self.offsetY+4*12))
        self.hoppers.append(npc)
        self.addCharacter(npc,2,2)
        npc = self.fetchThroughRegistry(characters.Character(xPosition=4,yPosition=5,creator=self,seed=self.yPosition+self.offsetY+4*23+30))
        self.hoppers.append(npc)
        self.addCharacter(npc,2,3)

        self.trainingItems = []
        item = src.items.Wall(1,1,creator=self)
        item.bolted = False
        self.trainingItems.append(item)
        item = src.items.Pipe(9,1,creator=self)
        item.bolted = False
        self.trainingItems.append(item)
        self.addItems(self.trainingItems)

        # assign hopper duty to hoppers
        for hopper in self.hoppers:
            self.addAsHopper(hopper)
            hopper.initialState = hopper.getState()

        # save initial state and register
        self.initialState = self.getState()
        loadingRegistry.register(self)

    '''
    add a character as hopper
    '''
    def addAsHopper(self,hopper):
        quest = src.quests.HopperDuty(self,creator=self)
        hopper.assignQuest(quest,active=True)
        hopper.addListener(self.addRescueQuest,"fallen unconcious")
        hopper.addListener(self.disposeOfCorpse,"died")

    '''
    rescue an unconcious hopper
    '''
    def addRescueQuest(self,character):
        quest = src.quests.WakeUpQuest(character,creator=self)
        quest.reputationReward = 2
        self.quests.append(quest)

    '''
    dispose of a dead hoppers corpse
    bad pattern: picking the corpse up and pretending nothing happend is not enough
    '''
    def disposeOfCorpse(self,info):
        quest = src.quests.PickupQuestMeta(info["corpse"],creator=self)
        quest.reputationReward = 1
        self.quests.append(quest)

    '''
    set internal state from dictionary
    '''
    def setState(self,state):
        super().setState(state)
        
        self.quests = []
        for questId in state["quests"]["ids"]:
             self.quests.append(src.quests.getQuestFromState(state["quests"]["states"][questId]))

    '''
    get state as dictionary
    '''
    def getState(self):
        state = super().getState()

        state["quests"] = {"ids":[],"states":{}}
        for quest in self.quests:
            state["quests"]["ids"].append(quest.id) 
            state["quests"]["states"][quest.id] = quest.getState()

        return state

    '''
    get difference between initial and current state as dictionary
    '''
    def getDiffState(self):
        state = super().getDiffState()

        state["quests"] = {"ids":[],"states":{}}
        for quest in self.quests:
            state["quests"]["ids"].append(quest.id) 
            state["quests"]["states"][quest.id] = quest.getState()

        return state

'''
a dummy for the mechs command centre
bad code: dummy only
'''
class MechCommand(Room):

    '''
    set basic attributes
    '''
    def __init__(self,xPosition,yPosition,offsetX,offsetY,desiredPosition=None,creator=None):
        self.roomLayout = """
XXXXX$XXXXX
XI        X
XI .....  X
XD .   .  X
XD .@@ .  X
XD .III.  X
XD .DDD.  X
XI .....  X
XI        X
XXXXXXXXXXX
"""
        super().__init__(self.roomLayout,xPosition,yPosition,offsetX,offsetY,desiredPosition,creator=creator)
        self.name = "Mech Command Centre"

        self.firstOfficer.name = "Cpt. "+self.firstOfficer.name

        firstOfficerDialog = {"dialogName":"Tell me more about the Commandchain","chat":chats.ConfigurableChat,"params":{
                "text":"I am the Captain and control everything that happens on this mech.\n%s is my second in command\n%s is handling logistics\n%s is coordinating the hopper\n%s is head of the military"%("","","",""),
                "info":[
                    ]
            }}
        self.firstOfficer.basicChatOptions.append(firstOfficerDialog)
        self.firstOfficer.basicChatOptions.append({"dialogName":"I want to be captain","chat":chats.CaptainChat})

'''
the place for production of tools and items
'''
class MetalWorkshop(Room):
    '''
    create room and add special items
    '''
    def __init__(self,xPosition,yPosition,offsetX,offsetY,desiredPosition=None,creator=None):
        self.roomLayout = """
XXXXXXXXXXX
XP        X
XP .....  X
XP .   .  X
XP . @ .  X
XP .   .  X
XP .....  X
XP        X
XP        X
XXXXX$XXXXX
"""
        self.quests = []
        super().__init__(self.roomLayout,xPosition,yPosition,offsetX,offsetY,desiredPosition,creator=creator)
        self.name = "MetalWorkshop"

        # add production machines
        self.artwork = src.items.ProductionArtwork(4,1,creator=self)
        self.compactor = src.items.ScrapCompactor(6,1,creator=self)
        self.addItems([self.artwork,self.compactor])

        # add some produced items
        self.producedItems = []
        item = src.items.Wall(9,4,creator=self)
        item.bolted = False
        self.producedItems.append(item)
        item = src.items.Wall(9,6,creator=self)
        item.bolted = False
        self.producedItems.append(item)
        item = src.items.Wall(9,3,creator=self)
        item.bolted = False
        self.producedItems.append(item)
        item = src.items.Wall(9,7,creator=self)
        item.bolted = False
        self.producedItems.append(item)
        item = src.items.Wall(9,2,creator=self)
        item.bolted = False
        self.producedItems.append(item)
        item = src.items.Wall(9,8,creator=self)
        item.bolted = False
        self.producedItems.append(item)
        self.addItems(self.producedItems)

        firstOfficerDialog = {"dialogName":"Do you need some help?","chat":chats.ConfigurableChat,"params":{
                "text":"no",
                "info":[
                    ]
            }}
        firstOfficerDialog["params"]["info"].append({"name":"Please give me reputation anyway.","text":"Ok","type":"text","trigger":{"container":self,"method":"dispenseFreeReputation"}})
        self.firstOfficer.basicChatOptions.append(firstOfficerDialog)

        # save initial state and register
        self.initialState = self.getState()
        loadingRegistry.register(self)

    def dispenseFreeReputation(self):
        mainChar.reputation += 100

'''
a room in the process of beeing constructed. The room itself exists but no items within
'''
class ConstructionSite(Room):
    '''
    create room and plan construction
    '''
    def __init__(self,xPosition,yPosition,offsetX,offsetY,desiredPosition=None,creator=None):
        self.roomLayout = """
XXXXXXXXXXX
X         X
X  .....  X
X  .   .  X
X  .   .  X
X  .   .  X
X  .....  X
X    @    X
X         X
XXXXX$XXXXX
"""
        self.desiredRoomlayout = """
XXXXXXXXXXX
X########XX
XXX.....##X
X#X.   .X#X
X#X. @ .##X
X#X.   .#XX
X#X.....##X
X#XXX XXX#X
X#### ####X
XXXXX$XXXXX
"""
        super().__init__(self.roomLayout,xPosition,yPosition,offsetX,offsetY,desiredPosition,creator=creator)
        self.name = "Construction Site"

        # get a map of items that need to be placed
        itemsToPlace = {}
        x = -1
        for line in self.desiredRoomlayout.split("\n"):
            if x in (-1,0,9):
                x += 1
                continue
            y = 0
            for char in line:
                if y in (0,10):
                    y += 1
                    continue
                if char == "#":
                    itemsToPlace[(x,y)] = src.items.Pipe
                if char == "X":
                    itemsToPlace[(x,y)] = src.items.Wall
                y += 1
            x += 1

        # add markers for items
        itemstoAdd = []
        for (position,itemType) in itemsToPlace.items():
            item = src.items.MarkerBean(position[1],position[0],creator=self)
            item.apply(self.firstOfficer)
            itemstoAdd.append(item)
        self.addItems(itemstoAdd)

        buildorder = []
        # task north-west corner
        x = 0
        while x < self.sizeX//2:
            y = 0
            while y < self.sizeY//2:
                buildorder.append((x,y))
                y += 1
            x += 1

        # task south-west corner
        x = self.sizeX
        while x >= self.sizeX//2:
            y = 0
            while y < self.sizeY//2:
                buildorder.append((x,y))
                y += 1
            x -= 1

        # task south-east corner
        x = self.sizeX
        while x >= self.sizeX//2:
            y = self.sizeY
            while y >= self.sizeY//2:
                buildorder.append((x,y))
                y -= 1
            x -= 1

        # task north-east corner
        x = 0
        while x < self.sizeX//2:
            y = self.sizeY
            while y >= self.sizeY//2:
                buildorder.append((x,y))
                y -= 1
            x += 1

        # bad code: buiding in the middle of the room is NIY

        # sort items in build order
        self.itemsInBuildOrder = []
        for position in buildorder:
            if position in itemsToPlace:
                self.itemsInBuildOrder.append((position,itemsToPlace[position]))
        self.itemsInBuildOrder.reverse()

        # save initial state and register
        self.initialState = self.getState()
        loadingRegistry.register(self)

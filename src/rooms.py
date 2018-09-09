import src.items as items
import src.quests as quests
import json

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
class Room(object):
    '''
    state initialization
    bad code: too many attributes
    '''
    def __init__(self,layout,xPosition,yPosition,offsetX,offsetY,desiredPosition=None,creator=None):
        # should be in extra class
        self.creationCounter = 0

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
                    # bad code: name generation should happen somewhere else
                    def getRandomName(seed1=0,seed2=None):
                        if seed2 == None:
                            seed2 = seed1+(seed1//5)
                        return names.characterFirstNames[seed1%len(names.characterFirstNames)]+" "+names.characterLastNames[seed2%len(names.characterLastNames)]
                        
                    # add default npc
                    if (not self.firstOfficer) or (not self.secondOfficer):
                        if not self.firstOfficer:
                            # add first officer
                            name = getRandomName(self.xPosition+2*self.offsetY,self.offsetX+2*self.yPosition)
                            npc = characters.Character(displayChars.staffCharactersByLetter[name[0].lower()],5,3,name=name,creator=self)
                            self.addCharacter(npc,rowCounter,lineCounter)
                            npc.terrain = self.terrain
                            self.firstOfficer = npc
                            quest = quests.RoomDuty(creator=self)
                            npc.assignQuest(quest,active=True)
                        else:
                            # add second officer
                            name = getRandomName(self.yPosition+2*self.offsetX,self.offsetY+2*self.xPosition)
                            npc = characters.Character(displayChars.staffCharactersByLetter[name[0].lower()],6,4,name=name,creator=self)
                            self.addCharacter(npc,rowCounter,lineCounter)
                            npc.terrain = self.terrain
                            self.secondOfficer = npc
                            quest = quests.RoomDuty(creator=self)
                            npc.assignQuest(quest,active=True)
                elif char in ("X","&"):
                    # add wall
                    itemsOnFloor.append(items.Wall(rowCounter,lineCounter,creator=self))
                elif char == "$":
                    # add door and mark position as entry point
                    door = items.Door(rowCounter,lineCounter,creator=self)
                    itemsOnFloor.append(door)
                    self.walkingAccess.append((rowCounter,lineCounter))
                    self.doors.append(door)
                elif char == "P":
                    # add pile and save to list
                    item = items.Pile(rowCounter,lineCounter,creator=self)
                    itemsOnFloor.append(item)
                    self.piles.append(item)
                elif char == "F":
                    # add furnace and save to list
                    item = items.Furnace(rowCounter,lineCounter,creator=self)
                    itemsOnFloor.append(item)
                    self.furnaces.append(item)
                elif char == "#":
                    # add pipe and save to list
                    item = items.Pipe(rowCounter,lineCounter,creator=self)
                    itemsOnFloor.append(item)
                    self.pipes.append(item)
                elif char == "D":
                    # add display
                    itemsOnFloor.append(items.Display(rowCounter,lineCounter,creator=self))
                elif char == "v":
                    #to be bin
                    itemsOnFloor.append(items.Item(displayChars.binStorage,rowCounter,lineCounter,creator=self))
                elif char == "O":
                    #to be pressure Tank
                    item = items.Boiler(rowCounter,lineCounter,creator=self)
                    itemsOnFloor.append(item)
                    self.boilers.append(item)
                    #itemsOnFloor.append(items.Item(displayChars.boiler_active,rowCounter,lineCounter))
                elif char == "8":
                    #to be chains
                    itemsOnFloor.append(items.Item(displayChars.chains,rowCounter,lineCounter,creator=self))
                elif char == "I":
                    #to be commlink
                    itemsOnFloor.append(items.Commlink(rowCounter,lineCounter,creator=self))
                elif char == "H":
                    # add hutch
                    # bad code: handle state some other way
                    itemsOnFloor.append(items.Hutch(rowCounter,lineCounter,creator=self))
                elif char == "'":
                    # add hutch
                    # bad code: handle state some other way
                    itemsOnFloor.append(items.Hutch(rowCounter,lineCounter,creator=self,activated=True))
                elif char == "o":
                    #to be grid
                    itemsOnFloor.append(items.Item(displayChars.grid,rowCounter,lineCounter,creator=self))
                elif char == "a":
                    #to be acid
                    item = items.Item(displayChars.acids[((2*rowCounter)+lineCounter)%5],rowCounter,lineCounter,creator=self)
                    item.walkable = True
                    itemsOnFloor.append(item)
                elif char == "b":
                    # to be foodstuffs
                    itemsOnFloor.append(items.Item(displayChars.foodStuffs[((2*rowCounter)+lineCounter)%6],rowCounter,lineCounter,creator=self))
                elif char == "m":
                    # to be machinery
                    itemsOnFloor.append(items.Item(displayChars.machineries[((2*rowCounter)+lineCounter)%5],rowCounter,lineCounter,creator=self))
                elif char == "h":
                    # add steam hub
                    itemsOnFloor.append(items.Item(displayChars.hub,rowCounter,lineCounter,creator=self))
                elif char == "i":
                    # add ramp
                    itemsOnFloor.append(items.Item(displayChars.ramp,rowCounter,lineCounter,creator=self))
                elif char == "p":
                    # add something
                    # bad code: either find out what this does or delete the code
                    itemsOnFloor.append(items.Item(displayChars.noClue,rowCounter,lineCounter,creator=self))
                elif char == "q":
                    # add special pipe
                    # bad code: pipe connection should be done some other way
                    item = items.Item(displayChars.pipe_lr,rowCounter,lineCounter,creator=self)
                    item.walkable = True
                    itemsOnFloor.append(item)
                elif char == "r":
                    # add special pipe
                    # bad code: pipe connection should be done some other way
                    item = items.Item(displayChars.pipe_lrd,rowCounter,lineCounter,creator=self)
                    item.walkable = True
                    itemsOnFloor.append(item)
                elif char == "s":
                    # add special pipe
                    # bad code: pipe connection should be done some other way
                    item = items.Item(displayChars.pipe_ld,rowCounter,lineCounter,creator=self)
                    item.walkable = True
                    itemsOnFloor.append(item)
                elif char == "t":
                    # add special pipe
                    # bad code: pipe connection should be done some other way
                    item = items.Item(displayChars.pipe_lu,rowCounter,lineCounter,creator=self)
                    item.walkable = True
                    itemsOnFloor.append(item)
                elif char == "u":
                    # add special pipe
                    # bad code: pipe connection should be done some other way
                    item = items.Item(displayChars.pipe_ru,rowCounter,lineCounter,creator=self)
                    item.walkable = True
                    itemsOnFloor.append(item)
                elif char == "w":
                    # add spray
                    # bad code: handle orientation some other way
                    item = items.Spray(rowCounter,lineCounter,direction="right",creator=self)
                    itemsOnFloor.append(item)
                    self.sprays.append(item)
                elif char == "x":
                    # add spray
                    # bad code: handle orientation some other way
                    item = items.Spray(rowCounter,lineCounter,direction="left",creator=self)
                    itemsOnFloor.append(item)
                    self.sprays.append(item)
                elif char == "y":
                    # to be outlet
                    itemsOnFloor.append(items.Item(displayChars.outlet,rowCounter,lineCounter,creator=self))
                elif char == "j":
                    # to be vat snake
                    itemsOnFloor.append(items.Item(displayChars.vatSnake,rowCounter,lineCounter,creator=self))
                elif char == "c":
                    # add corpse
                    item = items.Corpse(rowCounter,lineCounter,creator=self)
                    itemsOnFloor.append(item)
                elif char == "z":
                    # add special pipe
                    # bad code: pipe connection should be done some other way
                    item = items.Item(displayChars.pipe_ud,rowCounter,lineCounter,creator=self)
                    item.walkable = True
                    itemsOnFloor.append(item)
                elif char == "Ö":
                    # add growth tank
                    # bad code: specal chars should not be used in code
                    # bad code: handle state some other way
                    item = items.GrowthTank(rowCounter,lineCounter,filled=True,creator=self)
                    itemsOnFloor.append(item)
                elif char == "ö":
                    # add growth tank
                    # bad code: specal chars should not be used in code
                    # bad code: handle state some other way
                    item = items.GrowthTank(rowCounter,lineCounter,filled=False,creator=self)
                    itemsOnFloor.append(item)
                elif char == "B":
                    # add to be barricade
                    item = items.Item(displayChars.barricade,rowCounter,lineCounter,creator=self)
                    item.walkable = True
                    itemsOnFloor.append(item)
                else:
                    # add undefined stuff
                    itemsOnFloor.append(items.Item(displayChars.randomStuff2[((2*rowCounter)+lineCounter)%10],rowCounter,lineCounter,creator=self))
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

        # actually add the items
        self.addItems(itemsOnFloor)

        self.initialState = self.getState()
        loadingRegistry.register(self)

    '''
    get count of children for creating unique ids
    '''
    def getCreationCounter(self):
        self.creationCounter += 1
        return self.creationCounter

    '''
    get the difference in state since creation
    '''
    def getDiffState(self):
        currentState = self.getState()

        result = {}

        # diff attributes
        for attribute in ("yPosition","xPosition","offsetX","offsetY"):
            if not self.initialState[attribute] == currentState[attribute]:
                result[attribute] = currentState[attribute]
        if not self.creationCounter == self.initialState["creationCounter"]:
            result["creationCounter"] = self.creationCounter

        '''
        get the difference of a list between existing and initial state
        bad code: should be in extra class
        bad code: redundant code
        '''
        def getDiffList(toDiff,containerName,exclude=[]):
            # the to be result
            states = {}
            newThingsList = []
            changedThingsList = []
            removedThingsList = []

            # helper state
            currentThingsList = []

            # handle things that exist right now
            for thing in toDiff:
                # skip excludes
                if thing.id in exclude:
                    continue

                # register thing as existing
                currentState = thing.getState()
                currentThingsList.append(thing.id)

                if thing.id in self.initialState[containerName]:
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
            for thingId in self.initialState[containerName]:
                if thingId in exclude:
                    continue
                if not thingId in currentThingsList:
                    removedThingsList.append(thingId)

            return (states,changedThingsList,newThingsList,removedThingsList)

        # store item diff
        (itemStates,changedItems,newItems,removedItems) = getDiffList(self.itemsOnFloor,"itemIds")
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
        (charStates,changedChars,newChars,removedChars) = getDiffList(self.characters,"characterIds",exclude=exclude)
        if changedChars:
            result["changedChars"] = changedChars
        if newChars:
            result["newChars"] = newChars
        if removedChars:
            result["removedChars"] = removedChars
        if charStates:
            result["charStates"] = charStates

        # store events diff
        (eventStates,changedEvents,newEvents,removedEvents) = getDiffList(self.events,"eventIds")
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
        '''
        get a list of ids an a dict of their states from a list of objects
        bad code: should be in extra class
        '''
        def storeStateList(sourceList,exclude=[]):
            ids = []
            states = {}

            for thing in sourceList:
                if thing.id in exclude:
                    continue
                ids.append(thing.id)
                states[thing.id] = thing.getDiffState()

            return (states,ids)

        # get states from lists
        (eventIds,eventStates) = storeStateList(self.events)
        (itemIds,itemStates) = storeStateList(self.itemsOnFloor)
        (charIds,charStates) = storeStateList(self.characters)

        # generate state
        return { 
                 "eventIds": eventIds,
                 "eventStates":eventStates,
                 "itemIds":itemIds,
                 "itemStates":itemStates,
                 "characterIds":charIds,
                 "characterStates":charStates,
                 "offsetX":self.offsetX,
                 "offsetY":self.offsetY,
                 "xPosition":self.xPosition,
                 "yPosition":self.yPosition,
                 "creationCounter":self.creationCounter,
        }

    '''
    construct state from semi serialised form
    bad code: incomplete
    '''
    def setState(self,state):
        if "creationCounter" in state:
            self.creationCounter = state["creationCounter"]

        # move room to correct position
        if "offsetX" in state:
            self.offsetX = state["offsetX"]
        if "offsetY" in state:
            self.offsetY = state["offsetY"]
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
                item = items.getItemFromState(itemState)
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
                char = characters.Character()
                char.setState(charState)
                self.addCharacter(char,charState["xPosition"],charState["yPosition"])

        # add new events
        if "newEvents" in state:
            for eventId in state["newEvents"]:
                eventState = state["eventStates"][eventId]
                event = events.getEventFromState(eventState)
                self.addEvent(event)

        self.forceRedraw()

    '''
    invalidate render
    '''
    def changed(self):
        self.requestRedraw()
        pass

    '''
    get physical resistance against beeing moved
    '''
    def getResistance(self):
        return self.sizeX*self.sizeY

    '''
    open all doors
    '''
    def openDoors(self):
        for door in self.doors:
            door.open()
            self.open = True

    '''
    close all doors
    '''
    def closeDoors(self):
        for door in self.doors:
            door.close()
            self.open = False

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
                        if not self.shownQuestmarkerLastRender:
                            # only show the questmarker every second turn
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
                        else:
                            # only show the questmarker every second turn
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

    '''
    teleport character out of the room
    '''
    def removeCharacter(self,character):
        self.characters.remove(character)
        character.room = None

    '''
    add items to internal structure
    '''
    def addItems(self,items):
        self.itemsOnFloor.extend(items)
        for item in items:
            item.room = self
            if (item.xPosition,item.yPosition) in self.itemByCoordinates:
                self.itemByCoordinates[(item.xPosition,item.yPosition)].append(item)
            else:
                self.itemByCoordinates[(item.xPosition,item.yPosition)] = [item]

    '''
    remove item from internal structure
    bad pattern: should be removeItems
    '''
    def removeItem(self,item):
        self.itemByCoordinates[(item.xPosition,item.yPosition)].remove(item)
        if not self.itemByCoordinates[(item.xPosition,item.yPosition)]:
            del self.itemByCoordinates[(item.xPosition,item.yPosition)]
        self.itemsOnFloor.remove(item)

    '''
    get a list of things affected if the room would move north
    bad code: nearly identical code for each direction
    '''
    def getAffectedByMovementNorth(self,initialMovement=True,force=1,movementBlock=set()):
        # gather things that would be affected on terrain level
        self.terrain.getAffectedByRoomMovementNorth(self,force=force,movementBlock=movementBlock)

        # gather things chained to the room
        for thing in self.chainedTo:
            if thing not in movementBlock:
                movementBlock.add(thing)
                thing.getAffectedByMovementNorth(force=force,movementBlock=movementBlock)

        return movementBlock

    '''
    move the room to the north
    bad code: nearly identical code for each direction
    '''
    def moveNorth(self,force=1,initialMovement=True,movementBlock=set()):
        if initialMovement:
            # collect the things that would be affected by the movement
            movementBlock = set()
            movementBlock.add(self)
            self.getAffectedByMovementNorth(force=force,movementBlock=movementBlock)

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
                    thing.moveNorth(initialMovement=False)
        
        # actually move the room
        self.terrain.moveRoomNorth(self)
        messages.append("*RUMBLE*")

    '''
    get a list of things affected if the room would move south
    bad code: nearly identical code for each direction
    '''
    def getAffectedByMovementSouth(self,initialMovement=True,force=1,movementBlock=set()):
        # gather things that would be affected on terrain level
        self.terrain.getAffectedByRoomMovementSouth(self,force=force,movementBlock=movementBlock)

        # gather things chained to the room
        for thing in self.chainedTo:
            if thing not in movementBlock:
                movementBlock.add(thing)
                thing.getAffectedByMovementSouth(force=force,movementBlock=movementBlock)

        return movementBlock

    '''
    move the room to the south
    bad code: nearly identical code for each direction
    '''
    def moveSouth(self,force=1,initialMovement=True,movementBlock=set()):
        if initialMovement:
            # collect the things that would be affected by the movement
            movementBlock = set()
            movementBlock.add(self)
            self.getAffectedByMovementSouth(force=force,movementBlock=movementBlock)

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
                    thing.moveSouth(initialMovement=False)
        
        # actually move the room
        self.terrain.moveRoomSouth(self)
        messages.append("*RUMBLE*")

    '''
    get a list of things affected if the room would move west
    bad code: nearly identical code for each direction
    '''
    def getAffectedByMovementWest(self,initialMovement=True,force=1,movementBlock=set()):
        # gather things that would be affected on terrain level
        self.terrain.getAffectedByRoomMovementWest(self,force=force,movementBlock=movementBlock)

        # gather things chained to the room
        for thing in self.chainedTo:
            if thing not in movementBlock:
                movementBlock.add(thing)
                thing.getAffectedByMovementWest(force=force,movementBlock=movementBlock)

        return movementBlock

    '''
    move the room to the west
    bad code: nearly identical code for each direction
    '''
    def moveWest(self,initialMovement=True,force=1,movementBlock=set()):
        if initialMovement:
            # collect the things that would be affected by the movement
            movementBlock = set()
            movementBlock.add(self)
            self.getAffectedByMovementWest(force=force,movementBlock=movementBlock)

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
                    thing.moveWest(initialMovement=False)
        
        # actually move the room
        self.terrain.moveRoomWest(self)
        messages.append("*RUMBLE*")

    '''
    get a list of things affected if the room would move east
    bad code: nearly identical code for each direction
    '''
    def getAffectedByMovementEast(self,force=1,movementBlock=set()):
        # gather things that would be affected on terrain level
        self.terrain.getAffectedByRoomMovementEast(self,force=force,movementBlock=movementBlock)

        # gather things chained to the room
        for thing in self.chainedTo:
            if thing not in movementBlock:
                movementBlock.add(thing)
                thing.getAffectedByMovementEast(force=force,movementBlock=movementBlock)

        return movementBlock

    '''
    move the room to the east
    bad code: nearly identical code for each direction
    '''
    def moveEast(self,initialMovement=True, movementToken=None,force=1):
        if initialMovement:
            # collect the things that would be affected by the movement
            movementBlock = set()
            movementBlock.add(self)
            self.getAffectedByMovementEast(force=force,movementBlock=movementBlock)

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
                    thing.moveEast(initialMovement=False)
        
        # actually move the room
        self.terrain.moveRoomEast(self)
        messages.append("*RUMBLE*")

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

        # move instide the room
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
        character.xPosition = newXPos
        character.yPosition = newYPos
        self.removeCharacter(character)
        self.terrain.characters.append(character)
        character.terrain = self.terrain
        character.changed()
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
            # bad code: does nothing
            else:
                character.xPosition = newPosition[0]
                character.yPosition = newPosition[1]

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
    '''
    def removeEvent(self,event):
        self.events.remove(event)

    '''
    remove items of a certain type from internal structure
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

        if not self.hidden:
            # redo delayed calculation
            if self.delayedTicks > 0:
                self.applySkippedAdvances()
            
            # advance each character
            for character in self.characters:
                character.advance()
        else:
            # do calculation later
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
        self.lever1 = items.Lever(1,5,"engine control",creator=self)
        self.lever2 = items.Lever(8,5,"boarding alarm",creator=self)
        coalPile1 = items.Pile(8,3,"coal Pile1",items.Coal,creator=self)
        coalPile2 = items.Pile(8,4,"coal Pile2",items.Coal,creator=self)
        coalPile3 = items.Pile(1,3,"coal Pile1",items.Coal,creator=self)
        coalPile4 = items.Pile(1,4,"coal Pile2",items.Coal,creator=self)

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
    def changed(self):
        # notify vat
        # bad code: vat should listen
        self.terrain.tutorialVatProcessing.recalculate()

        if self.desiredSteamGeneration:
            if not self.desiredSteamGeneration == self.steamGeneration:
                # reset order for firering the furnaces
                if self.secondOfficer:
                    if self.furnaceQuest:
                        self.furnaceQuest.deactivate()
                        self.furnaceQuest.postHandler()
                    self.furnaceQuest = quests.KeepFurnacesFiredMeta(self.furnaces[:self.desiredSteamGeneration])
                    self.secondOfficer.assignQuest(self.furnaceQuest,active=True)
            else:
                messages.append("we did it! "+str(self.desiredSteamGeneration)+" instead of "+str(self.steamGeneration))

'''
a room to waste cpu power. used for performance testing
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
        add a patroling npc
        '''
        def addNPC(x,y):
            # generate quests
            #TODO: replace with patrol quest since it's actually bugging
            quest1 = quests.MoveQuestMeta(self,2,2,creator=self)
            quest2 = quests.MoveQuestMeta(self,2,7,creator=self)
            quest3 = quests.MoveQuestMeta(self,7,7,creator=self)
            quest4 = quests.MoveQuestMeta(self,7,2,creator=self)
            quest1.followUp = quest2
            quest2.followUp = quest3
            quest3.followUp = quest4
            quest4.followUp = quest1

            # add npc
            npc = Character(displayChars.staffCharactersByLetter["l"],x,y,name="Erwin von Liebweg",creator=self)
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
        
        # bad code: does nothing
        class Event(object):
            def __init__(subself,tick):
                subself.tick = tick

            def handleEvent(subself):
                self.applySkippedAdvances()

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
X .......DX
X'.'' ''.IX
X'.'' ''.|X
X'.'' ''.|X
X'.'' ''.IX
X .......DX
XXXXXXXXXXX
"""
        super().__init__(self.roomLayout,xPosition,yPosition,offsetX,offsetY,desiredPosition,creator=creator)
        self.name = "Infanteryquarters"
    
'''
the room where raw goo is processed into eatable form
'''
class Vat1(Room):
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
        self.gooDispenser = items.GooDispenser(6,7,creator=self)
        self.addItems([self.gooDispenser])
        self.name = "Vat1"

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
'''
class Vat2(Room):
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
        self.name = "Vat2"

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
Xm .PX
XOF.PX
Xmm.PX
XXXXXX
"""
        super().__init__(self.roomLayout,xPosition,yPosition,offsetX,offsetY,desiredPosition,creator=creator)
        self.floorDisplay = [displayChars.nonWalkableUnkown]
        self.gogogo = False
        self.engineStrength = 0
        self.name = "MiniMech"

        # add npc
        self.npc = Character(displayChars.staffCharacters[12],3,3,name="Friedrich Engelbart",creator=self)
        self.addCharacter(self.npc,3,3)
        self.npc.room = self

        quest = None
        '''
        the chat for making the npc stop firering the furnace
        '''
        class StopChat(interaction.SubMenu):
            id = "StopChat"
            type = "StopChat"

            dialogName = "stop fireing the furnaces."
            '''
            basic state initialization
            '''
            def __init__(self,partner):
                self.state = None
                self.partner = partner
                self.firstRun = True
                self.done = False
                self.persistentText = ""
                super().__init__()

            '''
            stop furnace quest and correct dialog
            '''
            def handleKey(self, key):
                if self.firstRun:
                    # stop fireing the furnace
                    self.persistentText = "OK, stopping now"
                    self.set_text(self.persistentText)
                    self.done = True
                    global quest
                    quest.deactivate()

                    # replace dialog option
                    self.partner.basicChatOptions.remove(StopChat)
                    self.partner.basicChatOptions.append(StartChat)

                    self.firstRun = False

                    return True
                else:
                    # show dialog till keystroke
                    return False

        '''
        the chat for making the npc start firering the furnace
        '''
        class StartChat(interaction.SubMenu):
            id = "StartChat"
            type = "StartChat"

            dialogName = "fire the furnaces."
            '''
            basic state initialization
            '''
            def __init__(self,partner):
                self.state = None
                self.partner = partner
                self.firstRun = True
                self.done = False
                self.persistentText = ""
                super().__init__()

            '''
            start furnace quest and correct dialog
            '''
            def handleKey(self, key):
                if self.firstRun:
                    # start fireing the furnace
                    self.persistentText = "Starting now. The engines should be running in a few ticks"
                    self.set_text(self.persistentText)
                    self.done = True
                    global quest
                    quest = quests.KeepFurnaceFiredMeta(self.partner.room.furnaces[0])
                    self.partner.assignQuest(quest,active=True)

                    # replace dialog option
                    self.partner.basicChatOptions.remove(StartChat)
                    self.partner.basicChatOptions.append(StopChat)

                    self.firstRun = False

                    return True
                else:
                    return False

        # add dialog options
        self.npc.basicChatOptions.append(StartChat)
        self.initialState = self.getState()
        loadingRegistry.register(self)

    '''
    recalculate engine strength
    '''
    def changed(self):
        self.engineStrength = 250*self.steamGeneration

'''
a room sized base for small off mech missions
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
        self.artwork = items.ProductionArtwork(4,1)
        self.compactor = items.ScrapCompactor(6,1)
        self.addItems([self.artwork,self.compactor])
        self.initialState = self.getState()
        loadingRegistry.register(self)

'''
a lab for behaviour testing
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
        bean = items.MarkerBean(1,2,creator=self)
        beanPile = items.Pile(1,1,"markerPile",items.MarkerBean,creator=self)
        self.addItems([bean,beanPile])
        self.name = "Lab"

        # save initial state and register
        self.initialState = self.getState()
        loadingRegistry.register(self)

'''
cargo storage for tighty packing items
'''
class CargoRoom(Room):
    '''
    create room, set storage order and fill with items
    '''
    def __init__(self,xPosition,yPosition,offsetX,offsetY,desiredPosition=None,itemTypes=[items.Pipe,items.Wall,items.Furnace,items.Boiler],amount=80,creator=None):
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

        # determine item types the room should be filled with
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

        # map items on storage space
        counter = 0
        for item in self.storedItems:
            item.xPosition = self.storageSpace[counter][0]
            item.yPosition = self.storageSpace[counter][1]
            counter += 1

        # actually add the items
        self.addItems(self.storedItems)
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
            counter += 1

        # actually add the items
        self.addItems(self.storedItems)
        self.initialState = self.getState()
        loadingRegistry.register(self)

    '''
    use specialised pathfinding
    '''
    def calculatePath(self,x,y,dstX,dstY,walkingPath):
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
        self.lever1 = items.Lever(3,1,"training lever",creator=self)
        self.objectDispenser = items.OjectDispenser(4,1,creator=self)
        self.gooDispenser = items.GooDispenser(5,9,creator=self)
        self.furnace = items.Furnace(4,9,creator=self)
        self.pile = items.Pile(6,9,creator=self)

        # connect lever
        def activateDispenser(dispenser):
            self.objectDispenser.dispenseObject()
        self.lever1.activateAction = activateDispenser

        # actually add items
        self.addItems([self.lever1,self.gooDispenser,self.objectDispenser,self.furnace,self.pile])

        # save initial state and register
        self.initialState = self.getState()
        loadingRegistry.register(self)

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
        npc = characters.Character(displayChars.staffCharactersByLetter["s"],4,4,name="Simon Kantbrett",creator=self)
        self.hoppers.append(npc)
        self.addCharacter(npc,2,2)
        npc = characters.Character(displayChars.staffCharactersByLetter["r"],4,5,name="Rudolf Krautbart",creator=self)
        self.hoppers.append(npc)
        self.addCharacter(npc,2,3)

        # assign hopper duty to hoppers
        for hopper in self.hoppers:
            quest = quests.HopperDuty(self,creator=self)
            hopper.assignQuest(quest,active=True)

        # save initial state and register
        self.initialState = self.getState()
        loadingRegistry.register(self)

'''
a dummy for the mechs command centre
'''
class MechCommand(Room):
    def __init__(self,xPosition,yPosition,offsetX,offsetY,desiredPosition=None,creator=None):
        self.roomLayout = """
XXXXX$XXXXX
XI        X
XI .....  X
XD .   .  X
XD .@@ .  X
XD .   .  X
XD .....  X
XI        X
XI        X
XXXXXXXXXXX
"""
        super().__init__(self.roomLayout,xPosition,yPosition,offsetX,offsetY,desiredPosition,creator=creator)
        self.name = "Mech Command Centre"

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
        self.artwork = items.ProductionArtwork(4,1,creator=self)
        self.compactor = items.ScrapCompactor(6,1,creator=self)
        self.addItems([self.artwork,self.compactor])

        # add some produced items
        self.producedItems = []
        self.producedItems.append(items.Wall(9,5,creator=self))
        self.producedItems.append(items.Wall(9,4,creator=self))
        self.producedItems.append(items.Wall(9,6,creator=self))
        self.producedItems.append(items.Wall(9,3,creator=self))
        self.producedItems.append(items.Wall(9,7,creator=self))
        self.producedItems.append(items.Wall(9,2,creator=self))
        self.producedItems.append(items.Wall(9,8,creator=self))
        self.addItems(self.producedItems)

        # save initial state and register
        self.initialState = self.getState()
        loadingRegistry.register(self)

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
                    itemsToPlace[(x,y)] = items.Pipe
                if char == "X":
                    itemsToPlace[(x,y)] = items.Wall
                y += 1
            x += 1

        # add marker for items
        itemstoAdd = []
        for (position,itemType) in itemsToPlace.items():
            item = items.MarkerBean(position[1],position[0],creator=self)
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

        # sort items in build order
        self.itemsInBuildOrder = []
        for position in buildorder:
            if position in itemsToPlace:
                self.itemsInBuildOrder.append((position,itemsToPlace[position]))
        self.itemsInBuildOrder.reverse()

        # save initial state and register
        self.initialState = self.getState()
        loadingRegistry.register(self)

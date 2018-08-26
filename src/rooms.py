import src.items as items
import src.quests as quests

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
    def __init__(self,layout,xPosition,yPosition,offsetX,offsetY,desiredPosition=None):
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
        self.id = "room_1_"+str(self.xPosition)+"_"+str(self.yPosition)+"_1"
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
                    # add default npc
                    if (not self.firstOfficer) or (not self.secondOfficer):
                        if not self.firstOfficer:
                            # add first officer
                            npc = characters.Character(displayChars.staffCharactersByLetter["e"],5,3,name="Eduart Eisenblatt")
                            self.addCharacter(npc,rowCounter,lineCounter)
                            npc.terrain = self.terrain
                            self.firstOfficer = npc
                            quest = quests.RoomDuty()
                            npc.assignQuest(quest,active=True)
                        else:
                            # add second officer
                            npc = characters.Character(displayChars.staffCharactersByLetter["s"],5,3,name="Siegfied Knobelbecher")
                            self.addCharacter(npc,rowCounter,lineCounter)
                            npc.terrain = self.terrain
                            self.secondOfficer = npc
                            quest = quests.RoomDuty()
                            npc.assignQuest(quest,active=True)
                elif char in ("X","&"):
                    # add wall
                    itemsOnFloor.append(items.Wall(rowCounter,lineCounter))
                elif char == "$":
                    # add door and mark position as entry point
                    door = items.Door(rowCounter,lineCounter)
                    itemsOnFloor.append(door)
                    self.walkingAccess.append((rowCounter,lineCounter))
                    self.doors.append(door)
                elif char == "P":
                    # add pile and save to list
                    item = items.Pile(rowCounter,lineCounter)
                    itemsOnFloor.append(item)
                    self.piles.append(item)
                elif char == "F":
                    # add furnace and save to list
                    item = items.Furnace(rowCounter,lineCounter)
                    itemsOnFloor.append(item)
                    self.furnaces.append(item)
                elif char == "#":
                    # add pipe and save to list
                    item = items.Pipe(rowCounter,lineCounter)
                    itemsOnFloor.append(item)
                    self.pipes.append(item)
                elif char == "D":
                    # add display
                    itemsOnFloor.append(items.Display(rowCounter,lineCounter))
                elif char == "v":
                    #to be bin
                    itemsOnFloor.append(items.Item(displayChars.binStorage,rowCounter,lineCounter))
                elif char == "O":
                    #to be pressure Tank
                    item = items.Boiler(rowCounter,lineCounter)
                    itemsOnFloor.append(item)
                    self.boilers.append(item)
                    #itemsOnFloor.append(items.Item(displayChars.boiler_active,rowCounter,lineCounter))
                elif char == "8":
                    #to be chains
                    itemsOnFloor.append(items.Item(displayChars.chains,rowCounter,lineCounter))
                elif char == "I":
                    #to be commlink
                    itemsOnFloor.append(items.Commlink(rowCounter,lineCounter))
                elif char == "H":
                    # add hutch
                    # bad code: handle state some other way
                    itemsOnFloor.append(items.Hutch(rowCounter,lineCounter))
                elif char == "'":
                    # add hutch
                    # bad code: handle state some other way
                    itemsOnFloor.append(items.Hutch(rowCounter,lineCounter,activated=True))
                elif char == "o":
                    #to be grid
                    itemsOnFloor.append(items.Item(displayChars.grid,rowCounter,lineCounter))
                elif char == "a":
                    #to be acid
                    item = items.Item(displayChars.acids[((2*rowCounter)+lineCounter)%5],rowCounter,lineCounter)
                    item.walkable = True
                    itemsOnFloor.append(item)
                elif char == "b":
                    # to be foodstuffs
                    itemsOnFloor.append(items.Item(displayChars.foodStuffs[((2*rowCounter)+lineCounter)%6],rowCounter,lineCounter))
                elif char == "m":
                    # to be machinery
                    itemsOnFloor.append(items.Item(displayChars.machineries[((2*rowCounter)+lineCounter)%5],rowCounter,lineCounter))
                elif char == "h":
                    # add steam hub
                    itemsOnFloor.append(items.Item(displayChars.hub,rowCounter,lineCounter))
                elif char == "i":
                    # add ramp
                    itemsOnFloor.append(items.Item(displayChars.ramp,rowCounter,lineCounter))
                elif char == "p":
                    # add something
                    # bad code: either find out what this does or delete the code
                    itemsOnFloor.append(items.Item(displayChars.noClue,rowCounter,lineCounter))
                elif char == "q":
                    # add special pipe
                    # bad code: pipe connection should be done some other way
                    item = items.Item(displayChars.pipe_lr,rowCounter,lineCounter)
                    item.walkable = True
                    itemsOnFloor.append(item)
                elif char == "r":
                    # add special pipe
                    # bad code: pipe connection should be done some other way
                    item = items.Item(displayChars.pipe_lrd,rowCounter,lineCounter)
                    item.walkable = True
                    itemsOnFloor.append(item)
                elif char == "s":
                    # add special pipe
                    # bad code: pipe connection should be done some other way
                    item = items.Item(displayChars.pipe_ld,rowCounter,lineCounter)
                    item.walkable = True
                    itemsOnFloor.append(item)
                elif char == "t":
                    # add special pipe
                    # bad code: pipe connection should be done some other way
                    item = items.Item(displayChars.pipe_lu,rowCounter,lineCounter)
                    item.walkable = True
                    itemsOnFloor.append(item)
                elif char == "u":
                    # add special pipe
                    # bad code: pipe connection should be done some other way
                    item = items.Item(displayChars.pipe_ru,rowCounter,lineCounter)
                    item.walkable = True
                    itemsOnFloor.append(item)
                elif char == "w":
                    # add spray
                    # bad code: handle orientation some other way
                    item = items.Spray(rowCounter,lineCounter,direction="right")
                    itemsOnFloor.append(item)
                    self.sprays.append(item)
                elif char == "x":
                    # add spray
                    # bad code: handle orientation some other way
                    item = items.Spray(rowCounter,lineCounter,direction="left")
                    itemsOnFloor.append(item)
                    self.sprays.append(item)
                elif char == "y":
                    # to be outlet
                    itemsOnFloor.append(items.Item(displayChars.outlet,rowCounter,lineCounter))
                elif char == "j":
                    # to be vat snake
                    itemsOnFloor.append(items.Item(displayChars.vatSnake,rowCounter,lineCounter))
                elif char == "c":
                    # add corpse
                    item = items.Corpse(rowCounter,lineCounter)
                    itemsOnFloor.append(item)
                elif char == "C":
                    # add unconcious body
                    item = items.UnconciousBody(rowCounter,lineCounter)
                    itemsOnFloor.append(item)
                elif char == "z":
                    # add special pipe
                    # bad code: pipe connection should be done some other way
                    item = items.Item(displayChars.pipe_ud,rowCounter,lineCounter)
                    item.walkable = True
                    itemsOnFloor.append(item)
                elif char == "Ö":
                    # add growth tank
                    # bad code: specal chars should not be used in code
                    # bad code: handle state some other way
                    item = items.GrowthTank(rowCounter,lineCounter,filled=True)
                    itemsOnFloor.append(item)
                elif char == "ö":
                    # add growth tank
                    # bad code: specal chars should not be used in code
                    # bad code: handle state some other way
                    item = items.GrowthTank(rowCounter,lineCounter,filled=False)
                    itemsOnFloor.append(item)
                elif char == "B":
                    # add to be barricade
                    item = items.Item(displayChars.barricade,rowCounter,lineCounter)
                    item.walkable = True
                    itemsOnFloor.append(item)
                else:
                    # add undefined stuff
                    itemsOnFloor.append(items.Item(displayChars.randomStuff2[((2*rowCounter)+lineCounter)%10],rowCounter,lineCounter))
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

    '''
    get semi serialised room state
    bad code: incomplete
    '''
    def getState(self):
        return { "offsetX":self.offsetX,
                 "offsetY":self.offsetY,
                 "xPosition":self.xPosition,
                 "yPosition":self.yPosition,
        }

    '''
    construct state from semi serialised form
    bad code: incomplete
    '''
    def setState(self,state):
        # move room to correct position
        self.offsetX = state["offsetX"]
        self.offsetY = state["offsetY"]
        if not (self.xPosition == state["xPosition"] and self.yPosition == state["yPosition"]):
            self.terrain.teleportRoom(self,(state["xPosition"],state["yPosition"]))

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
                chars[character.yPosition][character.xPosition] = character.display

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
                chars[mainChar.yPosition][mainChar.xPosition] = mainChar.display
        # show dummy of the room
        else:
            # fill inside the room with invisibility
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

    '''
    move character north within the room
    bad code: almost identical code for each direction
    '''
    def moveCharacterNorth(self,character):
        # teleport character to terrain if moved of terrain
        if not character.yPosition:
            newYPos = character.yPosition+character.room.yPosition*15+character.room.offsetY-1
            newXPos = character.xPosition+character.room.xPosition*15+character.room.offsetX
            character.xPosition = newXPos
            character.yPosition = newYPos
            self.removeCharacter(character)
            self.terrain.characters.append(character)
            character.terrain = self.terrain
            character.changed()
            return

        # move character
        newPosition = (character.xPosition,character.yPosition-1)
        return self.moveCharacter(character,newPosition)

    '''
    move character south within the room
    bad code: almost identical code for each direction
    '''
    def moveCharacterSouth(self,character):
        # teleport character to terrain if moved of terrain
        if character.yPosition == self.sizeY-1:
            newYPos = character.yPosition+character.room.yPosition*15+character.room.offsetY+1
            newXPos = character.xPosition+character.room.xPosition*15+character.room.offsetX
            character.xPosition = newXPos
            character.yPosition = newYPos
            self.removeCharacter(character)
            self.terrain.characters.append(character)
            character.terrain = self.terrain
            character.changed()
            return

        # move character
        newPosition = (character.xPosition,character.yPosition+1)
        return self.moveCharacter(character,newPosition)

    '''
    move character west within the room
    bad code: almost identical code for each direction
    '''
    def moveCharacterWest(self,character):

        # teleport character to terrain if moved of terrain
        if not character.xPosition:
            newYPos = character.yPosition+character.room.yPosition*15+character.room.offsetY
            newXPos = character.xPosition+character.room.xPosition*15+character.room.offsetX-1
            character.xPosition = newXPos
            character.yPosition = newYPos
            self.removeCharacter(character)
            self.terrain.characters.append(character)
            character.terrain = self.terrain
            character.changed()
            return

        # move character
        newPosition = (character.xPosition-1,character.yPosition)
        return self.moveCharacter(character,newPosition)

    '''
    move character east within the room
    bad code: almost identical code for each direction
    '''
    def moveCharacterEast(self,character):
        # teleport character to terrain if moved of terrain
        if character.xPosition == self.sizeX-1:
            newYPos = character.yPosition+character.room.yPosition*15+character.room.offsetY
            newXPos = character.xPosition+character.room.xPosition*15+character.room.offsetX+1
            character.xPosition = newXPos
            character.yPosition = newYPos
            self.removeCharacter(character)
            self.terrain.characters.append(character)
            character.terrain = self.terrain
            character.changed()
            return

        # move character
        newPosition = (character.xPosition+1,character.yPosition)
        return self.moveCharacter(character,newPosition)

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
a test
bad code: is unused and silly
'''
class Room1(Room):
    '''
    create room
    '''
    def __init__(self,xPosition=0,yPosition=0,offsetX=2,offsetY=2,desiredPosition=None):
        self.roomLayout = """
XXXXXXXXXX
X#-------X
X#......-X
X#.- --.-X
X#.   -.-X
X#.----.-X
XB.BBBB.BX
$ ...... X
XMMv vMMMX
XXXXXXXXXX
"""
        super().__init__(self.roomLayout,xPosition,yPosition,offsetX,offsetY,desiredPosition)
        self.name = "Vat"

'''
a test
bad code: is unused and silly
'''
class Room2(Room):
    '''
    create rooms content
    '''
    def __init__(self,xPosition=0,yPosition=1,offsetX=4,offsetY=0,desiredPosition=None):
        self.roomMeta = """
"""
        roomLayout = """
XXXXXXXXXX
XXXXXXXXXX
XXXXXXXXXX
XXXXXXXXXX
XXXXXXXXXX
XXXXXXXXXX
XXXXXXXXXX
XXXXXXXXXX
XXXXXXXXXX
XXXXXXXXXX

XXX↓X↓↓X↓X
X  #8## #X
X  #8## #X
X  #8##8#X
X  # ## #X
X  # ##8#X
X  #8## #X
X  #8## #X
X  #8## #X
XXX↓X↓↓↓↓X

XXXXXXXXXX
X        X
X        X
X  88##8 X
X  #8##8 X
X  88##8 X
X   8    X
X        X
X        X
XXXXXXXXXX

XXXXHXXXXX
X@Iv vID#X
X@      #X
X@ 8#OF PX
X@ ##OF PX
XB 8#OF PX
XB |DI  PX
XB      #X
XPPPPPID#X
XXXXXXXXXX
"""
        roomLayout = """
XXXX$XXXXX
X@ v vID#X
X@......#X
X@.8#O . X
X@.##O . X
XH.8#O . X
XH.|DI . X
XH......#X
XXPPP ID#X
XXXXXXXXXX
"""
        super().__init__(roomLayout,xPosition,yPosition,offsetX,offsetY,desiredPosition=None)
        self.name = "Boilerroom"

        # create special items
        self.lever1 = items.Lever(3,6,"engine control")
        self.lever2 = items.Lever(1,2,"boarding alarm")
        coalPile1 = items.Pile(8,3,"coal Pile1",items.Coal)
        coalPile2 = items.Pile(8,4,"coal Pile2",items.Coal)
        coalPile3 = items.Pile(8,5,"coal Pile3",items.Coal)
        coalPile4 = items.Pile(8,6,"coal Pile4",items.Coal)
        self.furnace1 = items.Furnace(6,3,"Furnace")
        self.furnace2 = items.Furnace(6,4,"Furnace")
        self.furnace3 = items.Furnace(6,5,"Furnace")
        
        # actually add items
        self.addItems([self.lever1,self.lever2,coalPile1,coalPile2,coalPile3,coalPile4,self.furnace])

        # create special quests
        quest0 = quests.ActivateQuest(self.lever1)
        quest1 = quests.MoveQuest(self,2,2)
        quest2 = quests.MoveQuest(self,2,7)
        quest3 = quests.MoveQuest(self,7,7)
        quest4 = quests.MoveQuest(self,7,2)
        quest0.followUp = quest1
        quest1.followUp = quest2
        quest2.followUp = quest3
        quest3.followUp = quest4
        quest4.followUp = quest1

        # add npc dooing these quests
        npc = Character(staffCharacters[11],1,2,name="Erwin von Liebweg")
        self.addCharacter(npc,1,3)
        npc.room = self
        npc.assignQuest(quest0)
        # bad code: commented out code
        #npc.automated = False

        # bind lever to action
        lever2 = self.lever2
        def lever2action(self):
            deactivateLeaverQuest = quests.ActivateQuest(lever2,desiredActive=False)
            npc.assignQuest(deactivateLeaverQuest,active=True)
        self.lever2.activateAction = lever2action

'''
the machine room used in the tutorial
bad pattern: should be abstracted
bad code: name and classname do not agree
'''
class TutorialMachineRoom(Room):
    '''
    create room and add special items
    '''
    def __init__(self,xPosition=0,yPosition=1,offsetX=4,offsetY=0,desiredPosition=None):
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
        super().__init__(roomLayout,xPosition,yPosition,offsetX,offsetY,desiredPosition)
        self.name = "Boilerroom"

        # generate special items
        self.lever1 = items.Lever(1,5,"engine control")
        self.lever2 = items.Lever(8,5,"boarding alarm")
        coalPile1 = items.Pile(8,3,"coal Pile1",items.Coal)
        coalPile2 = items.Pile(8,4,"coal Pile2",items.Coal)
        coalPile3 = items.Pile(1,3,"coal Pile1",items.Coal)
        coalPile4 = items.Pile(1,4,"coal Pile2",items.Coal)

        # actually add items
        self.addItems([self.lever1,self.lever2,coalPile1,coalPile2,coalPile3,coalPile4])

        self.furnaceQuest = None

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
a test
bad code: is unused and silly
'''
class Room3(Room):
    '''
    create room
    '''
    def __init__(self,xPosition=1,yPosition=0,offsetX=2,offsetY=2,desiredPosition=None):
        self.roomLayout = """
XXXXXXXXXX
X????????X
X?......?X
X?.X#X?.?X
XP.?#??.?X
XP.X#X?.?X
X?.X#  .?X
X?......?X
X??v v???X
XXXX$XXXXX
"""
        super().__init__(roomLayout,xPosition,yPosition,offsetX,offsetY,desiredPosition)
        self.name = "Room3"

'''
a test
bad code: is unused and silly
'''
class Room4(Room):
    '''
    create room
    '''
    def __init__(self):
        self.roomLayout = """
XX$XXXXXXX
Xv v?????X
X?......PX
X?.????.PX
X?.????.#X
X?.???P.#X
X?.?X??.#X
X?......#X
X? ?????#X
XXXXXXXXXX
"""
        super().__init__(roomLayout,xPosition,yPosition,offsetX,offsetY,desiredPosition)
        self.name = "Room4"

'''
a test for a automatic item placement
bad code: is unused and silly
'''
class GenericRoom(Room):
    '''
    create room
    '''
    def __init__(self,xPosition,yPosition,offsetX,offsetY,desiredPosition=None):
        self.roomLayout = """
XX$XXXXXXX
Xv v?????X
X?......PX
X?.????.PX
X?.????.#X
X?.???P.#X
X?.?X??.#X
X?......#X
X? XXXXX#X
XXXXXXXXXX
"""
        super().__init__(roomLayout,xPosition,yPosition,offsetX,offsetY,desiredPosition)
        self.name = "GenericRoom"

'''
a room to waste cpu power. used for performance testing
'''
class CpuWasterRoom(Room):
    '''
    create room and add patroling npcs
    '''
    def __init__(self,xPosition,yPosition,offsetX,offsetY):
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
        super().__init__(self.roomLayout,xPosition,yPosition,offsetX,offsetY,desiredPosition=None)
        self.name = "CpuWasterRoom"

        '''
        add a patroling npc
        '''
        def addNPC(x,y):
            # generate quests
            #TODO: replace with patrol quest since it's actually bugging
            quest1 = quests.MoveQuest(self,2,2)
            quest2 = quests.MoveQuest(self,2,7)
            quest3 = quests.MoveQuest(self,7,7)
            quest4 = quests.MoveQuest(self,7,2)
            quest1.followUp = quest2
            quest2.followUp = quest3
            quest3.followUp = quest4
            quest4.followUp = quest1

            # add npc
            npc = Character(displayChars.staffCharactersByLetter["l"],x,y,name="Erwin von Liebweg")
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

'''
the living space for soldiers
'''
class InfanteryQuarters(Room):
    '''
    create room
    '''
    def __init__(self,xPosition,yPosition,offsetX,offsetY,desiredPosition=None):
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
        super().__init__(self.roomLayout,xPosition,yPosition,offsetX,offsetY,desiredPosition)
        self.name = "Infanteryquarters"
    
'''
a test for a automatic item placement
'''
class FreePlacementRoom(Room):
    '''
    create room
    '''
    def __init__(self,xPosition,yPosition,offsetX,offsetY,desiredPosition=None):
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
        super().__init__(roomLayout,xPosition,yPosition,offsetX,offsetY,desiredPosition)
        self.name = "FreePlacementRoom"

'''
the room where raw goo is processed into eatable form
'''
class Vat1(Room):
    '''
    create room and add special item
    '''
    def __init__(self,xPosition,yPosition,offsetX,offsetY,desiredPosition=None):
        self.roomLayout = """
XXXXXXXXXX
XababaabbX
XrqqrqqsaX
XzayzayzaX
XuwbuwxtbX
XabybayaaX
XpsaabbaiX
XmhmooooDX
Xmmmv.voIX
XXXXX$XXXX
"""
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
        super().__init__(self.roomLayout,xPosition,yPosition,offsetX,offsetY,desiredPosition)

        # add special items
        self.gooDispenser = items.GooDispenser(6,7)
        self.addItems([self.gooDispenser])
        self.name = "Vat1"

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
    def __init__(self,xPosition,yPosition,offsetX,offsetY,desiredPosition=None):
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
        super().__init__(self.roomLayout,xPosition,yPosition,offsetX,offsetY,desiredPosition)
        self.isContainment = True
        self.floorDisplay = displayChars.acids
        self.name = "Vat2"

'''
the armor plates of a mech
'''
class MechArmor(Room):
    '''
    create room
    '''
    def __init__(self,xPosition,yPosition,offsetX,offsetY,desiredPosition=None):
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
        super().__init__(self.roomLayout,xPosition,yPosition,offsetX,offsetY,desiredPosition)
        self.floorDisplay = [displayChars.nonWalkableUnkown]
        self.name = "MechArmor"

'''
a mini mech to drive around with. including boiler and coal storage and furnace fireing npc
'''
class MiniMech(Room):
    '''
    create the room and add the npc
    '''
    def __init__(self,xPosition,yPosition,offsetX,offsetY,desiredPosition=None):
        self.roomLayout = """
XX$XXX
XD..@X
Xm .PX
XOF.PX
Xmm.PX
XXXXXX
"""
        super().__init__(self.roomLayout,xPosition,yPosition,offsetX,offsetY,desiredPosition)
        self.floorDisplay = [displayChars.nonWalkableUnkown]
        self.gogogo = False
        self.engineStrength = 0
        self.name = "MiniMech"

        # add npc
        self.npc = Character(displayChars.staffCharacters[12],3,3,name="Friedrich Engelbart")
        self.addCharacter(self.npc,3,3)
        self.npc.room = self

        quest = None
        '''
        the chat for making the npc stop firering the furnace
        '''
        class StopChat(interaction.SubMenu):
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
    def __init__(self,xPosition,yPosition,offsetX,offsetY,desiredPosition=None):
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
        super().__init__(self.roomLayout,xPosition,yPosition,offsetX,offsetY,desiredPosition)
        self.artwork = items.ProductionArtwork(4,1)
        self.compactor = items.ScrapCompactor(6,1)
        self.addItems([self.artwork,self.compactor])

'''
a lab for behaviour testing
'''
class LabRoom(Room):
    '''
    create room and add special items
    '''
    def __init__(self,xPosition,yPosition,offsetX,offsetY,desiredPosition=None):
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
        super().__init__(self.roomLayout,xPosition,yPosition,offsetX,offsetY,desiredPosition)
        bean = items.MarkerBean(1,2)
        beanPile = items.Pile(1,1,"markerPile",items.MarkerBean)
        self.addItems([bean,beanPile])
        self.name = "Lab"

'''
cargo storage for tighty packing items
'''
class CargoRoom(Room):
    '''
    create room, set storage order and fill with items
    '''
    def __init__(self,xPosition,yPosition,offsetX,offsetY,desiredPosition=None,itemTypes=[items.Pipe,items.Wall,items.Furnace,items.Boiler]):
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
        super().__init__(self.roomLayout,xPosition,yPosition,offsetX,offsetY,desiredPosition)
        self.floorDisplay = [displayChars.nonWalkableUnkown]
        self.name = "CargoRoom"

        # determine item types the room should be filled with
        self.storedItems = []
        counter = 0
        length = len(itemTypes)
        for i in range(1,80):
            i = i+i%3+i%10*2
            if i%2:
                counter += 1
            elif i%4:
                counter += 2
            elif i%8:
                counter += 3
            else:
                counter += 4
            self.storedItems.append(itemTypes[counter%length]())

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

'''
storage for storing items in an accessible way
'''
class StorageRoom(Room):
    '''
    create room, set storage order 
    '''
    def __init__(self,xPosition,yPosition,offsetX,offsetY,desiredPosition=None):
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

        super().__init__(self.roomLayout,xPosition,yPosition,offsetX,offsetY,desiredPosition)
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
    def __init__(self,xPosition,yPosition,offsetX,offsetY,desiredPosition=None):
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
        super().__init__(self.roomLayout,xPosition,yPosition,offsetX,offsetY,desiredPosition)
        self.name = "WakeUpRoom"

        # generate special items
        self.lever1 = items.Lever(3,1,"training lever")
        self.objectDispenser = items.OjectDispenser(4,1)
        self.gooDispenser = items.GooDispenser(5,9)
        self.furnace = items.Furnace(4,9)
        self.pile = items.Pile(6,9)

        # connect lever
        def activateDispenser(dispenser):
            self.objectDispenser.dispenseObject()
        self.lever1.activateAction = activateDispenser

        # actually add items
        self.addItems([self.lever1,self.gooDispenser,self.objectDispenser,self.furnace,self.pile])

'''
the room where hoppers wait for jobs
'''
class WaitingRoom(Room):
    '''
    create room and add hoppers
    '''
    def __init__(self,xPosition,yPosition,offsetX,offsetY,desiredPosition=None):
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
        super().__init__(self.roomLayout,xPosition,yPosition,offsetX,offsetY,desiredPosition)
        self.name = "WaitingRoom"
        self.hoppers = []

        # add hoppers
        npc = characters.Character(displayChars.staffCharactersByLetter["s"],5,3,name="Simon Kantbrett")
        self.hoppers.append(npc)
        self.addCharacter(npc,2,2)
        npc = characters.Character(displayChars.staffCharactersByLetter["r"],5,3,name="Rudolf Krautbart")
        self.hoppers.append(npc)
        self.addCharacter(npc,2,3)

        # assign hopper duty to hoppers
        for hopper in self.hoppers:
            quest = quests.HopperDuty(self)
            hopper.assignQuest(quest,active=True)

'''
a dummy for the mechs command centre
'''
class MechCommand(Room):
    def __init__(self,xPosition,yPosition,offsetX,offsetY,desiredPosition=None):
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
        super().__init__(self.roomLayout,xPosition,yPosition,offsetX,offsetY,desiredPosition)
        self.name = "Mech Command Centre"

'''
the place for production of tools and items
'''
class MetalWorkshop(Room):
    '''
    create room and add special items
    '''
    def __init__(self,xPosition,yPosition,offsetX,offsetY,desiredPosition=None):
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
        super().__init__(self.roomLayout,xPosition,yPosition,offsetX,offsetY,desiredPosition)
        self.name = "MetalWorkshop"

        # add production machines
        self.artwork = items.ProductionArtwork(4,1)
        self.compactor = items.ScrapCompactor(6,1)
        self.addItems([self.artwork,self.compactor])

        # add some produced items
        self.producedItems = []
        self.producedItems.append(items.Wall(9,5))
        self.producedItems.append(items.Wall(9,4))
        self.producedItems.append(items.Wall(9,6))
        self.producedItems.append(items.Wall(9,3))
        self.producedItems.append(items.Wall(9,7))
        self.producedItems.append(items.Wall(9,2))
        self.producedItems.append(items.Wall(9,8))
        self.addItems(self.producedItems)

'''
a room in the process of beeing constructed. The room itself exists but no items within
'''
class ConstructionSite(Room):
    '''
    create room and plan construction
    '''
    def __init__(self,xPosition,yPosition,offsetX,offsetY,desiredPosition=None):
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
        super().__init__(self.roomLayout,xPosition,yPosition,offsetX,offsetY,desiredPosition)
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
            item = items.MarkerBean(position[1],position[0])
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

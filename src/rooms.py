import src.items as items
import src.quests as quests

Character = None
mainChar = None
characters = None
messages = None
debugMessages = None
calculatePath = None
displayChars = None

class Room(object):
    def __init__(self,layout,xPosition,yPosition,offsetX,offsetY,desiredPosition=None):
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

        self.id = "room_1_"+str(self.xPosition)+"_"+str(self.yPosition)+"_1"

        self.itemByCoordinates = {}


        self.walkingAccess = []
        lineCounter = 0
        itemsOnFloor = []
        for line in self.layout[1:].split("\n"):
            rowCounter = 0
            for char in line:
                if char in (" ",".","@"):
                    pass
                elif char in ("X","&"):
                    itemsOnFloor.append(items.Wall(rowCounter,lineCounter))
                elif char == "$":
                    door = items.Door(rowCounter,lineCounter)
                    itemsOnFloor.append(door)
                    self.walkingAccess.append((rowCounter,lineCounter))
                    self.doors.append(door)
                elif char == "P":
                    item = items.Pile(rowCounter,lineCounter)
                    itemsOnFloor.append(item)
                    self.piles.append(item)
                elif char == "F":
                    item = items.Furnace(rowCounter,lineCounter)
                    itemsOnFloor.append(item)
                    self.furnaces.append(item)
                elif char == "#":
                    item = items.Pipe(rowCounter,lineCounter)
                    itemsOnFloor.append(item)
                    self.pipes.append(item)
                elif char == "D":
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
                    itemsOnFloor.append(items.Hutch(rowCounter,lineCounter))
                elif char == "'":
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
                    #to be foodstuffs
                    itemsOnFloor.append(items.Item(displayChars.foodStuffs[((2*rowCounter)+lineCounter)%6],rowCounter,lineCounter))
                elif char == "m":
                    itemsOnFloor.append(items.Item(displayChars.machineries[((2*rowCounter)+lineCounter)%5],rowCounter,lineCounter))
                elif char == "h":
                    itemsOnFloor.append(items.Item(displayChars.hub,rowCounter,lineCounter))
                elif char == "i":
                    itemsOnFloor.append(items.Item(displayChars.ramp,rowCounter,lineCounter))
                elif char == "p":
                    itemsOnFloor.append(items.Item(displayChars.noClue,rowCounter,lineCounter))
                elif char == "q":
                    item = items.Item(displayChars.pipe_lr,rowCounter,lineCounter)
                    item.walkable = True
                    itemsOnFloor.append(item)
                elif char == "r":
                    item = items.Item(displayChars.pipe_lrd,rowCounter,lineCounter)
                    item.walkable = True
                    itemsOnFloor.append(item)
                elif char == "s":
                    item = items.Item(displayChars.pipe_ld,rowCounter,lineCounter)
                    item.walkable = True
                    itemsOnFloor.append(item)
                elif char == "t":
                    item = items.Item(displayChars.pipe_lu,rowCounter,lineCounter)
                    item.walkable = True
                    itemsOnFloor.append(item)
                elif char == "u":
                    item = items.Item(displayChars.pipe_ru,rowCounter,lineCounter)
                    item.walkable = True
                    itemsOnFloor.append(item)
                elif char == "w":
                    item = items.Spray(rowCounter,lineCounter,direction="right")
                    itemsOnFloor.append(item)
                    self.sprays.append(item)
                elif char == "x":
                    item = items.Spray(rowCounter,lineCounter,direction="left")
                    itemsOnFloor.append(item)
                    self.sprays.append(item)
                elif char == "y":
                    itemsOnFloor.append(items.Item(displayChars.outlet,rowCounter,lineCounter))
                elif char == "j":
                    itemsOnFloor.append(items.Item(displayChars.vatSnake,rowCounter,lineCounter))
                elif char == "c":
                    item = items.Corpse(rowCounter,lineCounter)
                    itemsOnFloor.append(item)
                elif char == "C":
                    item = items.UnconciousBody(rowCounter,lineCounter)
                    itemsOnFloor.append(item)
                elif char == "z":
                    item = items.Item(displayChars.pipe_ud,rowCounter,lineCounter)
                    item.walkable = True
                    itemsOnFloor.append(item)
                elif char == "Ö":
                    item = items.GrowthTank(rowCounter,lineCounter,filled=True)
                    itemsOnFloor.append(item)
                elif char == "ö":
                    item = items.GrowthTank(rowCounter,lineCounter,filled=False)
                    itemsOnFloor.append(item)
                elif char == "B":
                    item = items.Item(displayChars.barricade,rowCounter,lineCounter)
                    item.walkable = True
                    itemsOnFloor.append(item)
                else:
                    itemsOnFloor.append(items.Item(displayChars.randomStuff2[((2*rowCounter)+lineCounter)%10],rowCounter,lineCounter))
                rowCounter += 1
                self.sizeX = rowCounter
            lineCounter += 1
        self.sizeY = lineCounter-1
        rawWalkingPath = []
        lineCounter = 0
        for line in self.layout[1:].split("\n"):
            rowCounter = 0
            for char in line:
                if char == ".":
                    rawWalkingPath.append((rowCounter,lineCounter))
                rowCounter += 1
            lineCounter += 1

        self.walkingPath = []
        startWayPoint = rawWalkingPath[0]
        endWayPoint = rawWalkingPath[0]

        self.walkingPath.append(rawWalkingPath[0])
        rawWalkingPath.remove(rawWalkingPath[0])

        while (1==1):
            endWayPoint = self.walkingPath[-1]
            east = (endWayPoint[0]+1,endWayPoint[1])
            west = (endWayPoint[0]-1,endWayPoint[1])
            south = (endWayPoint[0],endWayPoint[1]+1)
            north = (endWayPoint[0],endWayPoint[1]-1)
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

        self.addItems(itemsOnFloor)

    def getState(self):
        return { "offsetX":self.offsetX,
                 "offsetY":self.offsetY,
                 "xPosition":self.xPosition,
                 "yPosition":self.yPosition,
        }

    def setState(self,state):
        self.offsetX = state["offsetX"]
        self.offsetY = state["offsetY"]

        if not (self.xPosition == state["xPosition"] and self.yPosition == state["yPosition"]):
            self.terrain.teleportRoom(self,(state["xPosition"],state["yPosition"]))

    def changed(self):
        self.requestRedraw()
        pass

    def getResistance(self):
        return self.sizeX*self.sizeY

    def openDoors(self):
        for door in self.doors:
            door.open()
            self.open = True

    def closeDoors(self):
        for door in self.doors:
            door.close()
            self.open = False

    def render(self):
        if self.lastRender:
            return self.lastRender
        
        if not self.hidden:
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
            
            for item in self.itemsOnFloor:
                chars[item.yPosition][item.xPosition] = item.display

            for character in self.characters:
                chars[character.yPosition][character.xPosition] = character.display

            if mainChar.room == self:
                if len(mainChar.quests):
                        if not self.shownQuestmarkerLastRender:
                            self.shownQuestmarkerLastRender = True
                            for quest in mainChar.quests:
                                if not quest.active:
                                    continue
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
                                try:
                                    chars[mainChar.quests[0].dstY][mainChar.quests[0].dstX] = displayChars.questTargetMarker
                                except:
                                    pass
                            try:
                                path = calculatePath(mainChar.xPosition,mainChar.yPosition,mainChar.quests[0].dstX,mainChar.quests[0].dstY,self.walkingPath)
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
                            self.shownQuestmarkerLastRender = False

            if mainChar in self.characters:
                chars[mainChar.yPosition][mainChar.xPosition] = mainChar.display
        else:
            chars = []
            for i in range(0,self.sizeY):
                subChars = []
                for j in range(0,self.sizeX):
                    subChars.append(displayChars.invisibleRoom)
                chars.append(subChars)

            for item in self.itemsOnFloor:
                if item.xPosition == 0 or item.xPosition == self.sizeX-1 or item.yPosition == 0 or item.yPosition == self.sizeY-1:
                    chars[item.yPosition][item.xPosition] = item.display

        self.lastRender = chars

        return chars

    def forceRedraw(self):
        self.lastRender = None

    def requestRedraw(self):
        if not self.hidden:
            self.lastRender = None

    def addCharacter(self,character,x,y):
        self.characters.append(character)
        character.room = self
        character.xPosition = x
        character.yPosition = y

    def removeCharacter(self,character):
        self.characters.remove(character)
        character.room = None

    def addItems(self,items):
        self.itemsOnFloor.extend(items)
        for item in items:
            item.room = self
            if (item.xPosition,item.yPosition) in self.itemByCoordinates:
                self.itemByCoordinates[(item.xPosition,item.yPosition)].append(item)
            else:
                self.itemByCoordinates[(item.xPosition,item.yPosition)] = [item]

    def removeItem(self,item):
        self.itemByCoordinates[(item.xPosition,item.yPosition)].remove(item)
        if not self.itemByCoordinates[(item.xPosition,item.yPosition)]:
            del self.itemByCoordinates[(item.xPosition,item.yPosition)]
        self.itemsOnFloor.remove(item)

    def getAffectedByMovementNorth(self,initialMovement=True,force=1,movementBlock=set()):
        self.terrain.getAffectedByRoomMovementNorth(self,force=force,movementBlock=movementBlock)

        for thing in self.chainedTo:
            if thing not in movementBlock:
                movementBlock.add(thing)
                thing.getAffectedByMovementNorth(force=force,movementBlock=movementBlock)

        return movementBlock


    def moveNorth(self,force=1,initialMovement=True,movementBlock=set()):
        if initialMovement:
            movementBlock = set()
            movementBlock.add(self)
            self.getAffectedByMovementNorth(force=force,movementBlock=movementBlock)

            totalResistance = 0
            for thing in movementBlock:
                totalResistance += thing.getResistance()

            if totalResistance > force:
                messages.append("*CLUNK*")
                return

            for thing in movementBlock:
                if not thing == self:
                    thing.moveNorth(initialMovement=False)
        
        self.terrain.moveRoomNorth(self)
        messages.append("*RUMBLE*")


    def getAffectedByMovementSouth(self,initialMovement=True,force=1,movementBlock=set()):
        self.terrain.getAffectedByRoomMovementSouth(self,force=force,movementBlock=movementBlock)

        for thing in self.chainedTo:
            if thing not in movementBlock:
                movementBlock.add(thing)
                thing.getAffectedByMovementSouth(force=force,movementBlock=movementBlock)

        return movementBlock

    def moveSouth(self,force=1,initialMovement=True,movementBlock=set()):
        if initialMovement:
            movementBlock = set()
            movementBlock.add(self)
            self.getAffectedByMovementSouth(force=force,movementBlock=movementBlock)

            totalResistance = 0
            for thing in movementBlock:
                totalResistance += thing.getResistance()

            if totalResistance > force:
                messages.append("*CLUNK*")
                return

            for thing in movementBlock:
                if not thing == self:
                    thing.moveSouth(initialMovement=False)
        
        self.terrain.moveRoomSouth(self)
        messages.append("*RUMBLE*")

    def getAffectedByMovementWest(self,initialMovement=True,force=1,movementBlock=set()):
        self.terrain.getAffectedByRoomMovementWest(self,force=force,movementBlock=movementBlock)

        for thing in self.chainedTo:
            if thing not in movementBlock:
                movementBlock.add(thing)
                thing.getAffectedByMovementWest(force=force,movementBlock=movementBlock)

        return movementBlock

    def moveWest(self,initialMovement=True,force=1,movementBlock=set()):
        if initialMovement:
            movementBlock = set()
            movementBlock.add(self)
            self.getAffectedByMovementWest(force=force,movementBlock=movementBlock)

            totalResistance = 0
            for thing in movementBlock:
                totalResistance += thing.getResistance()

            if totalResistance > force:
                messages.append("*CLUNK*")
                return

            for thing in movementBlock:
                if not thing == self:
                    thing.moveWest(initialMovement=False)
        
        self.terrain.moveRoomWest(self)
        messages.append("*RUMBLE*")

    def getAffectedByMovementEast(self,force=1,movementBlock=set()):
        self.terrain.getAffectedByRoomMovementEast(self,force=force,movementBlock=movementBlock)

        for thing in self.chainedTo:
            if thing not in movementBlock:
                movementBlock.add(thing)
                thing.getAffectedByMovementEast(force=force,movementBlock=movementBlock)

        return movementBlock

    def moveEast(self,initialMovement=True, movementToken=None,force=1):
        if initialMovement:
            movementBlock = set()
            movementBlock.add(self)
            self.getAffectedByMovementEast(force=force,movementBlock=movementBlock)

            totalResistance = 0
            for thing in movementBlock:
                totalResistance += thing.getResistance()

            if totalResistance > force:
                messages.append("*CLUNK*")
                return

            for thing in movementBlock:
                if not thing == self:
                    thing.moveEast(initialMovement=False)
        
        self.terrain.moveRoomEast(self)
        messages.append("*RUMBLE*")


    def moveCharacterNorth(self,character):
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

        newPosition = (character.xPosition,character.yPosition-1)
        return self.moveCharacter(character,newPosition)

    def moveCharacterSouth(self,character):
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

        newPosition = (character.xPosition,character.yPosition+1)
        return self.moveCharacter(character,newPosition)

    def moveCharacterWest(self,character):
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

        newPosition = (character.xPosition-1,character.yPosition)
        return self.moveCharacter(character,newPosition)

    def moveCharacterEast(self,character):
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

        newPosition = (character.xPosition+1,character.yPosition)
        return self.moveCharacter(character,newPosition)

    def moveCharacter(self,character,newPosition):
        if newPosition in self.itemByCoordinates:
            for item in self.itemByCoordinates[newPosition]:
                if not item.walkable:
                    return item
            else:
                character.xPosition = newPosition[0]
                character.yPosition = newPosition[1]
        character.xPosition = newPosition[0]
        character.yPosition = newPosition[1]
        character.changed()
        return None

    def applySkippedAdvances(self):
        while self.delayedTicks > 0:
            for character in self.characters:
                character.advance()
            self.delayedTicks -= 1

    def addEvent(self,event):
        index = 0
        for existingEvent in self.events:
            if event.tick < existingEvent.tick:
                break
            index += 1
        self.events.insert(index,event)

    def removeEvent(self,event):
        self.events.remove(event)

    def removeEventsByType(self,eventType):
        for event in self.events:
            if type(event) == eventType:
                self.events.remove(event)

    def advance(self):
        self.timeIndex += 1
        self.requestRedraw()

        while self.events and self.timeIndex >  self.events[0].tick:
            event = self.events[0]
            debugMessages.append("something went wrong and event"+str(event)+"was skipped")
            self.events.remove(event)
        while self.events and self.timeIndex == self.events[0].tick:
            event = self.events[0]
            event.handleEvent()
            self.events.remove(event)

        if not self.hidden:
            if self.delayedTicks > 0:
                self.applySkippedAdvances()
            
            for character in self.characters:
                character.advance()
        else:
            self.delayedTicks += 1
    
class Room1(Room):
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

class Room2(Room):
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

        self.lever1 = items.Lever(3,6,"engine control")
        self.lever2 = items.Lever(1,2,"boarding alarm")

        coalPile1 = items.Pile(8,3,"coal Pile1",items.Coal)
        coalPile2 = items.Pile(8,4,"coal Pile2",items.Coal)
        coalPile3 = items.Pile(8,5,"coal Pile3",items.Coal)
        coalPile4 = items.Pile(8,6,"coal Pile4",items.Coal)
        self.furnace1 = items.Furnace(6,3,"Furnace")
        self.furnace2 = items.Furnace(6,4,"Furnace")
        self.furnace3 = items.Furnace(6,5,"Furnace")

        self.addItems([self.lever1,self.lever2,coalPile1,coalPile2,coalPile3,coalPile4,self.furnace])

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
        npc = Character(staffCharacters[11],1,2,name="Erwin von Libwig")
        self.addCharacter(npc,1,3)
        npc.room = self
        npc.assignQuest(quest0)
        #npc.automated = False

        lever2 = self.lever2
        def lever2action(self):
            deactivateLeaverQuest = quests.ActivateQuest(lever2,desiredActive=False)
            npc.assignQuest(deactivateLeaverQuest,active=True)
        self.lever2.activateAction = lever2action

class TutorialMachineRoom(Room):
    def __init__(self,xPosition=0,yPosition=1,offsetX=4,offsetY=0,desiredPosition=None):
        roomLayout = """
X#XX$XXX#X
X#Pv vID#X
X#......#X
X .@@@@. X
X .HHHH. X
X ...... X
XFFFFFFFFX
XOOOOOOOOX
X#########
XXXXXXXXXX
"""
        super().__init__(roomLayout,xPosition,yPosition,offsetX,offsetY,desiredPosition)
        self.name = "Boilerroom"

        self.lever1 = items.Lever(1,5,"engine control")
        self.lever2 = items.Lever(8,5,"boarding alarm")

        coalPile1 = items.Pile(8,3,"coal Pile1",items.Coal)
        coalPile2 = items.Pile(8,4,"coal Pile2",items.Coal)
        coalPile3 = items.Pile(1,3,"coal Pile1",items.Coal)
        coalPile4 = items.Pile(1,4,"coal Pile2",items.Coal)

        self.addItems([self.lever1,self.lever2,coalPile1,coalPile2,coalPile3,coalPile4])

        self.furnaceQuests = []

    def endTraining(self):
        class ChangeRequirements(object):
            def __init__(subself,tick):
                subself.tick = tick
                self.loop = [0,1,2,7,4,3,5,6]

            def handleEvent(subself):
                index = self.loop.index(self.desiredSteamGeneration)
                index += 1
                if index < len(self.loop):
                    messages.append("*comlink*: changed orders. please generate "+str(self.loop[index])+" power")
                    self.desiredSteamGeneration = self.loop[index]
                else:
                    self.desiredSteamGeneration = self.loop[0]
                    
                self.changed()
                self.addEvent(ChangeRequirements(self.timeIndex+50))

        self.desiredSteamGeneration = 0
        self.changed()
        self.addEvent(ChangeRequirements(self.timeIndex+20))
        
    def changed(self):
        self.terrain.tutorialVatProcessing.recalculate()
        if self.desiredSteamGeneration:
            if not self.desiredSteamGeneration == self.steamGeneration:
                if self.firstOfficer:
                    numFurnaces = len(self.furnaceQuests)
                    diff = self.desiredSteamGeneration - numFurnaces
                    while diff > 0:
                        officer = self.firstOfficer
                        if self.secondOfficer and numFurnaces < 4:
                            officer = self.secondOfficer
                        quest = quests.KeepFurnaceFired(self.furnaces[7-numFurnaces])
                        officer.assignQuest(quest)

                        self.furnaceQuests.append(quest)
                        diff -= 1
                        numFurnaces += 1
                    while diff < 0:
                        quest = self.furnaceQuests[-1]
                        quest.deactivate()
                        self.furnaceQuests.remove(quest)

                        diff += 1
                        numFurnaces -= 1
                    
                    
            else:
                messages.append("we did it! "+str(self.desiredSteamGeneration)+" instead of "+str(self.steamGeneration))

class Room3(Room):
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

class Room4(Room):
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

class GenericRoom(Room):
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

class CpuWasterRoom(Room):
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

        def addNPC(x,y):
            #TODO: replace with patrol quest since it's actually bugging
            quest1 = quests.MoveQuest(self,2,2)
            quest2 = quests.MoveQuest(self,2,7)
            quest3 = quests.MoveQuest(self,7,7)
            quest4 = quests.MoveQuest(self,7,2)
            quest1.followUp = quest2
            quest2.followUp = quest3
            quest3.followUp = quest4
            quest4.followUp = quest1
            npc = Character(displayChars.staffCharactersByLetter["l"],x,y,name="Erwin von Libwig")
            self.addCharacter(npc,x,y)
            npc.room = self
            npc.assignQuest(quest1)
            return npc

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
        
        class Event(object):
            def __init__(subself,tick):
                subself.tick = tick

            def handleEvent(subself):
                self.applySkippedAdvances()

class StorageRoom(Room):
    def __init__(self,xPosition,yPosition,offsetX,offsetY,desiredPosition=None):
        self.roomLayout = """
XX&XX&XX&XX
X?....?? ?X
X?.??.?? ?X
X?.??.?? ?X
X?.??.?? ?X
X?....   ?X
X? ?? ?? ?X
X? ?? ?? ?X
X? ?v v? ?X
XX&XX$XX&XX
"""
        super().__init__(roomLayout,xPosition,yPosition,offsetX,offsetY,desiredPosition)
        self.maxStorage = 2
        self.store = {}

class InfanteryQuarters(Room):
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
    
class FreePlacemenRoom(Room):
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

class Vat1(Room):
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
        self.gooDispenser = items.GooDispenser(6,7)
        self.addItems([self.gooDispenser])

    def recalculate(self):
        for spray in self.sprays:
            spray.recalculate()

class Vat2(Room):
    def __init__(self,xPosition,yPosition,offsetX,offsetY,desiredPosition=None):
        self.roomLayout = """
XXXXXXXXXX
X   b jjjX
X  ......X
X b.b bb.X
X .. c b.X
X .b  j .X
X .. b b.X
X b. ....X
## ...v ##
XXXXX$XXXX
"""
        super().__init__(self.roomLayout,xPosition,yPosition,offsetX,offsetY,desiredPosition)
        self.floorDisplay = displayChars.acids

class MechArmor(Room):
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

class MiniMech(Room):
    def __init__(self,xPosition,yPosition,offsetX,offsetY,desiredPosition=None):
        self.roomLayout = """
XX$XXX
XD.. X
Xm .PX
XOF.PX
Xmm.PX
XXXXXX
"""
        super().__init__(self.roomLayout,xPosition,yPosition,offsetX,offsetY,desiredPosition)
        self.floorDisplay = [displayChars.nonWalkableUnkown]
        self.gogogo = False
        self.engineStrength = 0

        self.npc = Character(displayChars.staffCharacters[12],3,3,name="Friedrich Engelbart")
        self.addCharacter(self.npc,3,3)
        self.npc.room = self

    def changed(self):
        self.engineStrength = 250*self.steamGeneration

class LabRoom(Room):
    def __init__(self,xPosition,yPosition,offsetX,offsetY,desiredPosition=None):
        self.roomLayout = """
XXXXXXXXXX
X        X
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

class CargoRoom(Room):
    def __init__(self,xPosition,yPosition,offsetX,offsetY,desiredPosition=None):
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

        self.storedItems = []
        for i in range(1,20):
            self.storedItems.append(items.Pipe())

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

        counter = 0
        for item in self.storedItems:
            item.xPosition = self.storageSpace[counter][0]
            item.yPosition = self.storageSpace[counter][1]
            counter += 1

        self.addItems(self.storedItems)

class WakeUpRoom(Room):
    def __init__(self,xPosition,yPosition,offsetX,offsetY,desiredPosition=None):
        self.roomLayout = """
XXXXXXXX
Xö    vX
XÖ ... $
XÖ . .vX
XÖ . . X
XÖ . . X
XÖ . . X
XÖ . . X
XÖ ... X
XÖ     X
XXXXXXXX
"""
        super().__init__(self.roomLayout,xPosition,yPosition,offsetX,offsetY,desiredPosition)

        self.lever1 = items.Lever(3,1,"engine control")
        self.objectDispenser = items.OjectDispenser(4,1)
        self.gooDispenser = items.GooDispenser(5,9)
        self.furnace = items.Furnace(4,9)
        self.pile = items.Pile(6,9)

        def activateDispenser(dispenser):
            self.objectDispenser.dispenseObject()

        self.lever1.activateAction = activateDispenser

        self.addItems([self.lever1,self.gooDispenser,self.objectDispenser,self.furnace,self.pile])

class WaitingRoom(Room):
    def __init__(self,xPosition,yPosition,offsetX,offsetY,desiredPosition=None):
        self.roomLayout = """
XXXXXXXXXXX
X         X
X  .....  X
X  .   .  X
X  .   .  $
X  .   . IX
X  ..... DX
X         X
X         X
XXXXXXXXXXX
"""
        super().__init__(self.roomLayout,xPosition,yPosition,offsetX,offsetY,desiredPosition)

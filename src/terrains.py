############################################################################################
###
##    terrains and terrain related code belongs here
#
############################################################################################

# import basic libs
import json

# import basic internal libs
import src.items
import src.rooms
import src.overlays
import src.gameMath
import src.saveing

# bad code: global varaibles
mainChar = None
messages = None
displayChars = None

'''
a abstracted coordinate.
bad code: is not used in all places
'''
class Coordinate(object):
    '''
    straightforward state initialization
    '''
    def __init__(self,x,y):
        self.x = x
        self.y = y

'''
the base class for terrains
'''
class Terrain(src.saveing.Saveable):

    '''
    straightforward state initialization
    '''
    def __init__(self,layout="",detailedLayout="",creator=None,seed=0, noPaths=False, noContent=False):
        super().__init__()

        self.noPaths = noPaths

        # store terrain content
        #self.itemsOnFloor = []
        self.characters = []
        self.rooms = []
        self.floordisplay = displayChars.floor
        self.itemsByCoordinate = {}
        self.roomByCoordinates = {}
        self.listeners = {"default":[]}
        self.initialSeed = seed
        self.seed = seed
        self.events = []
        self.biomeInfo = {"wet":2}

        # set id
        import uuid
        self.id = uuid.uuid4().hex
            
        # misc state
        self.overlay = None
        self.alarm = False

        if not noContent:
            # add items 
            # bad code: repetetive code
            mapItems = []
            self.detailedLayout = detailedLayout
            lineCounter = 0
            for layoutline in self.detailedLayout.split("\n")[1:]:
                rowCounter = 0
                for char in layoutline:
                    if char in (" ",".",",","@"):
                        pass
                    elif char == "X":
                        mapItems.append(src.items.Wall(rowCounter,lineCounter,creator=self))
                    elif char == "#":
                        mapItems.append(src.items.Pipe(rowCounter,lineCounter,creator=self))
                    elif char == "R":
                        pass
                    elif char == "O":
                        mapItems.append(src.items.Item(displayChars.clamp_active,rowCounter,lineCounter,creator=self))
                    elif char == "0":
                        mapItems.append(src.items.Item(displayChars.clamp_inactive,rowCounter,lineCounter,creator=self))
                    elif char == "8":
                        mapItems.append(src.items.Chain(rowCounter,lineCounter,creator=self))
                    elif char == "C":
                        mapItems.append(src.items.Winch(rowCounter,lineCounter,creator=self))
                    elif char == "P":
                        mapItems.append(src.items.Pile(rowCounter,lineCounter,creator=self))
                    else:
                        mapItems.append(src.items.Item(displayChars.randomStuff2[((2*rowCounter)+lineCounter)%10],rowCounter,lineCounter,creator=self))
                    rowCounter += 1
                lineCounter += 1
            self.addItems(mapItems)

        # container for categories of rooms for easy access
        # bad code: should be abstracted
        roomsOnMap = []
        self.tutorialVat = None
        self.tutorialVatProcessing = None
        self.tutorialMachineRoom = None
        self.tutorialLab = None
        self.challengeRooms = []
        self.tutorialCargoRooms = []
        self.tutorialStorageRooms = []
        self.miniMechs = []
        self.wakeUpRoom = None
        self.militaryRooms = []

        # nodes for pathfinding
        self.watershedStart = []
        self.superNodes = {}

        if not noContent:
            # add rooms
            # bad code: this should be abstracted
            # bad code: repetetive code
            # bad code: watershed coordinates should not be set here
            lineCounter = 0
            for layoutline in layout.split("\n")[1:]:
                rowCounter = 0
                for char in layoutline:
                    if char in (".",","," ","t"):
                        # add starting points for pathfinding
                        self.watershedStart.extend([(rowCounter*15+1,lineCounter*15+1),(rowCounter*15+13,lineCounter*15+1),(rowCounter*15+1,lineCounter*15+13),(rowCounter*15+13,lineCounter*15+13)])
                        if char in ("."):
                            # add starting point for higher level pathfinding
                            self.superNodes[(rowCounter,lineCounter)] = (rowCounter*15+1,lineCounter*15+1)

                    if char in (".",","," "):
                        # ignore paths
                        pass
                    elif char == "X":
                        # add armor plating
                        roomsOnMap.append(src.rooms.MechArmor(rowCounter,lineCounter,0,0,creator=self))
                    elif char == "V":
                        # add vat and save first reference
                        room = src.rooms.VatFermenting(rowCounter,lineCounter,2,2,creator=self)
                        if not self.tutorialVat:
                            self.tutorialVat = room
                        roomsOnMap.append(room)
                    elif char == "v":
                        # add vat and save first reference
                        room = src.rooms.VatProcessing(rowCounter,lineCounter,2,2,creator=self)
                        if not self.tutorialVatProcessing:
                            self.tutorialVatProcessing = room
                        roomsOnMap.append(room)
                    elif char == "Q":
                        # add room and add to room list
                        room = src.rooms.InfanteryQuarters(rowCounter,lineCounter,1,2,creator=self)
                        roomsOnMap.append(room)
                        self.militaryRooms.append(room)

                        # add terrain wide listener
                        self.addListener(room.enforceFloorPermit,"entered terrain")
                    elif char == "w":
                        # add room and add to room list
                        room = src.rooms.WaitingRoom(rowCounter,lineCounter,1,2,creator=self)
                        self.waitingRoom = room
                        roomsOnMap.append(room)
                    elif char == "M":
                        # add room and add to room list
                        room = src.rooms.TutorialMachineRoom(rowCounter,lineCounter,4,1,creator=self)
                        if not self.tutorialMachineRoom:
                            self.tutorialMachineRoom = room
                        roomsOnMap.append(room)
                    elif char == "L":
                        # add room and add to room list
                        room = src.rooms.LabRoom(rowCounter,lineCounter,1,1,creator=self)
                        if not self.tutorialLab:
                            self.tutorialLab = room
                        roomsOnMap.append(room)
                    elif char == "l":
                        # add room and add to room list
                        room = src.rooms.ChallengeRoom(rowCounter,lineCounter,3,1,creator=self,seed=seed+rowCounter-3*lineCounter)
                        self.challengeRooms.append(room)
                        roomsOnMap.append(room)
                    elif char == "C":
                        # generate pseudo random content type
                        itemTypes = [src.items.Wall,src.items.Pipe]
                        amount = 40
                        if not (rowCounter+seed)%2:
                            itemTypes.append(src.items.Lever)
                            amount += 10
                        if not (rowCounter+seed)%3:
                            itemTypes.append(src.items.Furnace)
                            amount += 15
                        if not (rowCounter+seed)%4:
                            itemTypes.append(src.items.Chain)
                            amount += 20
                        if not (rowCounter+seed)%5:
                            itemTypes.append(src.items.Hutch)
                            amount += 7
                        if not (rowCounter+seed)%6:
                            itemTypes.append(src.items.GrowthTank)
                            amount += 8
                        if not (lineCounter+seed)%2:
                            itemTypes.append(src.items.Door)
                            amount += 15
                        if not (lineCounter+seed)%3:
                            itemTypes.append(src.items.Boiler)
                            amount += 10
                        if not (lineCounter+seed)%4:
                            itemTypes.append(src.items.Winch)
                            amount += 7
                        if not (lineCounter+seed)%5:
                            itemTypes.append(src.items.RoomControls)
                            amount += 7
                        if not (lineCounter+seed)%6:
                            itemTypes.append(src.items.Commlink)
                            amount += 7
                        if not itemTypes:
                            itemTypes = [src.items.Pipe,src.items.Wall,src.items.Furnace,src.items.Boiler]
                            amount += 30
                        while amount > 80:
                            amount -= seed%40+1

                        # add room and add to room list
                        room = src.rooms.CargoRoom(rowCounter,lineCounter,3,0,itemTypes=itemTypes,amount=amount,creator=self,seed=seed+2*rowCounter+5*lineCounter//7)
                        self.tutorialCargoRooms.append(room)
                        roomsOnMap.append(room)
                    elif char == "h":
                        # add room and add to room list
                        room = src.rooms.HuntersLodge(rowCounter,lineCounter,3,0,creator=self)
                        self.huntersLodge = room
                        roomsOnMap.append(room)
                    elif char == "U":
                        # add room and add to room list
                        room = src.rooms.StorageRoom(rowCounter,lineCounter,3,0,creator=self)
                        self.tutorialStorageRooms.append(room)
                    elif char == "?":
                        # add room and add to room list
                        roomsOnMap.append(src.rooms.CpuWasterRoom(rowCounter,lineCounter,2,2,creator=self))
                    elif char == "t":
                        # add room and add to room list
                        miniMech = src.rooms.MiniMech(rowCounter,lineCounter,2,2,creator=self)
                        self.miniMechs.append(miniMech)
                        roomsOnMap.append(miniMech)
                    elif char == "W":
                        # add room and add to room list
                        wakeUpRoom = src.rooms.WakeUpRoom(rowCounter,lineCounter,1,1,creator=self)
                        self.wakeUpRoom = wakeUpRoom
                        roomsOnMap.append(wakeUpRoom)
                    elif char == "m":
                        # add room and add to room list
                        room = src.rooms.MetalWorkshop(rowCounter,lineCounter,1,1,creator=self,seed=seed+3*rowCounter+2*lineCounter//8)
                        self.metalWorkshop = room
                        roomsOnMap.append(room)
                    elif char == "b":
                        # add room and add to room list
                        room = src.rooms.ConstructionSite(rowCounter,lineCounter,1,1,creator=self)
                        roomsOnMap.append(room)
                    elif char == "K":
                        # add room and add to room list
                        room = src.rooms.MechCommand(rowCounter,lineCounter,1,1,creator=self)
                        roomsOnMap.append(room)
                    else:
                        # add starting points for pathfinding
                        self.watershedStart.append((rowCounter*15+7,lineCounter*15+7))
                        pass
                    rowCounter += 1
                lineCounter += 1

            # actually add the rooms to the map
            self.addRooms(roomsOnMap)

        # set meta information for saving
        self.attributesToStore.extend([
              "yPosition","xPosition",
                ])

    def getItemByPosition(self,position):

        if position[0]%15 == 0:
            if position[1]%15 < 7:
                position = (position[0]+1,position[1]+1,position[2])
            elif position[1]%15 > 7:
                position = (position[0]+1,position[1]-1,position[2])
        if position[0]%15 == 14:
            if position[1]%15 < 7:
                position = (position[0]-1,position[1]+1,position[2])
            elif position[1]%15 > 7:
                position = (position[0]-1,position[1]-1,position[2])
        if position[1]%15 == 0:
            if position[0]%15 < 7:
                position = (position[0]+1,position[1]+1,position[2])
            elif position[0]%15 > 7:
                position = (position[0]-1,position[1]+1,position[2])
        if position[1]%15 == 14:
            if position[0]%15 < 7:
                position = (position[0]+1,position[1]-1,position[2])
            elif position[0]%15 > 7:
                position = (position[0]-1,position[1]-1,position[2])

        try:
            return self.itemsByCoordinate[(position[0],position[1],position[2])]
        except KeyError:
            return []

    def runner1(self):
        room = None
        for room in self.rooms:
            if isinstance(room,src.rooms.VatFermenting):
                break
        if room:
            quest = src.quests.MoveQuestMeta(room,5,8,creator=self)
            quest.endTrigger = {"container":self,"method":"runner2"}
            self.runner.assignQuest(quest,active=True)

    def runner2(self):
        for room in reversed(self.rooms):
            if isinstance(room,src.rooms.VatFermenting):
                break
        quest = src.quests.MoveQuestMeta(room,5,8,creator=self)
        quest.endTrigger = {"container":self,"method":"runner1"}
        self.runner.assignQuest(quest,active=True)

    '''
    registering for notifications
    bad code: should be an extra class
    '''
    def addListener(self,listenFunction,tag="default"):
        if not tag in self.listeners:
            self.listeners[tag] = []

        if not listenFunction in self.listeners[tag]:
            self.listeners[tag].append(listenFunction)

    '''
    deregistering for notifications
    bad code: should be an extra class
    '''
    def delListener(self,listenFunction,tag="default"):
        if listenFunction in self.listeners[tag]:
            self.listeners[tag].remove(listenFunction)

        if not self.listeners[tag]:
            del self.listeners[tag]

    '''
    sending notifications
    bad code: probably misnamed
    bad code: should be an extra class
    '''
    def changed(self,tag="default",info=None):
        if not tag == "default":
            if not tag in self.listeners:
                return

            for listenFunction in self.listeners[tag]:
                listenFunction(info)
        for listenFunction in self.listeners["default"]:
            listenFunction()

    '''
    create a map of non passable tiles
    '''
    def setNonMovableMap(self):
        return
        self.nonMovablecoordinates = {}

        # add non movable items
        for coordinate,itemList in self.itemByCoordinates.items():
            for item in itemList:
                if not item.walkable:
                    self.nonMovablecoordinates[coordinate] = True

        # add rooms
        for room in self.rooms:
            for x in range(room.xPosition*15+room.offsetX,room.xPosition*15+room.offsetX+room.sizeX):
                for y in range(room.yPosition*15+room.offsetY,room.yPosition*15+room.offsetY+room.sizeY):
                     self.nonMovablecoordinates[(x,y)] = True

    '''
    precalculate pathfinding data
    '''
    def calculatePathMap(self):

        # container for pathfinding information
        self.watershedNodeMap = {}
        self.foundPaths = {}
        self.applicablePaths = []
        self.obseveredCoordinates = {}
        self.superNodePaths = {}
        self.watershedSuperNodeMap = {}
        self.watershedSuperCoordinates = {}
        self.foundSuperPaths = {}
        self.foundSuperPathsComplete = {}

        self.setNonMovableMap()
        self.watershedCoordinates = {}

        return
        if self.noPaths:
            return

        # place starting points for pathfinding next to doors
        for room in self.rooms:
            # ignore rooms intended to be moved
            if room in self.miniMechs:
                continue

            # get the coordiate of the door
            xCoord = room.xPosition*15+room.offsetX+room.walkingAccess[0][0]
            yCoord = room.yPosition*15+room.offsetY+room.walkingAccess[0][1]

            # mark door as movable
            if (xCoord,yCoord) in self.nonMovablecoordinates:
                del self.nonMovablecoordinates[(xCoord,yCoord)]

            # get coordinate in front of the door
            if room.walkingAccess[0][0] == 0:
                xCoord -= 1
            elif room.walkingAccess[0][0] == room.sizeX-1:
                xCoord += 1
            if room.walkingAccess[0][1] == 0:
                yCoord -= 1
            elif room.walkingAccess[0][1] == room.sizeY-1:
                yCoord += 1

            # add the starting point
            self.watershedStart.append((xCoord,yCoord))

        # container for pathfinding information
        self.watershedCoordinates = {}

        # try to find paths between all nodes by placing growing circles around the starting points until the meet each other
        last = {}
        for coordinate in self.watershedStart:
            self.watershedNodeMap[coordinate] = []
            self.watershedCoordinates[coordinate] = (coordinate,0)
            last[coordinate] = [coordinate]
        self.watershed(0,last)

        # try to connect the super nodes using the paths between the nodes
        # bad code: redudant code with the pathfinding between nodes
        last = {}
        for bigCoord,smallCoord in self.superNodes.items():
            self.watershedSuperNodeMap[smallCoord] = []

            self.watershedSuperCoordinates[smallCoord] = (smallCoord,0)
            last[smallCoord] = [smallCoord]
        self.superWatershed(0,last)

        # try to find paths between all nodes by placing growing circles around the starting points until the meet each other
        self.superNodePaths
        self.overlay = self.addWatershedOverlay
        self.overlay = None

    '''
    get a path to node from within the nodes section
    result is not returned instead an argument is modified to store the result
    '''
    def walkBack(self,coordinate,bucket,path,last=1000):

        # get neighbouring coordinates
        testCoordinates = [(coordinate[0]-1,coordinate[1]),(coordinate[0]+1,coordinate[1]),(coordinate[0],coordinate[1]-1),(coordinate[0],coordinate[1]+1)]
        nextStep = (None,(None,last))

        # select step leading back to node
        for testCoordinate in testCoordinates:

            # skip coordinates that were not mapped
            if not testCoordinate in self.watershedCoordinates:
                continue

            # get node for coordinate
            value = self.watershedCoordinates[testCoordinate]

            # stay within the current section
            if not value[0] == bucket:
                continue

            # select tile with lower distance to node
            if value[1] < nextStep[1][1]:
                nextStep = (testCoordinate,value)
            
        # continue till no improvement
        if nextStep[1][1] < last:
            path.append(nextStep[0])
            self.walkBack(nextStep[0],bucket,path,last=nextStep[1][1]+1)

    '''
    expand the section around a node in a circular pattern until it reaches the section of another node and connect them
    '''
    def watershed(self,counter,lastCoordinates):

        # limit size to not destroy performace/get endless loops
        counter += 1
        if counter > 60:
            return

        # extend the size of each bucket/starting point
        newLast = {}
        for start,coordinates in lastCoordinates.items():
            newLastList = []

            # expand each coordinate
            for coordinate in coordinates:

                # add applicable neighbour coordinates
                newCoordinates = [(coordinate[0]-1,coordinate[1]),(coordinate[0]+1,coordinate[1]),(coordinate[0],coordinate[1]-1),(coordinate[0],coordinate[1]+1)]
                for newCoordinate in newCoordinates:
                     
                    # ignore non walkable terrain
                    if newCoordinate in self.nonMovablecoordinates:
                        continue

                    # handle hitting another section
                    if newCoordinate in self.watershedCoordinates:
                        # skip sections with a known path
                        partnerNode = self.watershedCoordinates[newCoordinate][0]
                        if partnerNode == start:
                            continue
                        if (start,partnerNode) in self.foundPaths or (partnerNode,start) in self.foundPaths:
                            continue

                        # add path from node to intersection
                        path = []
                        self.walkBack(newCoordinate,start,path)
                        path.reverse()
                        path.append(newCoordinate)

                        # add path from intersection to partner node
                        self.walkBack(newCoordinate,partnerNode,path)
                        self.foundPaths[(start,partnerNode)] = path
                        path = path[:]
                        path.reverse()

                        # save path
                        self.foundPaths[(partnerNode,start)] = path
                        continue

                    # add coordinates to section
                    newLastList.append(newCoordinate)
                    self.watershedCoordinates[newCoordinate] = (start,counter)

            # store the coordinates visited for next interaction
            newLast[start] = newLastList

        # recursivly increase section
        self.watershed(counter,newLast)

        # add found path between nodes to map
        for pair,path in self.foundPaths.items():
            if not pair[1] in self.watershedNodeMap[pair[0]]:
                self.watershedNodeMap[pair[0]].append(pair[1])
            if not pair[0] in [pair[1]]:
                self.watershedNodeMap[pair[1]].append(pair[0])

    '''
    get a path to supernode from within the supernodes section
    result is not returned but a modifcation of a argument
    bad code: similar to pathfinding for nodes
    '''
    def walkBackSuper(self,coordinate,bucket,path,last=1000):

        # get neighbouring nodes
        testCoordinates = self.watershedNodeMap[coordinate]
        nextStep = (None,(None,last))

        # select step leading back to super node
        for testCoordinate in testCoordinates:

            # skip coordinates that were not mapped
            if not testCoordinate in self.watershedSuperCoordinates:
                continue

            # get supernode for node
            value = self.watershedSuperCoordinates[testCoordinate]

            # stay within the current section
            if not value[0] == bucket:
                continue

            # select node with lower distance to supernode
            if value[1] < nextStep[1][1]:
                nextStep = (testCoordinate,value)

        # continue till no improvement
        if nextStep[1][1] < last:
            path.append(nextStep[0])
            self.walkBackSuper(nextStep[0],bucket,path,last=nextStep[1][1]+1)

    '''
    expand the section around a supernode in a circular pattern until it reaches the section of another supernode and connect them
    bad code: similar to pathfinding for nodes
    '''
    def superWatershed(self,counter,lastCoordinates):
        # limit size to not destroy performace/get endless loops
        counter += 1
        if counter > 60:
            return

        # extend the size of each bucket/starting point
        newLast = {}
        for start,coordinates in lastCoordinates.items():
            newLastList = []

            # expand each coordinate
            for coordinate in coordinates:

                # add applicable neighbour coordinates
                newCoordinates = self.watershedNodeMap[coordinate]
                for newCoordinate in newCoordinates:

                    # handle hitting another section
                    if newCoordinate in self.watershedSuperCoordinates:
                        # skip sections with a known path
                        partnerSuperNode = self.watershedSuperCoordinates[newCoordinate][0]
                        if partnerSuperNode == start:
                            continue
                        if (start,partnerSuperNode) in self.foundSuperPaths or (partnerSuperNode,start) in self.foundSuperPaths:
                            continue

                        # add path from supernode to intersection
                        path = []
                        self.walkBackSuper(newCoordinate,start,path)
                        path.reverse()
                        path.append(newCoordinate)

                        # add path from intersection to supernode
                        self.walkBackSuper(newCoordinate,partnerSuperNode,path)
                        self.foundSuperPaths[(partnerSuperNode,start)] = path
                        self.foundSuperPaths[(start,partnerSuperNode)] = path

                        # save path
                        last = path[0]
                        completePath = [last]
                        for waypoint in path[1:]:
                            completePath.extend(self.foundPaths[(last,waypoint)][1:])
                            last = waypoint
                        self.foundSuperPathsComplete[(start,partnerSuperNode)] = completePath[1:]
                        completePath = completePath[:-1]
                        completePath.reverse()
                        self.foundSuperPathsComplete[(partnerSuperNode,start)] = completePath
                        continue

                    # add nodes to section
                    newLastList.append(newCoordinate)
                    self.watershedSuperCoordinates[newCoordinate] = (start,counter)

            # store the nodes visited for next iteration
            newLast[start] = newLastList

        # add found path between supernodes to map
        for pair,path in self.foundSuperPaths.items():
            if not pair[1] in self.watershedSuperNodeMap[pair[0]]:
                self.watershedSuperNodeMap[pair[0]].append(pair[1])

            if not pair[0] in self.watershedSuperNodeMap[pair[1]]:
                self.watershedSuperNodeMap[pair[1]].append(pair[0])

        # recursevly increase section
        self.superWatershed(counter,newLast)

    '''
    remove a character from the terrain
    '''
    def removeCharacter(self,character):
        self.characters.remove(character)
        character.room = None
        character.terrain = None

    def moveCharacterDirection(self,char,direction):
        if not char.terrain:
            return
        if not (char.xPosition and char.yPosition):
            return

        if direction == "west":
            if char.xPosition%15 == 1:
                if (char.yPosition%15 < 7):
                    direction = "south"
                elif (char.yPosition%15 > 7):
                    direction = "north"
                else:
                    if char.xPosition == 16:
                        return
                    else:
                        #char.stasis = True
                        char.macroState["commandKeyQueue"].insert(0,("a",["norecord"]))
                        char.macroState["commandKeyQueue"].insert(0,("a",["norecord"]))
                        pass
                char.addMessage("a force field pushes you")
        elif direction == "east":
            if char.xPosition%15 == 13:
                if (char.yPosition%15 < 7):
                    direction = "south"
                elif (char.yPosition%15 > 7):
                    direction = "north"
                else:
                    if char.xPosition == 15*14-2:
                        return
                    else:
                        #char.stasis = True
                        char.macroState["commandKeyQueue"].insert(0,("d",["norecord"]))
                        char.macroState["commandKeyQueue"].insert(0,("d",["norecord"]))
                        pass
                char.addMessage("a force field pushes you")
        elif direction == "north":
            if char.yPosition%15 == 1:
                if (char.xPosition%15 < 7):
                    direction = "east"
                elif (char.xPosition%15 > 7):
                    direction = "west"
                else:
                    if char.yPosition == 16:
                        return
                    else:
                        #char.stasis = True
                        char.macroState["commandKeyQueue"].insert(0,("w",["norecord"]))
                        char.macroState["commandKeyQueue"].insert(0,("w",["norecord"]))
                        pass
                char.addMessage("a force field pushes you")
        elif direction == "south":
            if char.yPosition%15 == 13:
                if (char.xPosition%15 < 7):
                    direction = "east"
                elif (char.xPosition%15 > 7):
                    direction = "west"
                else:
                    if char.yPosition == 15*14-2:
                        return
                    else:
                        #char.stasis = True
                        char.macroState["commandKeyQueue"].insert(0,("s",["norecord"]))
                        char.macroState["commandKeyQueue"].insert(0,("s",["norecord"]))
                        pass
                char.addMessage("a force field pushes you")
        if char.xPosition%15 in (0,14) and direction in ("north","south"):
            return
        if char.yPosition%15 in (0,14) and direction in ("east","west"):
            return


        # gather the rooms the character might have entered
        if direction == "north":
            bigX = (char.xPosition)//15
            bigY = (char.yPosition-1)//15
        elif direction == "south":
            bigX = (char.xPosition)//15
            bigY = (char.yPosition+1)//15
        elif direction == "east":
            bigX = (char.xPosition+1)//15
            bigY = (char.yPosition)//15
        elif direction == "west":
            bigX = (char.xPosition)//15
            bigY = (char.yPosition-1)//15

        # gather the rooms the player might step into
        roomCandidates = []
        for coordinate in [(bigX,bigY),
                           (bigX,bigY+1),(bigX+1,bigY+1),(bigX+1,bigY),(bigX+1,bigY-1),(bigX,bigY-1),(bigX-1,bigY-1),(bigX-1,bigY),(bigX-1,bigY+1),
                           (bigX-2,bigY),(bigX-2,bigY-1),(bigX-2,bigY-2),(bigX-1,bigY-2),(bigX,bigY-2),(bigX+1,bigY-2),(bigX+2,bigY-2),(bigX+2,bigY-1),
                           (bigX+2,bigY),(bigX+2,bigY-1),(bigX+2,bigY-2),(bigX+1,bigY-2),(bigX,bigY-2),(bigX-1,bigY-2),(bigX-2,bigY-2),(bigX-1,bigY-2),
                          ]:
            if coordinate in char.terrain.roomByCoordinates:
                for room in char.terrain.roomByCoordinates[coordinate]:
                    if not room in roomCandidates:
                        roomCandidates.append(room)

        '''
        move a player into a room
        bad code: inline function within inline function
        '''
        def enterLocalised(room,localisedEntry):

            # get the entry point in room coordinates
            if localisedEntry in room.walkingAccess:
                if localisedEntry in room.itemByCoordinates:
                    # check if the entry point is blocked (by a door)
                    for item in room.itemByCoordinates[localisedEntry]:

                        # handle collisions
                        if not item.walkable:
                            # print some info
                            if isinstance(item,src.items.itemMap["Door"]):
                                char.addMessage("you need to open the door first")
                            else:
                                char.addMessage("the entry is blocked")
                            #char.addMessage("press "+commandChars.activate+" to apply")
                            #if noAdvanceGame == False:
                            #    header.set_text((urwid.AttrSpec("default","default"),renderHeader(char)))

                            # remember the item for interaction and abort
                            return item

                    if len(room.itemByCoordinates[localisedEntry]) >= 15:
                        char.addMessage("the entry is blocked by items.")
                        #char.addMessage("press "+commandChars.activate+" to apply")
                        #if noAdvanceGame == False:
                        #    header.set_text((urwid.AttrSpec("default","default"),renderHeader(char)))
                        return room.itemByCoordinates[localisedEntry][0]

                char.changed("moved",direction)

                # teleport the character into the room
                room.addCharacter(char,localisedEntry[0],localisedEntry[1])
                try:
                    char.terrain.characters.remove(char)
                except:
                    char.addMessage("fail,fail,fail")

                return

            # do not move player into the room
            else:
                char.addMessage("you cannot move there")

        # check if character has entered a room
        hadRoomInteraction = False
        for room in roomCandidates:
            # check north
            if direction == "north":
                # check if the character crossed the edge of the room
                if room.yPosition*15+room.offsetY+room.sizeY == char.yPosition:
                    if room.xPosition*15+room.offsetX-1 < char.xPosition and room.xPosition*15+room.offsetX+room.sizeX > char.xPosition:
                        # get the entry point in room coordinates
                        hadRoomInteraction = True
                        localisedEntry = (char.xPosition%15-room.offsetX,char.yPosition%15-room.offsetY-1)
                        if localisedEntry[1] == -1:
                            localisedEntry = (localisedEntry[0],room.sizeY-1)

            # check south
            elif direction == "south":
                # check if the character crossed the edge of the room
                if room.yPosition*15+room.offsetY == char.yPosition+1:
                    if room.xPosition*15+room.offsetX-1 < char.xPosition and room.xPosition*15+room.offsetX+room.sizeX > char.xPosition:
                        # get the entry point in room coordinates
                        hadRoomInteraction = True
                        localisedEntry = ((char.xPosition-room.offsetX)%15,(char.yPosition-room.offsetY+1)%15)

            # check east
            elif direction == "east":
                # check if the character crossed the edge of the room
                if room.xPosition*15+room.offsetX == char.xPosition+1:
                    if room.yPosition*15+room.offsetY < char.yPosition+1 and room.yPosition*15+room.offsetY+room.sizeY > char.yPosition:
                        # get the entry point in room coordinates
                        hadRoomInteraction = True
                        localisedEntry = ((char.xPosition-room.offsetX+1)%15,(char.yPosition-room.offsetY)%15)

            # check west
            elif direction == "west":
                # check if the character crossed the edge of the room
                if room.xPosition*15+room.offsetX+room.sizeX == char.xPosition:
                    if room.yPosition*15+room.offsetY < char.yPosition+1 and room.yPosition*15+room.offsetY+room.sizeY > char.yPosition:
                        # get the entry point in room coordinates
                        hadRoomInteraction = True
                        localisedEntry = ((char.xPosition-room.offsetX-1)%15,(char.yPosition-room.offsetY)%15)

            # move player into the room
            if hadRoomInteraction:
                item = enterLocalised(room,localisedEntry)
                if item:
                    return item

                break

        # handle walking without room interaction
        if not hadRoomInteraction:
            # get the items on the destination coordinate 
            if direction == "north":
                destCoord = (char.xPosition,char.yPosition-1,char.zPosition)
            elif direction == "south":
                destCoord = (char.xPosition,char.yPosition+1,char.zPosition)
            elif direction == "east":
                destCoord = (char.xPosition+1,char.yPosition,char.zPosition)
            elif direction == "west":
                destCoord = (char.xPosition-1,char.yPosition,char.zPosition)

            foundItems = char.terrain.getItemByPosition(destCoord)

            # check for items blocking the move to the destination coordinate
            foundItem = None
            item = None
            for item in foundItems:
                if item and not item.walkable:
                    # print some info
                    char.addMessage("You cannot walk there")
                    #char.addMessage("press "+commandChars.activate+" to apply")
                    #if noAdvanceGame == False:
                    #    header.set_text((urwid.AttrSpec("default","default"),renderHeader(char)))

                    # remember the item for interaction and abort
                    foundItem = item
                    break
            if not foundItem:
                if len(foundItems) >= 15:
                    char.addMessage("the floor is too full to walk there")
                    #char.addMessage("press "+commandChars.activate+" to apply")
                    #if noAdvanceGame == False:
                    #    header.set_text((urwid.AttrSpec("default","default"),renderHeader(char)))

                    # remember the item for interaction and abort
                    foundItem = foundItems[0]

            if foundItem:
                foundItem = foundItems[0]

            # move the character
            if not foundItem:
                if direction == "north":
                    char.yPosition -= 1
                elif direction == "south":
                    char.yPosition += 1
                elif direction == "east":
                    char.xPosition += 1
                elif direction == "west":
                    char.xPosition -= 1
                char.changed()
                char.changed("moved",direction)

            return foundItem


    '''
    add a character to the terrain
    '''
    def addCharacter(self,character,x,y):
        self.characters.append(character)
        character.terrain = self
        character.room = None
        character.xPosition = x
        character.yPosition = y
        character.changed()
        self.changed("entered terrain",character)

    '''
    paint the information for the pathfinding
    bad code: is part visual debugging and partially looking nice, it still has to be integrated properly
    bad code: urwid specific code
    '''
    def addWatershedOverlay(self,chars):
        import urwid

        # define colors for the sections
        colors = ["#fff","#ff0","#f0f","#0ff","#f00","#0f0","#00f","#55f","#f55","#5f5","#055","#505","#550"]
        colorByType = {}

        # determine the section the player is in
        mainCharPair = None
        if mainChar.terrain:
            mainCharPair = self.watershedCoordinates[(mainChar.xPosition,mainChar.yPosition)][0]

        # assign the colors to the sections
        counter = 0
        for item in self.watershedStart:
            colorByType[item] = colors[counter%len(colors)]
            counter += 1

        # encode the distance to node as string and show instead of the normal terrain
        for coordinate,value in self.watershedCoordinates.items():
            if value[1] < 10:
                display = "0"+str(value[1])
            else:
                display = str(value[1])

            if mainCharPair == value[0]:
                chars[coordinate[1]][coordinate[0]] = (urwid.AttrSpec("#333","default"),display)
            else:
                chars[coordinate[1]][coordinate[0]] = (urwid.AttrSpec(colorByType[value[0]],"default"),display)

        # mark the paths between nodes
        counter = 3
        for dualPair,path in self.foundPaths.items():
            for coordinate in path:
                if dualPair in self.applicablePaths:
                    chars[coordinate[1]][coordinate[0]] =  (urwid.AttrSpec("#888","default"),"XX")
                else:
                    chars[coordinate[1]][coordinate[0]] =  (urwid.AttrSpec(colors[counter%len(colors)],"default"),"XX")
            counter += 1

        # show pathfinding to next node
        for newCoordinate,counter in self.obseveredCoordinates.items():
            if counter < 10:
                display = "0"+str(counter)
            else:
                display = str(counter)
            chars[newCoordinate[1]][newCoordinate[0]] =  (urwid.AttrSpec("#888","default"),display)

        chars[mainChar.yPosition][mainChar.xPosition] =  mainChar.display

    '''
    find path between start and end coordinates
    '''
    def findPath(self,start,end):

        # clear pathfinding state
        self.applicablePaths = {}
        self.obseveredCoordinates = {}

        # get start node
        if not start in self.watershedCoordinates:
            return
        startPair = self.watershedCoordinates[start][0]

        # get paths that can be taken from start node
        for dualPair,path in self.foundPaths.items():
            if startPair in dualPair:
                self.applicablePaths[dualPair] = path

        # get super node for start node
        if not startPair in self.watershedSuperCoordinates:
            return
        startSuper = self.watershedSuperCoordinates[startPair]

        # find path to any point an a path leading to the start node
        entryPoint = self.mark([start])
        if not entryPoint:
            return

        # get path from start position to start node
        startCoordinate = Coordinate(entryPoint[0][0],entryPoint[0][1])
        startNode = entryPoint[1][1]
        pathToStartNode = self.foundPaths[entryPoint[1]][self.foundPaths[entryPoint[1]].index((startCoordinate.x,startCoordinate.y))+1:]

        # clear pathfinding state
        self.applicablePaths = {}
        self.obseveredCoordinates = {}

        # get end node
        ends = (end,(end[0]-1,end[1]),(end[0]+1,end[1]),(end[0],end[1]-1),(end[0],end[1]+1))
        found = False
        for end in ends:
            if end in self.watershedCoordinates:
                found = True
                break

        if not found:
            debugMessages.append("did not find end in watershedCoordinates")
            return
        endPair = self.watershedCoordinates[end][0]

        # get paths that can be taken from end node
        for dualPair,path in self.foundPaths.items():
            if endPair in dualPair:
                self.applicablePaths[dualPair] = path

        # get super node for end node
        if not endPair in self.watershedSuperCoordinates:
            return
        endSuper = self.watershedSuperCoordinates[endPair]

        # find path to any point an a path leading to the end node
        exitPoint = self.mark([end])
        if not exitPoint:
            debugMessages.append("did not find exit point")
            return

        # get path from end position to end node
        endCoordinate = Coordinate(exitPoint[0][0],exitPoint[0][1])
        endNode = exitPoint[1][0]
        pathToEndNode = self.foundPaths[exitPoint[1]][1:self.foundPaths[exitPoint[1]].index((endCoordinate.x,endCoordinate.y))+1]

        # find path from start node to end node
        path = []
        
        # find path from node to node using the supernodes
        if not startSuper[0] == endSuper[0]:
            if endSuper[0] in self.watershedSuperNodeMap[startSuper[0]]:
                path = self.foundSuperPathsComplete[(startSuper[0],endSuper[0])]
            else:
                path = self.foundSuperPathsComplete[(startSuper[0],self.watershedSuperNodeMap[startSuper[0]][0])]+self.foundSuperPathsComplete[(self.watershedSuperNodeMap[startSuper[0]][0],endSuper[0])]
            path = pathToStartNode + self.findWayNodeBased(Coordinate(entryPoint[1][1][0],entryPoint[1][1][1]),Coordinate(startSuper[0][0],startSuper[0][1]))+path
            path = path + self.findWayNodeBased(Coordinate(endSuper[0][0],endSuper[0][1]),Coordinate(endNode[0],endNode[1]))+pathToEndNode
        # find path directly from node to node
        else:
            path = pathToStartNode + self.findWayNodeBased(Coordinate(startNode[0],startNode[1]),Coordinate(endNode[0],endNode[1]))+pathToEndNode

        # stitch together the path
        if not entryPoint[2][0] == start:
            entryPoint[2].reverse()
        path = entryPoint[2]+path+exitPoint[2][1:]

        # return cleaned up path
        return src.gameMath.removeLoops(path)

    '''
    construct the path to a coordinate by walking backwards from this coordinate back to the starting point
    bad code: simliar to the other pathfinding
    '''
    def markWalkBack(self,coordinate,obseveredCoordinates,pathToEntry,counter=0,limit=1000):

        # add current coordinate
        pathToEntry.append((coordinate[0],coordinate[1]))

        found = None

        # go back to position with lowest moves to start position
        for newCoordinate in [(coordinate[0]-1,coordinate[1]),(coordinate[0],coordinate[1]-1),(coordinate[0]+1,coordinate[1]),(coordinate[0],coordinate[1]+1)]:
            if not newCoordinate in obseveredCoordinates:
                continue
            if obseveredCoordinates[newCoordinate] >= limit:
                continue
            if (not found) or (obseveredCoordinates[found] < obseveredCoordinates[newCoordinate]):
                found = newCoordinate

        # walk back till start
        if found:
            self.markWalkBack(found,obseveredCoordinates,pathToEntry,counter+1, obseveredCoordinates[found])

    '''
    find path to the nearest entry point to a path
    '''
    def mark(self,coordinates,counter=0,obseveredCoordinates={}):

        # limit recursion depth
        if counter > 30:
            return

        newCoordinates = []
        # increse radius around current position
        if not counter == 0:
            for coordinate in coordinates:
                for newCoordinate in [(coordinate[0]-1,coordinate[1]),(coordinate[0],coordinate[1]-1),(coordinate[0]+1,coordinate[1]),(coordinate[0],coordinate[1]+1)]:
                    if newCoordinate in self.nonMovablecoordinates:
                        continue
                    if newCoordinate in self.obseveredCoordinates:
                        continue
                    newCoordinates.append(newCoordinate)
        # start from current position
        else:
            newCoordinates.append(coordinates[0])

        # check for intersections with a path
        for newCoordinate in newCoordinates:
            self.obseveredCoordinates[newCoordinate] = counter
            for dualPair,path in self.applicablePaths.items():
                if newCoordinate in path:
                    # get path by walking back to the start
                    pathToEntry = []
                    self.markWalkBack(newCoordinate,self.obseveredCoordinates,pathToEntry)
                    return (newCoordinate,dualPair,pathToEntry)

        # continue increasing the radius until path was intersected
        if newCoordinates:
            return self.mark(newCoordinates,counter+1,obseveredCoordinates)

    '''
    find path between start and end nodes using precalculated paths between nodes
    '''
    def findWayNodeBased(self,start,end):
        index = 0
        nodeMap = {}
        neighbourNodes = []

        # start with start node 
        startNode = (start.x,start.y)
        neighbourNodes.append(startNode)
        nodeMap[startNode] = (None,0)

        # abort because start node is end node
        if startNode == (end.x,end.y):
            lastNode = startNode

        # mode to neighbour nodes till end node is reached
        else:
            lastNode = None
            counter = 1
            while not lastNode:
                for neighbourNode in neighbourNodes[:]:
                    for watershedNode in self.watershedNodeMap[neighbourNode]:
                        if not watershedNode in neighbourNodes:
                            neighbourNodes.append(watershedNode)
                            nodeMap[watershedNode] = (neighbourNode,counter)
                        if watershedNode == (end.x,end.y):
                            lastNode = watershedNode
                            break
                counter += 1

                if counter == 20:
                    raise Exception("unable to find end node from "+str(start.x)+" / "+str(start.y)+" to "+str(end.x)+" / "+str(end.y))

        # walk back to start node and stitch together path
        outPath = []
        if lastNode:
            while nodeMap[lastNode][0]:
                extension = []
                if (lastNode,nodeMap[lastNode][0]) in self.foundPaths:
                    extension = self.foundPaths[(lastNode,nodeMap[lastNode][0])][:-1]
                    extension = list(reversed(extension))
                else:
                    extension = self.foundPaths[(nodeMap[lastNode][0],lastNode)][1:]
                outPath = extension + outPath
                lastNode = nodeMap[lastNode][0]

        return outPath

    '''
    add rooms to terrain and add them to internal datastructures
    '''
    def addRooms(self,rooms):
        self.rooms.extend(rooms)
        for room in rooms:
            room.terrain = self
            if (room.xPosition,room.yPosition) in self.roomByCoordinates:
                self.roomByCoordinates[(room.xPosition,room.yPosition)].append(room)
            else:
                self.roomByCoordinates[(room.xPosition,room.yPosition)] = [room]
        if hasattr(self,"watershedStart"): # nontrivial: prevents crashes in constructor
            self.calculatePathMap()

    '''
    remove item from terrain
    '''
    def removeItem(self,item,recalculate=True):
        #self.itemsOnFloor.remove(item)
        pos = (item.xPosition,item.yPosition,item.zPosition)
        itemList = self.getItemByPosition(pos)
        try:
            itemList.remove(item)
        except:
            pass

    def removeItems(self,items,recalcuate=True):
        for item in items:
            self.removeItem(item,recalculate=False)

    def addItem(self,item):
        self.addItems([item])

    '''
    add items to terrain and add them to internal datastructures
    '''
    def addItems(self,items,recalculate=True):
        #self.itemsOnFloor.extend(items)
        recalc = False
        for item in items:
            item.terrain = self
            item.room = None
            item.container = self
            if not item.walkable:
                recalc = True

            if not (item.xPosition or item.xPosition):
                return 

            position = (item.xPosition,item.yPosition,item.zPosition)
            if position[0]%15 == 0:
                if position[1]%15 < 7:
                    position = (position[0]+1,position[1]+1,position[2])
                elif position[1]%15 > 7:
                    position = (position[0]+1,position[1]-1,position[2])
                else:
                    if not item.type in ("Explosion","FireCrystals","Bomb","CommandBloom"):
                        continue
            if position[0]%15 == 14:
                if position[1]%15 < 7:
                    position = (position[0]-1,position[1]+1,position[2])
                elif position[1]%15 > 7:
                    position = (position[0]-1,position[1]-1,position[2])
                else:
                    if not item.type in ("Explosion","FireCrystals","Bomb","CommandBloom"):
                        continue
            if position[1]%15 == 0:
                if position[0]%15 < 7:
                    position = (position[0]+1,position[1]+1,position[2])
                elif position[0]%15 > 7:
                    position = (position[0]-1,position[1]+1,position[2])
                else:
                    if not item.type in ("Explosion","FireCrystals","Bomb","CommandBloom"):
                        continue
            if position[1]%15 == 14:
                if position[0]%15 < 7:
                    position = (position[0]+1,position[1]-1,position[2])
                elif position[0]%15 > 7:
                    position = (position[0]-1,position[1]-1,position[2])
                else:
                    if not item.type in ("Explosion","FireCrystals","Bomb","CommandBloom"):
                        continue

            item.xPosition = position[0]
            item.yPosition = position[1]
            item.zPosition = position[2]

            if position in self.itemsByCoordinate:
                self.itemsByCoordinate[position].insert(0,item)
            else:
                self.itemsByCoordinate[position] = [item]
        if recalc and hasattr(self,"watershedStart") and recalculate: # nontrivial: prevents crashes in constructor
            self.calculatePathMap()

    '''
    draw the floor
    '''
    def paintFloor(self):
        chars = []
        for i in range(0,250):
            line = []
            for j in range(0,250):
                if not self.hidden:
                    line.append(self.floordisplay)
                else:
                    line.append(displayChars.void)
            chars.append(line)
        return chars

    '''
    get nearby rooms

    '''
    def getNearbyRooms(self, pos):
        roomCandidates = []
        possiblePositions = set()
        for i in range(-1,2):
            for j in range(-1,2):
                possiblePositions.add((pos[0]-i,pos[1]-j))
        for coordinate in possiblePositions:
            if coordinate in self.roomByCoordinates:
                roomCandidates.extend(self.roomByCoordinates[coordinate])

        return roomCandidates

    def getRoomsOnFineCoordinate(self, pos):
        rooms = []
        for room in self.getNearbyRooms((pos[0]//15,pos[1]//15)):
            if (room.xPosition*15+room.offsetX < pos[0] and room.xPosition*15+room.offsetX+room.sizeX > pos[0] and
                room.yPosition*15+room.offsetY < pos[1] and room.yPosition*15+room.offsetY+room.sizeY > pos[1]):
                
                rooms.append(room)
        return rooms

    '''
    render the terrain and its contents
    '''
    def render(self):
        # hide/show map
        global mapHidden
        if mainChar.room == None:
            mapHidden = False
        else:
            if mainChar.room.open:
                mapHidden = False
            else:
                mapHidden = True
        #mapHidden = False
        self.hidden = mapHidden

        # paint floor
        chars = self.paintFloor()
        for x in range (0,225):
            for y in range (0,16):
                chars[x][y] = displayChars.forceField
                chars[x][y+14*15-1] = displayChars.forceField

        for y in range (0,225):
            for x in range (0,16):
                chars[x][y] = displayChars.forceField
                chars[x+14*15-1][y] = displayChars.forceField

        # show/hide rooms
        for room in self.rooms:
            if mainChar.room == room:
                room.hidden = False
            else:
                if not mapHidden and room.open and room.hidden:
                    room.hidden = False
                    room.applySkippedAdvances() # ensure the rooms state is up to date
                else:
                    room.hidden = True

        for bigX in range(0,14):
            for bigY in range(0,14):
                for x in range(0,15):
                    for y in range(0,15):
                        if x == 7 or y == 7:
                            continue 
                        chars[bigX*15+x][bigY*15+0] = displayChars.forceField
                        chars[bigX*15+x][bigY*15+14] = displayChars.forceField
                        chars[bigX*15+0][bigY*15+y] = displayChars.forceField
                        chars[bigX*15+14][bigY*15+y] = displayChars.forceField
                
        # calculate room visibility
        if not mapHidden:
            # get players position in tiles (15*15 segments)
            pos = None
            if mainChar.room == None:
                pos = (mainChar.xPosition//15,mainChar.yPosition//15)
            else:
                pos = (mainChar.room.xPosition,mainChar.yPosition)

            # get rooms near the player
            roomCandidates = self.getNearbyRooms(pos)

            # show rooms near the player
            for room in roomCandidates:
                if room.open:
                    room.hidden = False
                    room.applySkippedAdvances() # ensure the rooms state is up to date
                
        # draw items on map
        if not mapHidden:
            #for item in self.itemsOnFloor:
            #    if not (item.yPosition and item.xPosition):
            #        continue
            #    chars[item.yPosition][item.xPosition] = item.display
            for entry in self.itemsByCoordinate.values():
                if not entry:
                    continue
                item = entry[0]
                if not (item.yPosition and item.xPosition):
                    continue
                if not (item.zPosition == mainChar.zPosition):
                    continue

                try:
                    chars[item.yPosition][item.xPosition] = item.render()
                except:
                    pass


        # render each room
        for room in self.rooms:

            # skip hidden rooms
            #if mapHidden and room.hidden:
            #    continue
            if not mainChar in room.characters:
                room.hidden = True

            # get the render for the room
            renderedRoom = room.render()
            
            # pace rendered room on rendered terrain
            xOffset = room.xPosition*15+room.offsetX
            yOffset = room.yPosition*15+room.offsetY
            lineCounter = 0
            for line in renderedRoom:
                rowCounter = 0
                for char in line:
                    chars[lineCounter+yOffset][rowCounter+xOffset] = char
                    rowCounter += 1
                lineCounter += 1

        # add overlays
        if not mapHidden:
            #src.overlays.QuestMarkerOverlay().apply(chars,mainChar,displayChars)
            src.overlays.NPCsOverlay().apply(chars,self)
            src.overlays.MainCharOverlay().apply(chars,mainChar)

        # cache rendering
        self.lastRender = chars

        # add special overlay
        if self.overlay:
            self.overlay(chars)

        for bigX in range(1,15):
            for bigY in range(1,15):
                for x in range(1,8):
                    chars[bigX*15+x][1] = displayChars.void

        chars[127][42] = displayChars.void
        chars[42][127] = displayChars.void
        return chars

    '''
    get things that would be affected if a room would move
    '''
    def getAffectedByRoomMovementDirection(self,room,direction,force=1,movementBlock=set()):

        # determine rooms that the room could collide with
        roomCandidates = []
        bigX = room.xPosition
        bigY = room.yPosition
        possiblePositions = set()
        for i in range(-2,2):
            for j in range(-2,2):
                possiblePositions.add((bigX-i,bigY-j))
        for coordinate in possiblePositions:
            if coordinate in self.roomByCoordinates:
                roomCandidates.extend(self.roomByCoordinates[coordinate])

        # get the rooms the room actually collides with
        roomCollisions = set()
        for roomCandidate in roomCandidates:
            if direction == "north":
                if (room.yPosition*15 + room.offsetY) == (roomCandidate.yPosition*15+roomCandidate.offsetY+roomCandidate.sizeY):
                    if (room.xPosition*15+room.offsetX < roomCandidate.xPosition*15+roomCandidate.offsetX+roomCandidate.sizeX) and (room.xPosition*15+room.offsetX+room.sizeX > roomCandidate.xPosition*15+roomCandidate.offsetX):
                        roomCollisions.add(roomCandidate)
            elif direction == "south":
                if (room.yPosition*15 + room.offsetY+room.sizeY) == (roomCandidate.yPosition*15+roomCandidate.offsetY):
                    if (room.xPosition*15+room.offsetX < roomCandidate.xPosition*15+roomCandidate.offsetX+roomCandidate.sizeX) and (room.xPosition*15+room.offsetX+room.sizeX > roomCandidate.xPosition*15+roomCandidate.offsetX):
                        roomCollisions.add(roomCandidate)
            elif direction == "west":
                if (room.xPosition*15 + room.offsetX) == (roomCandidate.xPosition*15+roomCandidate.offsetX+roomCandidate.sizeX):
                    if (room.yPosition*15+room.offsetY < roomCandidate.yPosition*15+roomCandidate.offsetY+roomCandidate.sizeY) and (room.yPosition*15+room.offsetY+room.sizeY > roomCandidate.yPosition*15+roomCandidate.offsetY):
                        roomCollisions.add(roomCandidate)
            elif direction == "east":
                if (room.xPosition*15 + room.offsetX+ room.sizeX) == (roomCandidate.xPosition*15+roomCandidate.offsetX):
                    if (room.yPosition*15+room.offsetY < roomCandidate.yPosition*15+roomCandidate.offsetY+roomCandidate.sizeY) and (room.yPosition*15+room.offsetY+room.sizeY > roomCandidate.yPosition*15+roomCandidate.offsetY):
                        roomCollisions.add(roomCandidate)
            else:
                debugMessages.append("invalid movement direction: "+str(direction))

        # get collisions from the pushed rooms recursively
        for roomCollision in roomCollisions:
            movementBlock.add(roomCollision)
            self.getAffectedByRoomMovementDirection(roomCollision,direction,force=force,movementBlock=movementBlock)

        # add affected items
        if direction == "north":
            posX = room.xPosition*15+room.offsetX-1
            maxX = room.xPosition*15+room.offsetX+room.sizeX-1
            while posX < maxX:
                posX += 1
                if (posX,room.yPosition*15+room.offsetY-1) in self.itemByCoordinates:
                    movementBlock.update(self.itemByCoordinates[(posX,room.yPosition*15+room.offsetY-1)])
        elif direction == "south":
            posX = room.xPosition*15+room.offsetX-1
            maxX = room.xPosition*15+room.offsetX+room.sizeX-1
            while posX < maxX:
                posX += 1
                if (posX,room.yPosition*15+room.offsetY+room.sizeY) in self.itemByCoordinates:
                    movementBlock.update(self.itemByCoordinates[(posX,room.yPosition*15+room.offsetY+room.sizeY)])
        elif direction == "west":
            posY = room.yPosition*15+room.offsetY-1
            maxY = room.yPosition*15+room.offsetY+room.sizeY-1
            while posY < maxY:
                posY += 1
                if (room.xPosition*15+room.offsetX-1,posY) in self.itemByCoordinates:
                    movementBlock.update(self.itemByCoordinates[(room.xPosition*15+room.offsetX-1,posY)])
        elif direction == "east":
            posY = room.yPosition*15+room.offsetY-1
            maxY = room.yPosition*15+room.offsetY+room.sizeY-1
            while posY < maxY:
                posY += 1
                if (room.xPosition*15+room.offsetX+room.sizeX,posY) in self.itemByCoordinates:
                    movementBlock.update(self.itemByCoordinates[(room.xPosition*15+room.offsetX+room.sizeX,posY)])
        else:
            debugMessages.append("invalid movement direction: "+str(direction))

    '''
    actually move a room trough the terrain
    '''
    def moveRoomDirection(self,direction,room,force=1,movementBlock=[]):

        # move the room
        if direction == "north":
            # naively move the room withion current tile
            if room.offsetY > -5:
                room.offsetY -= 1
            # remove room from current tile
            else:
                room.offsetY = 9
                self.removeRoom(room)
                room.yPosition -= 1
                self.addRoom(room)
        elif direction == "south":
            # naively move the room withion current tile
            if room.offsetY < 9:
                room.offsetY += 1
            # remove room from current tile
            else:
                room.offsetY = -5
                self.removeRoom(room)
                room.yPosition += 1
                self.addRoom(room)
        elif direction == "east":
            # naively move the room withion current tile
            if room.offsetX < 9:
                room.offsetX += 1
            # remove room from current tile
            else:
                room.offsetX = -5
                self.removeRoom(room)
                room.xPosition += 1
                self.addRoom(room)
        elif direction == "west":
            # naively move the room withion current tile
            if room.offsetX > -5:
                room.offsetX -= 1
            # remove room from current tile
            else:
                room.offsetX = 9
                self.removeRoom(room)
                room.xPosition -= 1
                self.addRoom(room)

        if room.xPosition < 0:
            mainChar.addMessage("switch to")
            terrain = gamestate.terrainMap[self.yPosition][self.xPosition-1]
            room.terrain = terrain
            self.removeRoom(room)
            terrain.addRoom(room)
            room.xPosition = 15
        if room.yPosition < 0:
            mainChar.addMessage("switch to")
            terrain = gamestate.terrainMap[self.yPosition-1][self.xPosition]
            room.terrain = terrain
            self.removeRoom(room)
            terrain.addRoom(room)
            room.yPosition = 15
        if room.xPosition > 15:
            mainChar.addMessage("switch to")
            terrain = gamestate.terrainMap[self.yPosition][self.xPosition+1]
            room.terrain = terrain
            self.removeRoom(room)
            terrain.addRoom(room)
            room.xPosition = 0
        if room.yPosition > 15:
            mainChar.addMessage("switch to")
            terrain = gamestate.terrainMap[self.yPosition+1][self.xPosition]
            room.terrain = terrain
            self.removeRoom(room)
            terrain.addRoom(room)
            room.yPosition = 0

        # kill characters driven over by the room
        for char in self.characters:
            if (char.xPosition > room.xPosition*15+room.offsetX and 
               char.xPosition < room.xPosition*15+room.offsetX+room.sizeX and
               char.yPosition > room.yPosition*15+room.offsetY and
               char.yPosition < room.yPosition*15+room.offsetY+room.sizeY):
                    char.die()

        # reset paths
        if hasattr(self,"watershedStart"):
            self.calculatePathMap()

    '''
    remove a room from terrain
    '''
    def removeRoom(self,room):
        self.rooms.remove(room)

        if (room.xPosition,room.yPosition) in self.roomByCoordinates:
            self.roomByCoordinates[(room.xPosition,room.yPosition)].remove(room)
            if not len(self.roomByCoordinates[(room.xPosition,room.yPosition)]):
                del self.roomByCoordinates[(room.xPosition,room.yPosition)]

        if hasattr(self,"watershedStart"): # nontrivial: prevents crashes in constructor
            self.calculatePathMap()

    '''
    add a room to the terrain
    '''
    def addRoom(self,room):
        room.terrain = self
        self.rooms.append(room)

        if (room.xPosition,room.yPosition) in self.roomByCoordinates:
            self.roomByCoordinates[(room.xPosition,room.yPosition)].append(room)
        else:
            self.roomByCoordinates[(room.xPosition,room.yPosition)] = [room]

        if hasattr(self,"watershedStart"): # nontrivial: prevents crashes in constructor
            self.calculatePathMap()
            
    '''
    teleport a room to another position
    '''
    def teleportRoom(self,room,newPosition):

        # remove room from old position
        oldPosition = (room.xPosition,room.yPosition)
        if oldPosition in self.roomByCoordinates:
            if room in self.roomByCoordinates[oldPosition]:
                self.roomByCoordinates[oldPosition].remove(room)
                if not len(self.roomByCoordinates[oldPosition]):
                    del self.roomByCoordinates[oldPosition]

        # add room to new position
        if newPosition in self.roomByCoordinates:
            self.roomByCoordinates[newPosition].append(room)
        else:
            self.roomByCoordinates[newPosition] = [room]
        room.xPosition = newPosition[0]
        room.yPosition = newPosition[1]

        # reset paths
        if hasattr(self,"watershedStart"):
            self.calculatePathMap()

    '''
    set state from dict
    bad code: should be in saveable
    '''
    def setState(self,state,tick=0):
        for roomId in state["roomIds"]:
            room = src.rooms.getRoomFromState(state["roomStates"][roomId],terrain=self)
            self.addRoom(room)

        for eventId in state["eventIds"]:
            eventState = state["eventStates"][eventId]
            event = src.events.getEventFromState(eventState)
            self.addEvent(event)

        for charId in state["characterIds"]:
            charState = state["characterStates"][charId]
            char = src.characters.getCharacterFromState(charState)
            char.terrain = self
            char.room = None
            self.addCharacter(char,charState["xPosition"],charState["yPosition"])

        addItems = []
        for itemId in state["itemIds"]:
            itemState = state["itemStates"][itemId]
            item = src.items.getItemFromState(itemState)
            addItems.append(item)
        self.addItems(addItems)

    '''
    get state as dict
    bad code: should be in saveable
    '''
    def getState(self):
        roomIds = []
        roomStates = {}
        for room in self.rooms:
            roomIds.append(room.id)
            roomStates[room.id] = room.getState()

        itemsOnFloor = []
        for entry in self.itemsByCoordinate.values():
            itemsOnFloor.extend(reversed(entry))
        itemIds = []
        itemStates = {}
        for item in itemsOnFloor:
            itemIds.append(item.id)
            itemStates[item.id] = item.getState()

        exclude = []
        if mainChar:
            exclude.append(mainChar.id)
        characterIds = []
        characterStates = {}
        for character in self.characters:
            if character == mainChar:
                continue
            characterIds.append(character.id)
            characterStates[character.id] = character.getState()

        eventIds = []
        eventStates = {}
        for event in self.events:
            eventIds.append(event.id)
            eventStates[event.id] = event.getState()

        # generate state
        return {
                  "objType":self.objType,

                  "roomIds":roomIds,
                  "roomStates":roomStates,
                  "itemIds":itemIds,
                  "itemStates":itemStates,
                  "characterIds":characterIds,
                  "characterStates":characterStates,
                  "initialSeed":self.initialSeed,
                  "eventIds":eventIds,
                  "eventStates":eventStates,
               }

    '''
    add an event to internal structure
    bad code: should be in extra class
    '''
    def addEvent(self,event):
        index = 0
        start = 0
        end = len(self.events)

        import random
        while not start == end:
            pivot = (start+end)//2
            compareEvent = self.events[pivot]
            if compareEvent.tick < event.tick:
                start = pivot+1
            elif compareEvent.tick == event.tick:
                start = pivot
                end = pivot
                break
            else:
                end = pivot
        self.events.insert(start,event)

'''
a empty terrain
'''
class EmptyTerrain(Terrain):
    objType = "EmptyTerrain"

'''
a almost empty terrain
'''
class Nothingness(Terrain):
    objType = "Nothingness"

    '''
    paint floor with minimal variation to ease perception of movement
    '''
    def paintFloor(self):
        displayChar = self.floordisplay
        if mainChar.zPosition < 0:
            displayChar = "%s"%(mainChar.zPosition,)
        if mainChar.zPosition > 0:
            displayChar = "+%s"%(mainChar.zPosition,)

        chars = []
        for i in range(0,250):
            line = []
            for j in range(0,250):
                if not self.hidden:
                    if not i%7 and not j%12 and not (i+j)%3:
                        # paint grass at pseudo random location
                        line.append(displayChars.grass)
                    else:
                        line.append(displayChar)
                else:
                    line.append(displayChars.void)
            chars.append(line)
        return chars

    '''
    state initialization
    '''
    def __init__(self,creator=None,seed=0, noContent=False):

        # leave layout empty
        layout = """
        """
        detailedLayout = """
        """

        super().__init__(layout,detailedLayout,creator=creator,seed=seed, noPaths = True, noContent=noContent)

        if not noContent:
            # add a few items scattered around
            self.dekoItems = []
            for x in range(1,224):
                for y in range(1,224):
                    item = None
                    if not x%23 and not y%35 and not (x+y)%5:
                        item = src.items.itemMap["Scrap"](x,y,1,creator=creator)
                        item.bolted = False
                    if not x%57 and not y%22 and not (x+y)%3:
                        item = src.items.itemMap["Item"](displayChars.foodStuffs[((2*x)+y)%6],x,y,creator=creator)
                        item.walkable = True
                        item.bolted = False
                    if not x%19 and not y%27 and not (x+y)%4:
                        item = src.items.itemMap["Item"](displayChars.foodStuffs[((2*x)+y)%6],x,y,creator=creator)
                        item.walkable = True
                        item.bolted = False
                    if item:
                        self.dekoItems.append(item)
            self.addItems(self.dekoItems)

        self.floordisplay = displayChars.dirt

'''
a gameplay test
'''
class GameplayTest(Terrain):
    objType = "GameplayTest"

    '''
    state initialization
    '''
    def __init__(self,creator=None,seed=0, noContent=False):
        # add only a few scattered intact rooms
        layout = """
             
             
             
             
             
             
             
             
     .       
    C.       
             
             
             
             
             
        """
        layout = """
        """
        detailedLayout = """
        """

        super().__init__(layout,detailedLayout,creator=creator,seed=seed, noContent=noContent)

        self.floordisplay = displayChars.dirt

        if not noContent:
            '''
            add field of thick scrap
            '''
            def addPseudoRandomScrap(maxItems,xRange,yRange,seed=0):
                excludes = {}

                counter = 0
                maxOffsetX = xRange[1]-xRange[0]
                maxOffsetY = yRange[1]-yRange[0]
                while counter < maxItems:

                    position = None
                    while position == None or position in excludes.keys():
                        position = (xRange[0]+seed%maxOffsetX,yRange[0]+seed//(maxItems*2)%maxOffsetY)
                        seed += 1

                    excludes[position] = seed%20

                    seed += seed%105
                    counter += 1

                counter = 0
                for (key,thickness) in excludes.items():
                    noScrap = False
                    if counter%5 == 0:
                        if key[0]//15 >= 7 and key[1]//15 == 7 or (key[0]//15,key[1]//15) in ((7,7),(7,6),(7,8),(8,7),(8,6),(8,8)):
                            continue
                        if key[0]%15 in (0,14) or key[1]%15 in (0,14):
                            continue
                        if not counter%(5*3) == 0:
                            l1types = [src.items.itemMap["Sheet"],src.items.itemMap["Rod"],src.items.itemMap["Sheet"],src.items.itemMap["Mount"],src.items.itemMap["Stripe"],src.items.itemMap["Bolt"],src.items.itemMap["Radiator"]]
                            self.scrapItems.append(l1types[seed%len(l1types)](key[0],key[1],creator=self))
                        else:
                            l2types = [src.items.itemMap["Tank"],src.items.itemMap["Heater"],src.items.itemMap["Connector"],src.items.itemMap["Pusher"],src.items.itemMap["Puller"],src.items.itemMap["GooFlask"],src.items.itemMap["Frame"]]
                            self.scrapItems.append(l2types[seed%len(l2types)](key[0],key[1],creator=self))

                        if seed%15:
                            noScrap = False
                        else:
                            noScrap = True

                        seed += seed%37

                    if not noScrap:
                        item = src.items.itemMap["Scrap"](key[0],key[1],thickness,creator=self)
                        item.mayContainMice = False
                        self.scrapItems.append(item)

                    seed += seed%13
                    counter += 1

            '''
            add field of items
            '''
            def addPseudoRandomThing(xRange,yRange,modulos,itemType):
                for x in range(xRange[0],xRange[1]):
                    for y in range(yRange[0],yRange[1]):
                        # skip pseudorandomly
                        if x%modulos[0] and y%modulos[1] or (not x%modulos[2] and not x%modulos[3]) or x%modulos[4] or not y%modulos[5]:
                            continue
                        if (x//15,y//15) in ((6,6),(6,7),(6,8),(7,7),(7,6),(7,8),(8,7),(8,6),(8,8),(11,7),(10,7),(9,7)):
                            continue

                        # add scrap
                        self.scrapItems.append(itemType(x,y,creator=creator))

            self.scrapItems = []

            # add scrap
            fieldThickness = seed//3%20
            x = 45
            while x < 180:
                y = 45
                while y < 180:
                    seed += seed%35
                    if x in (45,165) or y in (45,165) or ((x,y) in ((90,90),(90,105),(90,120))):
                        maxItems = (8*8)-seed%10-fieldThickness
                    elif x >= 75 and x <= 135 and y >= 75 and y <= 135:
                        maxItems = (12*12)-seed%20-fieldThickness
                    else:
                        maxItems = (15*15)-seed%30-fieldThickness
                    addPseudoRandomScrap(maxItems,(x,x+15),(y,y+15),seed)

                    y += 15
                x += 15
            self.addItems(self.scrapItems)

            self.scrapItems = []

            # add other objects
            addPseudoRandomThing((45,170),(45,170),(23,7,2,3,2,4),src.items.itemMap["Wall"])
            seed += seed%35
            addPseudoRandomThing((45,170),(45,170),(13,15,3,5,3,2),src.items.itemMap["Pipe"])

            toRemove = []
            for item in self.scrapItems:
                subItems = self.getItemByPosition((item.xPosition,item.yPosition,item.zPosition))
                for subItem in subItems:
                    toRemove.append(subItem)

            self.addItems(self.scrapItems)

            """
            x = 157
            for y in range(97,129):
                toRemove.extend(self.getItemByPosition((x,y)))
            """
            
            for item in toRemove:
                self.removeItem(item, recalculate=False)

            seed += seed%23
            furnace = src.items.itemMap["Furnace"](90+seed%78,90+(seed*5)%78,creator=self)
            furnace.bolted = False
            seed += seed%42
            hutch = src.items.itemMap["Hutch"](90+seed%78,90+(seed*5)%78,creator=self)
            hutch.bolted = False
            seed += seed%65
            growthTank = src.items.itemMap["GrowthTank"](90+seed%78,90+(seed*5)%78,creator=self)
            growthTank.bolted = False
            extraItems = [furnace,hutch,growthTank]
            self.addItems(extraItems)

            # add base of operations
            # add base of operations
            self.miniBase = src.rooms.MiniBase(7,7,1,1,creator=self,seed=seed)
            self.addRooms([self.miniBase])
            #3,8

            extraItems = []

            #tree = src.items.Tree(67,93,creator=self)
            #extraItems.append(tree)
            #tree = src.items.Tree(103,64,creator=self)
            #extraItems.append(tree)
            #tree = src.items.Tree(80,25,creator=self)
            #extraItems.append(tree)
            #tree = src.items.Tree(125,74,creator=self)
            #extraItems.append(tree)
            #tree = src.items.Tree(15,14,creator=self)
            #extraItems.append(tree)

            #coalMine = src.items.CoalMine(50,112,creator=self)
            #extraItems.append(coalMine)

            self.addItems(extraItems)

            toRemove = []
            for x in range(124,131):
                for y in range(124,131):
                    subItems = self.getItemByPosition((x,y,0))
                    for subItem in subItems:
                        toRemove.append(subItem)

            for item in toRemove:
                self.removeItem(item, recalculate=False)

            # save internal state
            self.initialState = self.getState()

    '''
    paint floor with minimal variation to ease perception of movement
    '''
    def paintFloor(self):
        chars = []
        for i in range(0,250):
            line = []
            for j in range(0,250):
                if not self.hidden:
                    line.append(self.floordisplay)
                else:
                    line.append(displayChars.void)
            chars.append(line)
        return chars

'''
a test for desert map
'''
class Desert(Terrain):
    objType = "Desert"

    '''
    state initialization
    '''
    def __init__(self,creator=None,seed=0, noContent=False):

        import random

        # add only a few scattered intact rooms
        layout = """
             
             
             
             
             
             
             
             
     .       
    C.       
             
             
             
             
             
        """
        layout = """
        """
        detailedLayout = """
        """

        super().__init__(layout,detailedLayout,creator=creator,seed=seed, noContent=noContent)

        self.itemPool = []
        self.itemPool.append(src.items.itemMap["SunScreen"](None,None,creator=self))
        self.itemPool.append(src.items.itemMap["SunScreen"](None,None,creator=self))
        self.itemPool.append(src.items.itemMap["SunScreen"](None,None,creator=self))
        machine = src.items.itemMap["Machine"](None,None,creator=self) 
        machine.setToProduce("Rod")
        machine.bolted = False
        self.itemPool.append(machine)
        machine = src.items.itemMap["Machine"](None,None,creator=self) 
        machine.setToProduce("Rod")
        machine.bolted = False
        self.itemPool.append(machine)
        machine = src.items.itemMap["Machine"](None,None,creator=self) 
        machine.setToProduce("Rod")
        machine.bolted = False
        self.itemPool.append(machine)
        machine = src.items.itemMap["Machine"](None,None,creator=self) 
        machine.setToProduce("Rod")
        machine.bolted = False
        self.itemPool.append(machine)
        machine = src.items.itemMap["Machine"](None,None,creator=self) 
        machine.setToProduce("Rod")
        machine.bolted = False
        self.itemPool.append(machine)
        machine = src.items.itemMap["Machine"](None,None,creator=self) 
        machine.setToProduce("Sheet")
        machine.bolted = False
        self.itemPool.append(machine)
        machine = src.items.itemMap["Machine"](None,None,creator=self) 
        machine.setToProduce("Sheet")
        machine.bolted = False
        self.itemPool.append(machine)
        machine = src.items.itemMap["Machine"](None,None,creator=self) 
        for i in range(1,30):
            self.itemPool.append(src.items.itemMap["Sheet"](None,None,creator=self))
            case = src.items.itemMap["Case"](None,None,creator=self)
            case.bolted = False
            self.itemPool.append(case)
            self.itemPool.append(src.items.itemMap["Vial"](None,None,creator=self))
            corpse = src.items.itemMap["Corpse"](None,None,creator=self)
            corpse.charges = random.randint(100,300)
            self.itemPool.append(corpse)
        for i in range(1,200):
            self.itemPool.append(src.items.itemMap["Coal"](None,None,creator=self))
            self.itemPool.append(src.items.itemMap["MetalBars"](None,None,creator=self))
            self.itemPool.append(src.items.itemMap["Rod"](None,None,creator=self))
            self.itemPool.append(src.items.itemMap["Scrap"](None,None,creator=self,amount=1))
            self.itemPool.append(src.items.itemMap["Scrap"](None,None,creator=self,amount=1))
            self.itemPool.append(src.items.itemMap["Scrap"](None,None,creator=self,amount=1))

        import random
        random.shuffle(self.itemPool)
        for item in self.itemPool:
            while 1:
                x = random.randint(1,225)
                y = random.randint(1,225)

                if x%15 in (0,14) or y%15 in (0,14):
                    continue

                item.xPosition = x
                item.yPosition = y
                break

        waterCondenser = src.items.itemMap["WaterCondenser"](6*15+6,7*15+6,creator=self)
        waterCondenser.lastUsage = -10000
        self.addItems([waterCondenser])
        waterCondenser = src.items.itemMap["WaterCondenser"](6*15+6,7*15+8,creator=self)
        waterCondenser.lastUsage = -10000
        self.addItems([waterCondenser])
        waterCondenser = src.items.itemMap["WaterCondenser"](6*15+8,7*15+6,creator=self)
        waterCondenser.lastUsage = -10000
        self.addItems([waterCondenser])
        waterCondenser = src.items.itemMap["WaterCondenser"](6*15+8,7*15+8,creator=self)
        waterCondenser.lastUsage = -10000
        self.addItems([waterCondenser])

        # add base of operations
        self.miniBase = src.rooms.MiniBase2(3,7,2,2,creator=self,seed=seed)
        self.addRooms([self.miniBase])

        # save internal state
        self.initialState = self.getState()

        self.doSandStorm()
        self.randomizeHeatmap()

    def randomizeHeatmap(self):
        # save heatmap for tiles
        import random

        self.heatmap = []
        for x in range(0,15):
            self.heatmap.append([])
            for y in range(0,15):
                self.heatmap[x].append(0)
                self.heatmap[x][y] = random.randint(1,5)

    def doSandStorm(self):
        import random

        counter = 0
        toMove = []
        for (position,items) in self.itemsByCoordinate.items():
            for item in items:
                if item.bolted:
                    continue
                self.removeItem(item)
                if counter%2 == 0:
                    toMove.append(item)
                else:
                    self.itemPool.append(item)
                counter += 1
        
        cutOff = len(self.itemPool)//10
        toAdd = self.itemPool[:cutOff]
        self.itemPool = self.itemPool[cutOff:]

        for item in toMove:
            x = item.xPosition+random.randint(-1,1)
            y = item.yPosition+random.randint(-1,1)
            if not x%15 in (0,14) and not y%15 in (0,14):
                    self.removeItem(item)
                    item.xPosition = x
                    item.yPosition = y
                    self.addItems([item])

        for item in toAdd[:len(toAdd)//2]:
            x = random.randint(16,209)
            if not x%15 in (0,14):
                item.xPosition = x
            y = random.randint(16,209)
            if not y%15 in (0,14):
                item.yPosition = y
        self.addItems(toAdd)

    '''
    paint floor with minimal variation to ease perception of movement
    '''
    def paintFloor(self):
        import urwid
        desertTiles = [
                        (urwid.AttrSpec("#0c2","black"),"::"),
                        (urwid.AttrSpec("#2c2","black"),"::"),
                        (urwid.AttrSpec("#4c2","black"),"::"),
                        (urwid.AttrSpec("#8c2","black"),"::"),
                        (urwid.AttrSpec("#ac2","black"),"::"),
                        (urwid.AttrSpec("#cc2","black"),"::"),
                        (urwid.AttrSpec("#fc2","black"),"::"),
                    ]

        chars = []
        for i in range(0,250):
            line = []
            for j in range(0,250):
                if not self.hidden:
                    try:
                        line.append(desertTiles[self.heatmap[j//15][i//15]])
                    except:
                        line.append(displayChars.void)
                else:
                    line.append(displayChars.void)
            chars.append(line)
        return chars

    def moveCharacterDirection(self,char,direction):
        heatDamage = self.heatmap[char.xPosition//15][char.yPosition//15]-char.heatResistance
        if heatDamage > 0:
            char.addMessage("The sun burns your skin")
            char.hurt(heatDamage,reason="sunburn")
        return super().moveCharacterDirection(char,direction)

'''
a wrecked mech
'''
class ScrapField(Terrain):
    objType = "ScrapField"

    '''
    state initialization
    '''
    def __init__(self,creator=None,seed=0, noContent=False):
        # add only a few scattered intact rooms
        layout = """


  U  U 
U  U 
     U
  U  U

        """
        detailedLayout = """
        """
        super().__init__(layout,detailedLayout,creator=creator,seed=seed,noContent=noContent)

        self.floordisplay = displayChars.dirt

        '''
        add field of thick scrap
        '''
        def addPseudoRandomScrap(counter,xRange,yRange,skips):
            for x in range(xRange[0],xRange[1]):
                for y in range(yRange[0],yRange[1]):
                    # skip pseudorandomly
                    toSkip = False
                    for skip in skips:
                        if not x%skip[0] and not y%skip[1]:
                            toSkip = True
                            break
                    if toSkip:
                        continue

                    # add scrap
                    self.scrapItems.append(src.items.Scrap(x,y,counter,creator=creator))
                    counter += 1
                    if counter == 16:
                        counter = 1
            return counter

        '''
        add field of items
        '''
        def addPseudoRandomThin(xRange,yRange,modulos,itemType):
            for x in range(xRange[0],xRange[1]):
                for y in range(yRange[0],yRange[1]):
                    # skip pseudorandomly
                    if x%modulos[0] and y%modulos[1] or (not x%modulos[2] and not x%modulos[3]) or x%modulos[4] or not y%modulos[5]:
                        continue

                    # add scrap
                    self.scrapItems.append(itemType(x,y,creator=creator))

        self.scrapItems = []

        # add scrap
        counter = 3
        counter = addPseudoRandomScrap(counter,(20,30),(30,110),((2,3),(3,2),(4,5),(5,4)))

        counter = 3
        counter = addPseudoRandomScrap(counter,(20,30),(30,110),((2,3),(3,2),(4,5),(5,4)))
        counter = addPseudoRandomScrap(counter,(20,120),(20,30),((2,3),(3,2),(4,5),(5,4)))
        counter = addPseudoRandomScrap(counter,(110,120),(30,110),((2,3),(3,2),(4,5),(5,4)))
        counter = addPseudoRandomScrap(counter,(20,120),(110,120),((2,3),(3,2),(4,5),(5,4)))
        counter = addPseudoRandomScrap(counter,(30,110),(30,110),((2,7),(5,3),(23,2),(13,9),(5,17)))

        # add other objects
        addPseudoRandomThin((30,110),(30,110),(23,7,2,3,2,4),src.items.Wall)
        addPseudoRandomThin((30,110),(30,110),(13,15,3,5,3,2),src.items.Pipe)

        self.addItems(self.scrapItems)

        # add base of operations
        self.wakeUpRoom = src.rooms.MiniBase(0,4,0,0,creator=creator)
        self.addRooms([self.wakeUpRoom])

'''
the tutorial mech
'''
class TutorialTerrain(Terrain):
    objType = "TutorialTerrain"

    def __init__(self,creator=None,seed=0, noContent=False):
        self.toTransport = []

        # the layout for the mech
        layout = """
XlllllllllX
XXXXXXXXXXX
XVv?b?Q?vVX
XO.t    .OX
Xw MQKhl LX
XW Q???Q mX
XU.     .UX
XU CCCCC UX
XU CCCCCtUX
XXXCCCCCXXX """
        detailedLayout = """
                                                                                                                                                                    
                                                                                                                                                                    
                                                                                                                                                                    
                                                                                                                                                                    
                                                                                                                                                                    
                                                                                                                                                                    
                                                                                                                                                                    
                                                                                                                                                                    
                                                                                                                                                                    
                                                                                                                                                                    
                                                                                                                                                                    
                                                                                                                                                                    
                                                                                                                                                                    
                                                                                                                                                                    
                                                                                                                                                                    
                                                                                                                                                                     
               X                                           X                                                                                                         
               X#           #X               X#           #XX#           #XX#           #XX#           #XX#           #X               X#           #X               
               X#           #X               X#           #XX#           #XX#           #XX#           #XX#           #X               X#           #X               
               X#           #X               X#           #XX#           #XX#           #XX#           #XX#           #X               X#           #X               
               X#           #X               X#           #XX#           #XX#           #XX#           #XX#           #X               X#           #X               
               X#           #X               X#           #XX#           #XX#           #XX#           #XX#           #X               X#           #X               
               X#           #X               X#           #XX#           #XX#           #XX#           #XX#           #X               X#           #X               
               X#           #X               X#           #XX#           #XX#           #XX#           #XX#           #X               X#           #X               
               X#           #X               X#           #XX#           #XX#           #XX#           #XX#           #X               X#           #X               
               X#           #X               X#           #XX#           #XX#           #XX#           #XX#           #X               X#           #X               
               X#           #X               X#           #XX#           #XX#           #XX#           #XX#           #X               X#           #X               
               X#           #X               X#           #XX#           #XX#           #XX#           #XX#           #X               X#           #X               
               X#           #X               X#           #XX#           #XX#           #XX#           #XX#           #X               X#           #X               
               XXXXXXXXXXXX#XX               XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX            X               
                  ###  ###                                                                                                                   XXXXXXXXX               
               ####O####O####      O  O       ################           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               # R          #   R        R    #R        R #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               #O          O#  O             ##           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               #            # ##          O  #O          O#XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               #            # #              ##           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               #O          O# #               #           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               #            # #              ##          ##XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               #            ####             #O          OXXX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               #O          O#  O          O  ##           XXX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               ##          ##  X              #           XXX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               #X         RX####R        R   ##R        R                XXXXXXXXXXXXXX XXXXXXXXXXXXXX XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX               
               #X          XXXX###### ########XXXX8  O                                                                                              X               
               #X             XXXXXXX XXXXXXXXX   8                                                                                                  X               
               #XXXXXXXXXX  X                     8                                                                                                  X              
               ############ #X                    8                                                                                   XXXXXXXX  XXXXXX              
               XXXXXXXXXXX  #X                    8                                                                                    X#X          #X               
                            #X                                                                                                         X#X          #X               
                            #X                                                                                                         X#X          #X               
                            #X                                                                                                         X#X          #X               
                            #X                                                                                                         X#X          #X               
                            #X                                                                                                         X#X          #X               
                            #X                                                                                                         X#X          #X               
                            #X                                                                                                         X#X          #X               
                            #X                                                                                                         X#X          #X               
                            #X                                                                                                         X#X          #X               
                            #X                                                                                                         X#X          #X               
                           ##X                                                                                                         X#X          #X               
               XXXXXXXXXXX   X                                                                                                         X#X                           
               #############                                                                                                           X#X          #X               
               XXXXXXXXXXXXXXX               X#####    #######            XX             XX             XX             X               X#X           X               
               X          X                  X   R        R#X#           #XX#           #XX#           #XX#           #X               X#X                           
               X#           XX               X             #X#           #XX#           #XX#           #XX#           #X               X#X          #X               
               X#           XX               X             #X#           #XX#           #XX#           #XX#           #X               X#X          #X               
               X#           XX               X             #X#           #XX#           #XX#           #XX#           #X               X#X          #X               
               X#           XX               X             #X#           #XX#           #XX#           #XX#           #X               X#X          #X               
               X#                            X             #X#           #XX#           #XX#           #XX#           #X                            #X               
               X#           XX               X             #X#           #XX#           #XX#           #XX#           #X               X#X          #X               
               X#           XX               X             #X#           #XX#           #XX#           #XX#           #X               X#X          #X               
               X#           XX               X             #X#           #XX#           #XX#           #XX#           #X               X#X          #X               
               X#           XX               X   R        RXX#           #XX#           #XX#           #XX#           #X               X#X          #X               
               X#           XX               X             XX#           #XX#           #XX#           #XX#           #X               X#X          #X               
               X#      X    XX               X             XX#           #XX#           #XX#           #XX#           #X               X#X          #X               
               X#      X    XX               X             XX#           #XX#           #XX#           #XX#           #X               X#X          #X               
               X#XXXXXXX    XX               XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX               XXX           X               
               X#########   #X               XX           XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX           XX               XXX           X               
               XXXXXXXXX    #X       X       X#           #XX#           #XX#           #XX#           #XX#           #X       X         X                           
               X#      X    #X  X   XXX   X  X#           #XX#           #XX#           #XX#           #XX#           #X  X   XXX   X  X            #X               
               X#           #X XXX  XXX  XXX X#           #XX#           #XX#           #XX#           #XX#           #X XXX  XXX  XXX X#X          #X               
               X#      X    #X  XX   X    X  X#           #XX#           #XX#           #XX#           #XX#           #X  X    X   XX  X#X          #X               
               X#      X    #XXXXXXX   XXXXXXX#           #XX#           #XX#           #XX#           #XX#           #XXXXXXX   XXXXXXX#           #X               
               X#      X    #XX X XXX XXX X XX#           #XX#           #XX#           #XX#           #XX#           #XX X XXX XXX X XX#           #X               
               X#      X    #XXXXXXX   XXXXXXX#           #XX#           #XX#           #XX#           #XX#           #XXXXXXX   XXXXXXX#           #X               
               X#      X    #X  X    X    X  X#           #XX#           #XX#           #XX#           #XX#           #X  X    X    X  X#           #X               
               X#      X    #X XXX  XXX  XXX X#           #XX#           #XX#           #XX#           #XX#           #X XXX  XXX  XXX X#           #X               
               X#      X    #X  X   XXX   X  X#           #XX#           #XX#           #XX#           #XX#           #X  X   XXX   X  X#           #X               
               XXXXXXXXX    #X       X       X#           #XX#           #XX#           #XX#           #XX#           #X       X                    #X               
               X#############X               X#           #XX#           #XX#           #XX#           #XX#           #X               X#           #X               
               X#XXXXXXX    #X               X# XPXX   XP #XX# XPX    XPX#XX# XPX    XPX#XX# XPX    XPX#XX# XPX    XPX#X               X#           #X               
               XXXXXXXXXXXX  X               XXXXC X XXXC XXXXXXC  XXXXC XXXXXXC  XXXXC XXXXXXC XX XXC XXXXXXC X XXXC XX               XX            X               
               X#XXXXXXXXXXX                     8      8       8      8       8      8       8      8       8      8                  X#            X               
               XX          X                                            .                                                              XX            X               
               X#                                                                                                                      X#            X               
               X#          X                                                                                                           X#           #X               
               X#          X                                                                                                           X#           #X               
               X#          X                                                                                                           X#           #X               
               X#          X                                                                                                           X#           #X               
               X#          X                                                                                                           X#           #X               
               X#          X                                                                                                           X#           #X               
               X#          X                                                                                                           X#           #X               
               X#          X                                                                                                           X#           #X               
               X#          X                                                                                                           X#           #X               
               X#          X                                                                                                           X#           #X               
               X#          X                                                                                                           X#           #X               
               XXXXXXXXXXXX#                  #              #              #              #              #                            XX            X               
               XXXXXXXXXXXX#                 X#X           XX#X           XX#X           XX#X           XX#X           X               XX            X               
               X                             X#X           XX#X           XX#X           XX#X           XX#X           X                                             
               X#                            X#X           XX#X           XX#X           XX#X           XX#X           X               X#            X               
               X#                            X#X           XX#X           XX#X           XX#X           XX#X           X               X#           #X               
               X#                            X#X           XX#X           XX#X           XX#X           XX#X           X               X#           #X               
               X#                            X#X           XX#X           XX#X           XX#X           XX#X           X               X#           #X               
               X#                            X#X           XX#X           XX#X           XX#X           XX#X           X               X#           #X               
               X#                            X#X           XX#X           XX#X           XX#X           XX#X           X               X#           #X               
               X#                            X#X           XX#X           XX#X           XX#X           XX#X           X               X#           #X               
               X#                            X#X           XX#X           XX#X           XX#X           XX#X           X               X#           #X               
               X#                            X#X           XX#X           XX#X           XX#X           XX#X           X               X#           #X               
               X#                            X#X           XX#X           XX#X           XX#X           XX#X           X               X#           #X               
               X#                            X#X           XX#X           XX#X           XX#X           XX#X           X               X#           #X               
               X#                            X#X           XX#X           XX#X           XX#X           XX#X           X               X#           #X               
               XXXXXXXXXXXX#                 X#X           XX#X           XX#X           XX#X           XX#X           X               XX            X               
               XXXXXXXXXXXX#                 X#X           #X#X           #X#X           #X#X           #X#X           X               XX            X               
               X                             X#X           XX#X           XX#X           XX#X           XX#X           X                                             
               X#                            X#X           XX#X           XX#X           XX#X           XX#X           X               X#            X               
               X#                            X#X           XX#X           XX#X           XX#X           XX#X           X               X#           #X               
               X#                            X#X           XX#X           XX#X           XX#X           XX#X           X               X#           #X               
               X#                            X#X           XX#X           XX#X           XX#X           XX#X           X               X#           #X               
               X#                            X#X           XX#X           XX#X           XX#x           XX#X           X               X#           #X               
               X#                            X#X           XX#X           XX#X           XX#X           XX#X           X               X#           #X               
               X#                            X#X           XX#X           XX#X           XX#X           XX#X           X               X#           #X               
               X#                            X#X           XX#X           XX#X           XX#X           XX#X           X               X#           #X               
               X#                            X#X           XX#X           XX#X           XX#X           XX#X           X               X#           #X               
               X#                            X#X           XX#X           XX#X           XX#X           XX#X           X               X#           #X               
               X#                            X#X           XX#X           XX#X           XX#X           XX#X           X               X#           #X               
               X#                            X#X           XX#X           XX#X           XX#X           XX#X           X               X#           #X               
               XXXXXXXXXXXX#XX               X#X           XX#X           XX#X           XX#X           XX#X           X               XX            X               
                                             X#X           #X#X           #X#X           #X#X           #X#X           X                                             
                                             X#X           XX#X           XX#X           XX#X           XX#X           X                                             
                                             X#X           XX#X           XX#X           XX#X           XX#X           X                                             
                                             X#X           XX#X           XX#X           XX#X           XX#X           X                                             
                                             X#X           XX#X           XX#X           XX#X           XX#X           X                                             
                                             X#X           XX#X           XX#X           XX#X           XX#X           X                                             
                                             X#X           XX#X           XX#X           XX#X           XX#X           X                                             
                                             X#X           XX#X           XX#X           XX#X           XX#X           X                                             
                                             X#X           XX#X           XX#X           XX#X           XX#X           X                                             
                                             X#X           XX#X           XX#X           XX#X           XX#X           X                                             
                                             X#X           XX#X           XX#X           XX#X           XX#X           X                                             
                                             X#X           XX#X           XX#X           XX#X           XX#X           X                                             
                                             X#X           XX#X           XX#X           XX#X           XX#X           X                                             
                                             X#X           XX#X           XX#X           XX#X           XX#X           X                                             
                                             X#XXXXXXXXXXXXXX#XXXXXXXXXXXXXX#XXXXXXXXXXXXXX#XXXXXXXXXXXXXX#XXXXXXXXXXXXX                                             
"""
        super().__init__(layout,detailedLayout,creator=creator,seed=seed, noContent=noContent)

        # add some tasks to keep npc busy
        self.toTransport = []
        roomsIndices = [0,1,2,3,5,6]
        roadBlocks = []
        for index in reversed(roomsIndices):
            room = self.tutorialCargoRooms[index]
            for item in room.storedItems:
                self.toTransport.append((room,(item.xPosition,item.yPosition)))

        # add more transport tasks to keep npcs busy
        x = 12
        while x > 8:
            y = 1
            while y < 9:
                self.toTransport.append((self.tutorialLab,(y,x)))
                y += 1
            x -= 1


        # add some tasks to keep npc busy
        self.addStorageQuest()

        # add scrap to be cleaned up
        self.scrapItems = [src.items.Scrap(20,52,3,creator=self),
                          src.items.Scrap(19,53,3,creator=self),
                          src.items.Scrap(20,51,3,creator=self),
                          src.items.Scrap(18,49,3,creator=self),
                          src.items.Scrap(21,53,3,creator=self),
                          src.items.Scrap(19,48,3,creator=self),
                          src.items.Scrap(20,52,3,creator=self),
                          src.items.Scrap(19,49,3,creator=self),
                          src.items.Scrap(20,48,3,creator=self),
                          src.items.Scrap(18,50,3,creator=self),
                          src.items.Scrap(18,51,3,creator=self)]
        self.addItems(self.scrapItems)

        # move roadblock periodically
        self.waitingRoom.addEvent(src.events.EndQuestEvent(4000,{"container":self,"method":"addRoadblock"},creator=self))

        # save internal state
        self.initialState = self.getState()

    '''
    add quest to move something from the lab to storage
    '''
    def addStorageQuest(self):
        if not self.toTransport:
            return

        task = self.toTransport.pop()

        # select target room
        roomIndices = [1,0,2,5,4]
        room = None
        for index in roomIndices:
            if self.tutorialStorageRooms[index].storageSpace:
               room = self.tutorialStorageRooms[index]
               break
        if not room:
            return

        # add quest to waiting room
        quest = src.quests.MoveToStorage([task[0].itemByCoordinates[task[1]][0]],room,creator=self,lifetime=400)
        quest.reputationReward = 1
        quest.endTrigger = {"container":self,"method":"addStorageQuest"}
        self.waitingRoom.quests.append(quest)

    '''
    add roadblock
    '''
    def addRoadblock(self):
        room = self.tutorialCargoRooms[8]
        item = room.storedItems[-1]
        outerQuest = quests.MetaQuestSequence([],creator=self)
        innerQuest = quests.TransportQuest(item,(None,127,81),creator=self)

        '''
        move character off the placed item
        bad code: should happen somewhere else
        '''
        def moveAway():
            outerQuest.character.yPosition -= 1

        innerQuest.endTrigger = moveAway
        outerQuest.addQuest(innerQuest)
        self.waitingRoom.quests.append(outerQuest)
        self.waitingRoom.addEvent(src.events.EndQuestEvent(gamestate.tick+4000,{"container":self,"method":"moveRoadblockToLeft"},creator=self))

    '''
    move roadblock
    bad code: should be more abstracted
    '''
    def moveRoadblockToLeft(self):
        # abort if roadblock is missing
        if not (127,81) in self.itemByCoordinates:
            return

        item = self.itemByCoordinates[(127,81)][0]
        outerQuest = quests.MetaQuestSequence([],creator=self)
        innerQuest = quests.TransportQuest(item,(None,37,81),creator=self)

        '''
        move character off the placed item
        bad code: should happen somewhere else
        '''
        def moveAway():
            outerQuest.character.yPosition -= 1

        innerQuest.endTrigger = moveAway
        outerQuest.addQuest(innerQuest)
        self.waitingRoom.quests.append(outerQuest)
        self.waitingRoom.addEvent(src.events.EndQuestEvent(gamestate.tick+4000,{"container":self,"method":"moveRoadblockToRight"},creator=self))

    '''
    move roadblock
    bad code: should be more abstracted
    '''
    def moveRoadblockToRight(self):
        # abort if roadblock is missing
        if not (37,81) in self.itemByCoordinates:
            return

        item = self.itemByCoordinates[(37,81)][0]
        outerQuest = quests.MetaQuestSequence([],creator=self)
        innerQuest = quests.TransportQuest(item,(None,127,81),creator=self)

        '''
        move character off the placed item
        bad code: should happen somewhere else
        '''
        def moveAway():
            outerQuest.character.yPosition -= 1

        innerQuest.endTrigger = moveAway
        outerQuest.addQuest(innerQuest)
        self.waitingRoom.quests.append(outerQuest)
        self.waitingRoom.addEvent(src.events.EndQuestEvent(gamestate.tick+4000,{"container":self,"method":"moveRoadblockToLeft"},creator=self))

# maping from strings to all items
# should be extendable
terrainMap = {
        "TutorialTerrain":TutorialTerrain,
        "Nothingness":Nothingness,
        "GameplayTest":GameplayTest,
        "ScrapField":ScrapField,
        "Desert":Desert,
}

'''
get item instances from dict state
'''
def getTerrainFromState(state, creator=None):
    terrain = terrainMap[state["objType"]](creator=creator,seed=state["initialSeed"],noContent=True)
    terrain.setState(state)
    loadingRegistry.register(terrain)
    return terrain


import src.items as items
import src.rooms as rooms
import src.overlays as overlays
import src.gameMath as gameMath

mainChar = None
messages = None
displayChars = None

class Coordinate(object):
    def __init__(self,x,y):
        self.x = x
        self.y = y

class Terrain(object):
    def __init__(self,layout,detailedLayout):
        self.itemsOnFloor = []
        self.characters = []
        self.rooms = []

        self.overlay = None

        self.itemByCoordinates = {}
        self.roomByCoordinates = {}
        self.watershedStart = []
        self.watershedNodeMap = {}
        self.foundPaths = {}
        self.applicablePaths = []
        self.obseveredCoordinates = {}
        self.superNodes = {}
        self.superNodePaths = {}
        self.watershedSuperNodeMap = {}
        self.watershedSuperCoordinates = {}
        self.foundSuperPaths = {}
        self.foundSuperPathsComplete = {}

        self.alarm = False

        mapItems = []
        self.detailedLayout = detailedLayout
        lineCounter = 0
        for layoutline in self.detailedLayout.split("\n")[1:]:
            rowCounter = 0
            for char in layoutline:
                if char in (" ",".",",","@"):
                    pass
                elif char == "X":
                    mapItems.append(items.Wall(rowCounter,lineCounter))
                elif char == "#":
                    mapItems.append(items.Pipe(rowCounter,lineCounter))
                elif char == "R":
                    pass
                elif char == "O":
                    mapItems.append(items.Item(displayChars.clamp_active,rowCounter,lineCounter))
                elif char == "0":
                    mapItems.append(items.Item(displayChars.clamp_inactive,rowCounter,lineCounter))
                elif char == "8":
                    mapItems.append(items.Chain(rowCounter,lineCounter))
                elif char == "C":
                    mapItems.append(items.Winch(rowCounter,lineCounter))
                elif char == "P":
                    mapItems.append(items.Pile(rowCounter,lineCounter))
                else:
                    mapItems.append(items.Item(displayChars.randomStuff2[((2*rowCounter)+lineCounter)%10],rowCounter,lineCounter))
                rowCounter += 1
            lineCounter += 1

        self.addItems(mapItems)

        roomsOnMap = []
        self.tutorialVat = None
        self.tutorialVatProcessing = None
        self.tutorialMachineRoom = None
        self.tutorialLab = None
        self.tutorialCargoRooms = []
        self.tutorialStorageRooms = []
        self.miniMechs = []
        self.wakeUpRoom = None
        lineCounter = 0
        for layoutline in layout.split("\n")[1:]:
            rowCounter = 0
            meta = False
            for char in layoutline:
                if meta:
                    meta = False
                    continue
                else:
                    meta = True
                if char in (".",","," ","t"):
                    self.watershedStart.extend([(rowCounter*15+1,lineCounter*15+1),(rowCounter*15+13,lineCounter*15+1),(rowCounter*15+1,lineCounter*15+13),(rowCounter*15+13,lineCounter*15+13)])
                    if char in ("."):
                        self.superNodes[(rowCounter,lineCounter)] = (rowCounter*15+1,lineCounter*15+1)

                if char in (".",","," "):
                    pass
                elif char == "X":
                    roomsOnMap.append(rooms.MechArmor(rowCounter,lineCounter,0,0))
                elif char == "V":
                    room = rooms.Vat2(rowCounter,lineCounter,2,2)
                    if not self.tutorialVat:
                        self.tutorialVat = room
                    roomsOnMap.append(room)
                elif char == "v":
                    room = rooms.Vat1(rowCounter,lineCounter,2,2)
                    if not self.tutorialVatProcessing:
                        self.tutorialVatProcessing = room
                    roomsOnMap.append(room)
                elif char == "Q":
                    roomsOnMap.append(rooms.InfanteryQuarters(rowCounter,lineCounter,1,2))
                elif char == "w":
                    room = rooms.WaitingRoom(rowCounter,lineCounter,1,2)
                    self.waitingRoom = room
                    roomsOnMap.append(room)
                elif char == "r":
                    roomsOnMap.append(rooms.Room1(rowCounter,lineCounter,1,2))
                elif char == "M":
                    room = rooms.TutorialMachineRoom(rowCounter,lineCounter,4,1)
                    if not self.tutorialMachineRoom:
                        self.tutorialMachineRoom = room
                    roomsOnMap.append(room)
                elif char == "L":
                    room = rooms.LabRoom(rowCounter,lineCounter,1,1)
                    if not self.tutorialLab:
                        self.tutorialLab = room
                    roomsOnMap.append(room)
                elif char == "C":
                    itemTypes = [items.Wall,items.Pipe]
                    if not rowCounter%2:
                        itemTypes.append(items.Lever)
                    if not rowCounter%3:
                        itemTypes.append(items.Furnace)
                    if not rowCounter%4:
                        itemTypes.append(items.Chain)
                    if not rowCounter%5:
                        itemTypes.append(items.Hutch)
                    if not rowCounter%6:
                        itemTypes.append(items.GrowthTank)
                    if not lineCounter%2:
                        itemTypes.append(items.Door)
                    if not lineCounter%3:
                        itemTypes.append(items.Boiler)
                    if not lineCounter%4:
                        itemTypes.append(items.Winch)
                    if not lineCounter%5:
                        itemTypes.append(items.Display)
                    if not lineCounter%6:
                        itemTypes.append(items.Commlink)
                    if not itemTypes:
                        itemTypes = [items.Pipe,items.Wall,items.Furnace,items.Boiler]
                    room = rooms.CargoRoom(rowCounter,lineCounter,3,0,itemTypes=itemTypes)
                    self.tutorialCargoRooms.append(room)
                    roomsOnMap.append(room)
                elif char == "U":
                    room = rooms.StorageRoom(rowCounter,lineCounter,3,0)
                    self.tutorialStorageRooms.append(room)
                    roomsOnMap.append(room)
                elif char == "?":
                    roomsOnMap.append(rooms.CpuWasterRoom(rowCounter,lineCounter,2,2))
                elif char == "t":
                    miniMech = rooms.MiniMech(rowCounter,lineCounter,2,2)
                    self.miniMechs.append(miniMech)
                    roomsOnMap.append(miniMech)
                elif char == "W":
                    wakeUpRoom = rooms.WakeUpRoom(rowCounter,lineCounter,1,1)
                    self.wakeUpRoom = wakeUpRoom
                    roomsOnMap.append(wakeUpRoom)
                elif char == "m":
                    room = rooms.MetalWorkshop(rowCounter,lineCounter,1,1)
                    self.metalWorkshop = room
                    roomsOnMap.append(room)
                elif char == "b":
                    room = rooms.ConstructionSite(rowCounter,lineCounter,1,1)
                    roomsOnMap.append(room)
                elif char == "K":
                    room = rooms.MechCommand(rowCounter,lineCounter,1,1)
                    roomsOnMap.append(room)
                else:
                    self.watershedStart.append((rowCounter*15+7,lineCounter*15+7))
                    pass
                rowCounter += 1
            lineCounter += 1

        self.testItems = [items.Scrap(20,52,3),items.Scrap(19,53,3),items.Scrap(20,51,3),items.Scrap(18,49,3),items.Scrap(21,53,3),items.Scrap(19,48,3),items.Scrap(20,52,3),items.Scrap(20,48,3),items.Scrap(18,50,3),items.Scrap(18,51,3)]
        self.addItems(self.testItems)

        self.addRooms(roomsOnMap)

        self.nonMovablecoordinates = {}
        for coordinate,itemList in self.itemByCoordinates.items():
            for item in itemList:
                if not item.walkable:
                    self.nonMovablecoordinates[coordinate] = True
        for room in self.rooms:
            for x in range(room.xPosition*15+room.offsetX,room.xPosition*15+room.offsetX+room.sizeX):
                for y in range(room.yPosition*15+room.offsetY,room.yPosition*15+room.offsetY+room.sizeY):
                     self.nonMovablecoordinates[(x,y)] = True

        for room in self.rooms:

            if room in self.miniMechs:
                continue

            xCoord = room.xPosition*15+room.offsetX+room.walkingAccess[0][0]
            yCoord = room.yPosition*15+room.offsetY+room.walkingAccess[0][1]

            if (xCoord,yCoord) in self.nonMovablecoordinates:
                del self.nonMovablecoordinates[(xCoord,yCoord)]

            if room.walkingAccess[0][0] == 0:
                xCoord -= 1
            elif room.walkingAccess[0][0] == room.sizeX-1:
                xCoord += 1

            if room.walkingAccess[0][1] == 0:
                yCoord -= 1
            elif room.walkingAccess[0][1] == room.sizeY-1:
                yCoord += 1
            self.watershedStart.append((xCoord,yCoord))

        self.watershedCoordinates = {}

        def walkBack(coordinate,bucket,path,last=1000):
            testCoordinates = [(coordinate[0]-1,coordinate[1]),(coordinate[0]+1,coordinate[1]),(coordinate[0],coordinate[1]-1),(coordinate[0],coordinate[1]+1)]
            nextStep = (None,(None,last))

            for testCoordinate in testCoordinates:
                if not testCoordinate in self.watershedCoordinates:
                    continue
                value = self.watershedCoordinates[testCoordinate]
                if not value[0] == bucket:
                    continue
                if value[1] < nextStep[1][1]:
                    nextStep = (testCoordinate,value)

            if nextStep[1][1] < last:
                path.append(nextStep[0])
                walkBack(nextStep[0],bucket,path,last=nextStep[1][1]+1)

        def watershed(counter,lastCoordinates):
            counter += 1
            
            if counter > 60:
                return

            newLast = {}
            for start,coordinates in lastCoordinates.items():
                newLastList = []

                for coordinate in coordinates:
                    newCoordinates = [(coordinate[0]-1,coordinate[1]),(coordinate[0]+1,coordinate[1]),(coordinate[0],coordinate[1]-1),(coordinate[0],coordinate[1]+1)]
                    for newCoordinate in newCoordinates:
                        if newCoordinate in self.nonMovablecoordinates:
                            continue
                        if newCoordinate in self.watershedCoordinates:
                            partnerNode = self.watershedCoordinates[newCoordinate][0]
                            if partnerNode == start:
                                continue
                            if (start,partnerNode) in self.foundPaths or (partnerNode,start) in self.foundPaths:
                                continue
                            path = []
                            walkBack(newCoordinate,start,path)
                            path.reverse()
                            path.append(newCoordinate)
                            walkBack(newCoordinate,partnerNode,path)
                            self.foundPaths[(start,partnerNode)] = path
                            path2 = path[:]
                            path2.reverse()
                            self.foundPaths[(partnerNode,start)] = path2
                            continue
                        newLastList.append(newCoordinate)
                        self.watershedCoordinates[newCoordinate] = (start,counter)

                newLast[start] = newLastList

            watershed(counter,newLast)

            for pair,path in self.foundPaths.items():
                if not pair[1] in self.watershedNodeMap[pair[0]]:
                    self.watershedNodeMap[pair[0]].append(pair[1])

                if not pair[0] in [pair[1]]:
                    self.watershedNodeMap[pair[1]].append(pair[0])

        last = {}
        for coordinate in self.watershedStart:
            self.watershedNodeMap[coordinate] = []

            self.watershedCoordinates[coordinate] = (coordinate,0)
            last[coordinate] = [coordinate]

        watershed(0,last)

        def walkBackSuper(coordinate,bucket,path,last=1000):
            testCoordinates = self.watershedNodeMap[coordinate]
            nextStep = (None,(None,last))

            for testCoordinate in testCoordinates:
                if not testCoordinate in self.watershedSuperCoordinates:
                    continue
                value = self.watershedSuperCoordinates[testCoordinate]
                if not value[0] == bucket:
                    continue
                if value[1] < nextStep[1][1]:
                    nextStep = (testCoordinate,value)

            if nextStep[1][1] < last:
                path.append(nextStep[0])
                walkBackSuper(nextStep[0],bucket,path,last=nextStep[1][1]+1)

        def superWatershed(counter,lastCoordinates):
            counter += 1
            
            if counter > 60:
                return

            newLast = {}
            for start,coordinates in lastCoordinates.items():
                newLastList = []

                for coordinate in coordinates:
                    newCoordinates = self.watershedNodeMap[coordinate]
                    for newCoordinate in newCoordinates:
                        if newCoordinate in self.watershedSuperCoordinates:
                            partnerSuperNode = self.watershedSuperCoordinates[newCoordinate][0]
                            if partnerSuperNode == start:
                                continue
                            if (start,partnerSuperNode) in self.foundSuperPaths or (partnerSuperNode,start) in self.foundSuperPaths:
                                continue
                            path = []
                            walkBackSuper(newCoordinate,start,path)
                            path.reverse()
                            path.append(newCoordinate)
                            walkBackSuper(newCoordinate,partnerSuperNode,path)
                            self.foundSuperPaths[(partnerSuperNode,start)] = path
                            self.foundSuperPaths[(start,partnerSuperNode)] = path

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
                        newLastList.append(newCoordinate)
                        self.watershedSuperCoordinates[newCoordinate] = (start,counter)

                newLast[start] = newLastList

            for pair,path in self.foundSuperPaths.items():
                if not pair[1] in self.watershedSuperNodeMap[pair[0]]:
                    self.watershedSuperNodeMap[pair[0]].append(pair[1])

                if not pair[0] in self.watershedSuperNodeMap[pair[1]]:
                    self.watershedSuperNodeMap[pair[1]].append(pair[0])


            superWatershed(counter,newLast)

        last = {}
        for bigCoord,smallCoord in self.superNodes.items():
            self.watershedSuperNodeMap[smallCoord] = []

            self.watershedSuperCoordinates[smallCoord] = (smallCoord,0)
            last[smallCoord] = [smallCoord]
        superWatershed(0,last)

        """
        for startNode in self.superNodes:
            for endNode in self.superNodes:
                if startNode == endNode:
                    continue
                start = self.superNodes[startNode]
                end = self.superNodes[endNode]

                start = Coordinate(start[0],start[1])
                end = Coordinate(end[0],end[1])

                self.superNodePaths[(startNode,endNode)] = self.findWayNodeBased(start,end,[self.superNodes[startNode]])
        """

        print(self.superNodePaths)

        self.superNodePaths
        self.overlay = self.addWatershedOverlay
        self.overlay = None
                    
        # add some tasks to keep npc busy
        toTransport = []
        x = 12
        while x > 8:
            y = 1
            while y < 9:
                toTransport.append((y,x))
                y += 1
            x -= 1
        def addStorageQuest():
            if not toTransport:
                return
            quest = quests.MoveToStorage([self.tutorialLab.itemByCoordinates[toTransport.pop()][0]],self.tutorialStorageRooms[1])
            quest.reputationReward = 1
            quest.endTrigger = addStorageQuest
            self.waitingRoom.quests.append(quest)
        addStorageQuest()

    def removeCharacter(self,character):
        self.characters.remove(character)
        character.room = None
        character.terrain = None

    def addWatershedOverlay(self,chars):
        import urwid
        colors = ["#fff","#ff0","#f0f","#0ff","#f00","#0f0","#00f","#55f","#f55","#5f5","#055","#505","#550"]
        colorByType = {}

        mainCharPair = None
        if mainChar.terrain:
            mainCharPair = self.watershedCoordinates[(mainChar.xPosition,mainChar.yPosition)][0]

        counter = 0
        for item in self.watershedStart:
            colorByType[item] = colors[counter%len(colors)]
            counter += 1

        for coordinate,value in self.watershedCoordinates.items():
            if value[1] < 10:
                display = "0"+str(value[1])
            else:
                display = str(value[1])

            if mainCharPair == value[0]:
                chars[coordinate[1]][coordinate[0]] = (urwid.AttrSpec("#333","default"),display)
            else:
                chars[coordinate[1]][coordinate[0]] = (urwid.AttrSpec(colorByType[value[0]],"default"),display)

        counter = 3
        for dualPair,path in self.foundPaths.items():
            for coordinate in path:
                if dualPair in self.applicablePaths:
                    chars[coordinate[1]][coordinate[0]] =  (urwid.AttrSpec("#888","default"),"XX")
                else:
                    chars[coordinate[1]][coordinate[0]] =  (urwid.AttrSpec(colors[counter%len(colors)],"default"),"XX")
            counter += 1

        for newCoordinate,counter in self.obseveredCoordinates.items():
            if counter < 10:
                display = "0"+str(counter)
            else:
                display = str(counter)
            chars[newCoordinate[1]][newCoordinate[0]] =  (urwid.AttrSpec("#888","default"),display)

        chars[mainChar.yPosition][mainChar.xPosition] =  mainChar.display

    def findPath(self,start,end):


        self.applicablePaths = {}
        self.obseveredCoordinates = {}

        if not start in self.watershedCoordinates:
            return
        startPair = self.watershedCoordinates[start][0]

        for dualPair,path in self.foundPaths.items():
            if startPair in dualPair:
                self.applicablePaths[dualPair] = path

        if not startPair in self.watershedSuperCoordinates:
            return
        startSuper = self.watershedSuperCoordinates[startPair]

        entryPoint = self.mark([start])
        if not entryPoint:
            return

        startCoordinate = Coordinate(entryPoint[0][0],entryPoint[0][1])
        startNode = entryPoint[1][1]
        pathToStartNode = self.foundPaths[entryPoint[1]][self.foundPaths[entryPoint[1]].index((startCoordinate.x,startCoordinate.y))+1:]

        self.applicablePaths = {}
        self.obseveredCoordinates = {}

        if not end in self.watershedCoordinates:
            return
        endPair = self.watershedCoordinates[end][0]

        for dualPair,path in self.foundPaths.items():
            if endPair in dualPair:
                self.applicablePaths[dualPair] = path

        if not endPair in self.watershedSuperCoordinates:
            return
        endSuper = self.watershedSuperCoordinates[endPair]

        exitPoint = self.mark([end])
        if not exitPoint:
            return

        endCoordinate = Coordinate(exitPoint[0][0],exitPoint[0][1])
        endNode = exitPoint[1][0]
        pathToEndNode = self.foundPaths[exitPoint[1]][1:self.foundPaths[exitPoint[1]].index((endCoordinate.x,endCoordinate.y))+1]

        path = []
        try:
            if not startSuper[0] == endSuper[0]:
                if endSuper[0] in self.watershedSuperNodeMap[startSuper[0]]:
                    path = self.foundSuperPathsComplete[(startSuper[0],endSuper[0])]
                else:
                    path = self.foundSuperPathsComplete[(startSuper[0],self.watershedSuperNodeMap[startSuper[0]][0])]+self.foundSuperPathsComplete[(self.watershedSuperNodeMap[startSuper[0]][0],endSuper[0])]
                path = pathToStartNode + self.findWayNodeBased(Coordinate(entryPoint[1][1][0],entryPoint[1][1][1]),Coordinate(startSuper[0][0],startSuper[0][1]))+path
                path = path + self.findWayNodeBased(Coordinate(endSuper[0][0],endSuper[0][1]),Coordinate(endNode[0],endNode[1]))+pathToEndNode
            else:
                path = pathToStartNode + self.findWayNodeBased(Coordinate(startNode[0],startNode[1]),Coordinate(endNode[0],endNode[1]))+pathToEndNode
        except Exception as e:
            import traceback
            messages.append("Error: "+str(e))
            messages.append(traceback.format_exc().splitlines()[-3])
            messages.append(traceback.format_exc().splitlines()[-2])
            messages.append(traceback.format_exc().splitlines()[-1])

        if not entryPoint[2][0] == start:
            entryPoint[2].reverse()
        path = entryPoint[2]+path+exitPoint[2][1:]
        return gameMath.removeLoops(path)

    def markWalkBack(self,coordinate,obseveredCoordinates,pathToEntry,counter=0,limit=1000):
        pathToEntry.append((coordinate[0],coordinate[1]))

        found = None
        foundValue = 10000
        for newCoordinate in [(coordinate[0]-1,coordinate[1]),(coordinate[0],coordinate[1]-1),(coordinate[0]+1,coordinate[1]),(coordinate[0],coordinate[1]+1)]:
            if not newCoordinate in obseveredCoordinates:
                continue
            if obseveredCoordinates[newCoordinate] >= limit:
                continue
            if (not found) or (obseveredCoordinates[found] < obseveredCoordinates[newCoordinate]):
                found = newCoordinate

        if found:
            self.markWalkBack(found,obseveredCoordinates,pathToEntry,counter+1, obseveredCoordinates[found])

    def mark(self,coordinates,counter=0,obseveredCoordinates={}):
        if counter > 30:
            return

        newCoordinates = []
        if not counter == 0:
            for coordinate in coordinates:
                for newCoordinate in [(coordinate[0]-1,coordinate[1]),(coordinate[0],coordinate[1]-1),(coordinate[0]+1,coordinate[1]),(coordinate[0],coordinate[1]+1)]:
                    if newCoordinate in self.nonMovablecoordinates:
                        continue
                    if newCoordinate in self.obseveredCoordinates:
                        continue
                    newCoordinates.append(newCoordinate)
        else:
            newCoordinates.append(coordinates[0])

        for newCoordinate in newCoordinates:
            self.obseveredCoordinates[newCoordinate] = counter

            for dualPair,path in self.applicablePaths.items():
                if newCoordinate in path:
                    pathToEntry = []
                    self.markWalkBack(newCoordinate,self.obseveredCoordinates,pathToEntry)
                    return (newCoordinate,dualPair,pathToEntry)

        if newCoordinates:
            return self.mark(newCoordinates,counter+1,obseveredCoordinates)

    def findWayNodeBased(self,start,end):
        index = 0

        nodeMap = {}
        neighbourNodes = []

        doLoop = True

        for node in ((start.x,start.y),):
            neighbourNodes.append(node)
            nodeMap[node] = (None,0)

            if node == (end.x,end.y):
                lastNode = node
                doLoop = False

        lastNode = None
        counter = 1
        while doLoop:
            for node in neighbourNodes[:]:
                for node2 in self.watershedNodeMap[node]:
                    if not node2 in neighbourNodes:
                        neighbourNodes.append(node2)
                        nodeMap[node2] = (node,counter)
                    if node2 == (end.x,end.y):
                        lastNode = node2
                        doLoop = False
            counter += 1

            if counter == 10:
                raise Exception("unable to find end node to "+str(end.x)+" / "+str(end.y))

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

    def addRooms(self,rooms):
        self.rooms.extend(rooms)
        for room in rooms:
            room.terrain = self
            if (room.xPosition,room.yPosition) in self.roomByCoordinates:
                self.roomByCoordinates[(room.xPosition,room.yPosition)].append(room)
            else:
                self.roomByCoordinates[(room.xPosition,room.yPosition)] = [room]


    def addItems(self,items):
        self.itemsOnFloor.extend(items)
        for item in items:
            item.terrain = self
            if (item.xPosition,item.yPosition) in self.itemByCoordinates:
                self.itemByCoordinates[(item.xPosition,item.yPosition)].append(item)
            else:
                self.itemByCoordinates[(item.xPosition,item.yPosition)] = [item]

    def render(self):
        global mapHidden
        if mainChar.room == None:
            mapHidden = False
        else:
            if mainChar.room.open:
                mapHidden = False
            else:
                mapHidden = True

        self.hidden = mapHidden

        chars = []
        for i in range(0,250):
            line = []
            for j in range(0,250):
                if not mapHidden:
                    line.append(displayChars.floor)
                else:
                    line.append(displayChars.void)
            chars.append(line)

        overlays.PathsOverlay().apply(chars,self)

        for room in self.rooms:
            if mainChar.room == room:
                room.hidden = False
            else:
                if not mapHidden and room.open and room.hidden:
                    room.hidden = False
                    room.applySkippedAdvances()
                else:
                    room.hidden = True
                
        if not mapHidden:

            pos = None
            roomContainer = None
            if mainChar.room == None:
                pos = (mainChar.xPosition//15,mainChar.yPosition//15)
                roomContainer = mainChar.terrain
            else:
                pos = (mainChar.room.xPosition,mainChar.yPosition)
                roomContainer = mainChar.room.terrain

            roomCandidates = []
            possiblePositions = set()
            for i in range(-1,2):
                for j in range(-1,2):
                    possiblePositions.add((pos[0]-i,pos[1]-j))
            for coordinate in possiblePositions:
                if coordinate in self.roomByCoordinates:
                    roomCandidates.extend(self.roomByCoordinates[coordinate])

            for room in roomCandidates:
                if room.open:
                    room.hidden = False
                    room.applySkippedAdvances()
                

        if not mapHidden:
            for item in self.itemsOnFloor:
                chars[item.yPosition][item.xPosition] = item.display

        for room in self.rooms:
            if mapHidden and room.hidden :
                continue

            renderedRoom = room.render()
            
            xOffset = room.xPosition*15+room.offsetX
            yOffset = room.yPosition*15+room.offsetY

            lineCounter = 0
            for line in renderedRoom:
                rowCounter = 0
                for char in line:
                    chars[lineCounter+yOffset][rowCounter+xOffset] = char
                    rowCounter += 1
                lineCounter += 1

        if not mapHidden:
            overlays.QuestMarkerOverlay().apply(chars,mainChar,displayChars)
            overlays.NPCsOverlay().apply(chars,self)
            overlays.MainCharOverlay().apply(chars,mainChar)

        self.lastRender = chars

        if self.overlay:
            self.overlay(chars)

        return chars

    def getAffectedByRoomMovementNorth(self,room,force=1,movementBlock=set()):
        # check for collision
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

        roomCollisions = set()
        for roomCandidate in roomCandidates:
            if (room.yPosition*15 + room.offsetY) == (roomCandidate.yPosition*15+roomCandidate.offsetY+roomCandidate.sizeY):
                if (room.xPosition*15+room.offsetX < roomCandidate.xPosition*15+roomCandidate.offsetX+roomCandidate.sizeX) and (room.xPosition*15+room.offsetX+room.sizeX > roomCandidate.xPosition*15+roomCandidate.offsetX):
                    roomCollisions.add(roomCandidate)

        for roomCollision in roomCollisions:
            movementBlock.add(roomCollision)
            self.getAffectedByRoomMovementNorth(roomCollision,force=force,movementBlock=movementBlock)

        posX = room.xPosition*15+room.offsetX-1
        maxX = room.xPosition*15+room.offsetX+room.sizeX-1
        while posX < maxX:
            posX += 1
            if (posX,room.yPosition*15+room.offsetY-1) in self.itemByCoordinates:
                movementBlock.update(self.itemByCoordinates[(posX,room.yPosition*15+room.offsetY-1)])

    def moveRoomNorth(self,room,force=1,movementBlock=[]):
        if room.offsetY > -5:
            room.offsetY -= 1
        else:
            room.offsetY = 9
            if (room.xPosition,room.yPosition) in self.roomByCoordinates:
                self.roomByCoordinates[(room.xPosition,room.yPosition)].remove(room)
                if not len(self.roomByCoordinates[(room.xPosition,room.yPosition)]):
                    del self.roomByCoordinates[(room.xPosition,room.yPosition)]
            room.yPosition -= 1
            if (room.xPosition,room.yPosition) in self.roomByCoordinates:
                self.roomByCoordinates[(room.xPosition,room.yPosition)].append(room)
            else:
                self.roomByCoordinates[(room.xPosition,room.yPosition)] = [room]

    def getAffectedByRoomMovementSouth(self,room,force=1,movementBlock=set()):
        # check for collision
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

        roomCollisions = set()
        for roomCandidate in roomCandidates:
            if (room.yPosition*15 + room.offsetY+room.sizeY) == (roomCandidate.yPosition*15+roomCandidate.offsetY):
                if (room.xPosition*15+room.offsetX < roomCandidate.xPosition*15+roomCandidate.offsetX+roomCandidate.sizeX) and (room.xPosition*15+room.offsetX+room.sizeX > roomCandidate.xPosition*15+roomCandidate.offsetX):
                    roomCollisions.add(roomCandidate)

        for roomCollision in roomCollisions:
            movementBlock.add(roomCollision)
            self.getAffectedByRoomMovementSouth(roomCollision,force=force,movementBlock=movementBlock)

        posX = room.xPosition*15+room.offsetX-1
        maxX = room.xPosition*15+room.offsetX+room.sizeX-1
        while posX < maxX:
            posX += 1
            if (posX,room.yPosition*15+room.offsetY+room.sizeY) in self.itemByCoordinates:
                movementBlock.update(self.itemByCoordinates[(posX,room.yPosition*15+room.offsetY+room.sizeY)])

    def moveRoomSouth(self,room,force=1,movementBlock=[]):
        if room.offsetY < 9:
            room.offsetY += 1
        else:
            room.offsetY = -5
            if (room.xPosition,room.yPosition) in self.roomByCoordinates:
                self.roomByCoordinates[(room.xPosition,room.yPosition)].remove(room)
                if not len(self.roomByCoordinates[(room.xPosition,room.yPosition)]):
                    del self.roomByCoordinates[(room.xPosition,room.yPosition)]
            room.yPosition += 1
            if (room.xPosition,room.yPosition) in self.roomByCoordinates:
                self.roomByCoordinates[(room.xPosition,room.yPosition)].append(room)
            else:
                self.roomByCoordinates[(room.xPosition,room.yPosition)] = [room]

    def getAffectedByRoomMovementWest(self,room,force=1,movementBlock=set()):
        # check for collision
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

        roomCollisions = set()
        for roomCandidate in roomCandidates:
            if (room.xPosition*15 + room.offsetX) == (roomCandidate.xPosition*15+roomCandidate.offsetX+roomCandidate.sizeX):
                if (room.yPosition*15+room.offsetY < roomCandidate.yPosition*15+roomCandidate.offsetY+roomCandidate.sizeY) and (room.yPosition*15+room.offsetY+room.sizeY > roomCandidate.yPosition*15+roomCandidate.offsetY):
                    roomCollisions.add(roomCandidate)

        for roomCollision in roomCollisions:
            movementBlock.add(roomCollision)
            self.getAffectedByRoomMovementWest(roomCollision,force=force,movementBlock=movementBlock)

        posY = room.yPosition*15+room.offsetY-1
        maxY = room.yPosition*15+room.offsetY+room.sizeY-1
        while posY < maxY:
            posY += 1
            if (room.xPosition*15+room.offsetX-1,posY) in self.itemByCoordinates:
                movementBlock.update(self.itemByCoordinates[(room.xPosition*15+room.offsetX-1,posY)])

    def moveRoomWest(self,room):
        if room.offsetX > -5:
            room.offsetX -= 1
        else:
            room.offsetX = 9
            if (room.xPosition,room.yPosition) in self.roomByCoordinates:
                self.roomByCoordinates[(room.xPosition,room.yPosition)].remove(room)
                if not len(self.roomByCoordinates[(room.xPosition,room.yPosition)]):
                    del self.roomByCoordinates[(room.xPosition,room.yPosition)]
            room.xPosition -= 1
            if (room.xPosition,room.yPosition) in self.roomByCoordinates:
                self.roomByCoordinates[(room.xPosition,room.yPosition)].append(room)
            else:
                self.roomByCoordinates[(room.xPosition,room.yPosition)] = [room]

    def getAffectedByRoomMovementEast(self,room,force=1,movementBlock=set()):
        # check for collision
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

        roomCollisions = set()
        for roomCandidate in roomCandidates:
            if (room.xPosition*15 + room.offsetX+ room.sizeX) == (roomCandidate.xPosition*15+roomCandidate.offsetX):
                if (room.yPosition*15+room.offsetY < roomCandidate.yPosition*15+roomCandidate.offsetY+roomCandidate.sizeY) and (room.yPosition*15+room.offsetY+room.sizeY > roomCandidate.yPosition*15+roomCandidate.offsetY):
                    roomCollisions.add(roomCandidate)

        for roomCollision in roomCollisions:
            movementBlock.add(roomCollision)
            self.getAffectedByRoomMovementEast(roomCollision,force=force,movementBlock=movementBlock)

        posY = room.yPosition*15+room.offsetY-1
        maxY = room.yPosition*15+room.offsetY+room.sizeY-1
        while posY < maxY:
            posY += 1
            if (room.xPosition*15+room.offsetX+room.sizeX,posY) in self.itemByCoordinates:
                movementBlock.update(self.itemByCoordinates[(room.xPosition*15+room.offsetX+room.sizeX,posY)])


    def moveRoomEast(self,room):
        if room.offsetX < 9:
            room.offsetX += 1
        else:
            room.offsetX = -5
            if (room.xPosition,room.yPosition) in self.roomByCoordinates:
                self.roomByCoordinates[(room.xPosition,room.yPosition)].remove(room)
                if not len(self.roomByCoordinates[(room.xPosition,room.yPosition)]):
                    del self.roomByCoordinates[(room.xPosition,room.yPosition)]
            room.xPosition += 1
            if (room.xPosition,room.yPosition) in self.roomByCoordinates:
                self.roomByCoordinates[(room.xPosition,room.yPosition)].append(room)
            else:
                self.roomByCoordinates[(room.xPosition,room.yPosition)] = [room]

    def teleportRoom(self,room,newPosition):
        oldPosition = (room.xPosition,room.yPosition)
        if oldPosition in self.roomByCoordinates:
            self.roomByCoordinates[oldPosition].remove(room)
            if not len(self.roomByCoordinates[oldPosition]):
                del self.roomByCoordinates[oldPosition]
        if newPosition in self.roomByCoordinates:
            self.roomByCoordinates[newPosition].append(room)
        else:
            self.roomByCoordinates[newPosition] = [room]
        room.xPosition = newPosition[0]
        room.yPosition = newPosition[1]

class TutorialTerrain(Terrain):
    def __init__(self):

        layout = """
XXXXXXXXXXXXXXXXXXXXXX
XXXXXXXXXXXXXXXXXXXXXX
XX??????????????????XX
XX??????????????????XX
XX?? . . . . . . .??XX
XX?? .?????????? .??XX
XX?? .?????????? .??XX
XX?? . . . . . . .??XX
XX??  ??????????  ??XX
XX??  ??????????  ??XX
XX??  ??????????  ??XX
XXXXXXXXXXXXXXXXXXXXXX"""
        layout = """
X X X X X X X X X X X
X X X X X X X X X X X
X V v ? b r ? ? v V X
X O . t         . O X
X w   M Q K ? ?   L X
X W   ? ? ? ? ?   m X
X U .           . U X
X U   C C C C C   U X
X U   C C C C C t U X
X X X C C C C C X X X """
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
               #X         RX####R        R    #R        R                XXXXXXXXXXXXXX XXXXXXXXXXXXXX XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX               
               #X          XXXX###### ########XXXX8  O                                                                                              X               
               #X             XXXXXXX XXXXXXXXX   8                                                                                                  X               
               #XXXXXXXXXX  X                     8                                                                                                  X              
               ############ #X                    8                                                                                   XXXXXXXXXXXXXXXX              
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
               XXXXXXXXXXX   X                                                                                                           X                           
               #############                                                                                                           X X          #X               
               XXXXXXXXXXXXXXX               X#####    #######            XX             XX             XX             X               X             X               
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
               X#XXXXXXX    XX               XXXXXXXXXXXXX XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX               XXX           X               
               X#########   #X               XXXXXXXXXXXXX XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX               XXX           X               
               XXXXXXXXX    #X       X       X#            X                                                                   X         X                           
               X#      X    #X  X   XXX   X  X#           #XX#           #XX#           #XX#           #XX#           #X  X   XXX   X  X            #X               
               X#           #X XXX  XXX  XXX X#           #XX#           #XX#           #XX#           #XX#           #X XXX  XXX  XXX X#X          #X               
               X#      X    #X  X    X    X  X#           #XX#           #XX#           #XX#           #XX#           #X  X    X    X  X#X          #X               
               X#      X    #XXXXXXX   XXXXXXX#           #XX#           #XX#           #XX#           #XX#           #XXXXXXX   XXXXXXX#           #X               
               X#      X    #XX X XXX XXX X XX#           #XX#           #XX#           #XX#           #XX#           #XX X XXX XXX X XX#           #X               
               X#      X    #XXXXXXX   XXXXXXX#           #XX#           #XX#           #XX#           #XX#           #XXXXXXX   XXXXXXX#           #X               
               X#      X    #X  X    X    X  X#           #XX#           #XX#           #XX#           #XX#           #X  X    X    X  X#           #X               
               X#      X    #X XXX  XXX  XXX X#           #XX#           #XX#           #XX#           #XX#           #X XXX  XXX  XXX X#           #X               
               X#      X    #X  X   XXX   X  X#           #XX#           #XX#           #XX#           #XX#           #X  X   XXX   X  X#           #X               
               XXXXXXXXX    #X       X       X#           #XX#           #XX#           #XX#           #XX#           #X       X                    #X               
               X######### ###X               X#           #XX#           #XX#           #XX#           #XX#           #X               X#           #X               
               X#XXXXXXX    #X               X# XPXX   XP #XX# XPX    XPX#XX# XPX    XPX#XX# XPX    XPX#XX# XPX    XPX#X               X#           #X               
               XXXXXXXXXXXX  X               XXXXC X XXXC XXXXXXC XXXXXC XXXXXXC  XXXXC XXXXXXC XX XXC XXXXXXC X XXXC XX               XX            X               
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
        super().__init__(layout,detailedLayout)


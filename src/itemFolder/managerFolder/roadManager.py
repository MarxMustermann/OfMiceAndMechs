import src

'''
gomode item for terraforming and things
'''
class RoadManager(src.items.ItemNew):
    type = "RoadManager"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="road manager",creator=None,noId=False):
        super().__init__("RM",xPosition,yPosition,name=name,creator=creator,runsJobOrders=True)

        self.roadNetwork = {}
        self.centerDirection = {}
        self.connections = {}
        self.center = None
        self.pathingNodes = {}
        self.pathsToCenter = {}
        self.pathsFromCenter = {}

    def generatePaths(self,character):
        text = ""
        for (key,value,) in self.pathingNodes.items():
            text += "%s: %s  => center\n"%(key,value["coordinate"],)
            text += "  "
            node = value["coordinate"]
            counter = 0
            backPath = []
            while not node == self.center:
                counter += 1
                if counter == 100:
                    break
                    raise Exception #pathfining loop

                if node == self.center or not node in self.centerDirection:
                    break

                backPath.append(node)
                direction = self.centerDirection[node]
                node = (node[0]+direction[0],node[1]+direction[1])
            backPath.append(self.center)

            self.pathsFromCenter[value["coordinate"]] = list(reversed(backPath))
            self.pathsToCenter[value["coordinate"]] = backPath

            text += "  %s\n"%(list(reversed(backPath)),)
            text += "  %s\n"%(backPath,)

            commandItem = src.items.itemMap["Command"](value["coordinate"][0]*15+7,value["coordinate"][1]*15+6)
            command = ""
            lastNode = None
            for node in self.pathsToCenter[value["coordinate"]]:
                if lastNode == None:
                    lastNode = node
                    continue
                
                if lastNode[0] > node[0]:
                    command += "as11awa"
                if lastNode[0] < node[0]:
                    command += "ds11dwd"
                if lastNode[1] > node[1]:
                    command += "11wawwd"
                if lastNode[1] < node[1]:
                    command += "dssa11s"

                lastNode = node
            commandItem.setPayload(list(command))

            terrain = self.getTerrain()
            terrain.addItem(commandItem)

        self.submenue = src.interaction.OneKeystrokeMenu(text)
        character.macroState["submenue"] = self.submenue


    def getJobOrderTriggers(self):
        result = super().getJobOrderTriggers()
        self.addTriggerToTriggerMap(result,"clear paths",self.jobOrderClearPaths)
        self.addTriggerToTriggerMap(result,"add pathing node",self.jobOrderAddPathingNode)
        self.addTriggerToTriggerMap(result,"add road",self.doAddRoad)
        self.addTriggerToTriggerMap(result,"print paths",self.doPrintPaths)
        return result

    def getCommandStringForPath(self,start,end):
        if not (start == self.center or end == self.center):
            raise Exception # invalid path
            return "invalid"

        command = ""

        if start == self.center:
            basePath = self.pathsFromCenter[end]
            if basePath[0][1] < basePath[1][1]:
                command += "assd13s"
            if basePath[0][1] > basePath[1][1]:
                command += "13wawwd"
            if basePath[0][0] > basePath[1][0]:
                command += "as13awa"
            if basePath[0][0] < basePath[1][0]:
                command += "ds13dwd"
            basePath = basePath[1:]
        else:
            basePath = self.pathsToCenter[start]
        self.character.addMessage(basePath)

        lastNode = None
        for node in basePath:
            if lastNode == None:
                lastNode = node
                continue
            
            if lastNode[0] > node[0]:
                command += "as11awa"
            if lastNode[0] < node[0]:
                command += "ds11dwd"
            if lastNode[1] > node[1]:
                command += "11wawwd"
            if lastNode[1] < node[1]:
                command += "dssa11s"

            lastNode = node
        return command

    def doPrintPaths(self,task,context):
        self.generatePaths(context["character"])
        self.character = context["character"]
        context["jobOrder"].information["pathTo"] = self.getCommandStringForPath(self.center,task["to"])
        context["jobOrder"].information["pathFrom"] = self.getCommandStringForPath(task["to"],self.center) 

        context["character"].runCommandString("200.")

    def jobOrderAddPathingNode(self,task,context):
        if not self.center:
            self.center = (self.room.xPosition,self.room.yPosition)
            self.roadNetwork[self.center] = {"type":"roomCenterBlocked"}
            
        if not "offset" in task:
            task["offset"] = [7,7]
        self.doAddPathingNode(task)

    def jobOrderClearPaths(self,task,context):
        self.doClearPaths(task["coordinate"][0],task["coordinate"][1])

    def doAddRoad(self,task,context):
        terrain = self.getTerrain()

        bigX = task["coordinate"][0]
        bigY = task["coordinate"][1]

        for pos in [(6,6),(6,7),(6,8),(7,8),(8,8),(8,7),(8,6),(7,6)]:
            floorPlate = src.items.itemMap["FloorPlate"](bigX*15+pos[0],bigY*15+pos[1])
            terrain.addItem(floorPlate)
        commandItem = src.items.itemMap["Command"](bigX*15+7,bigY*15+6)
        terrain.addItem(commandItem)

        if not self.roadNetwork:
            self.roadNetwork[(self.room.xPosition,self.room.yPosition)] = {"type":"centerBlocked"}
            #self.roadNetwork[(bigX,bigY)] = {"type":"centerBlocked"}
        
        neighbours = [(bigX+1,bigY),(bigX-1,bigY),(bigX,bigY-1),(bigX,bigY+1)]
        import random
        random.shuffle(neighbours)

        foundNeighbourSlot = None
        for slot in neighbours:
            if slot in self.roadNetwork:
                foundNeighbourSlot = slot
                break

        if not foundNeighbourSlot:
            return

        slotCoordinate = (bigX,bigY)

        self.roadNetwork[(bigX,bigY)] = {"type":"centerBlocked"}

        index = 0
        if foundNeighbourSlot[0] == slotCoordinate[0]:
            index = 1
        
        changePerStep = 1
        if foundNeighbourSlot[index] < slotCoordinate[index]:
            changePerStep = -1

        if index == 0 and changePerStep == 1:
            commandString = "ds11dwd"
        if index == 1 and changePerStep == 1:
            commandString = "dssa11s"
        if index == 0 and changePerStep == -1:
            commandString = "as11awa"
        if index == 1 and changePerStep == -1:
            commandString = "11wawwd"
        commandItem.setPayload(list(commandString))

        direction = [0,0]
        direction[index] = changePerStep
        self.centerDirection[(bigX,bigY)] = tuple(direction)

        startPos = [7,7]
        startPos[index] += changePerStep
        for i in range(0,12):
            startPos[index] += changePerStep
            if i in (5,6,):
                continue
            floorPlate = src.items.itemMap["FloorPlate"](bigX*15+startPos[0],bigY*15+startPos[1])
            terrain.addItem(floorPlate)

    def doAddPathingNode(self,task):
        terrain = self.getTerrain()

        nodeName = task["nodeName"]
        bigX = task["coordinate"][0]
        bigY = task["coordinate"][1]
        offsetX = task["offset"][0]
        offsetY = task["offset"][1]

        if not self.center:
            self.center == (bigX,bigY)
            self.roadNetwork[self.center] = {"type":"centerBlocked"}
        else:
            neighbours = [(bigX+1,bigY),(bigX-1,bigY),(bigX,bigY-1),(bigX,bigY+1)]
            import random
            random.shuffle(neighbours)

            foundNeighbourSlot = None
            for slot in neighbours:
                if slot in self.roadNetwork:
                    foundNeighbourSlot = slot
                    break

            if not foundNeighbourSlot:
                return

            slotCoordinate = (bigX,bigY)

            self.roadNetwork[(bigX,bigY)] = {"type":"centerBlocked"}

            index = 0
            if foundNeighbourSlot[0] == slotCoordinate[0]:
                index = 1
            
            changePerStep = 1
            if foundNeighbourSlot[index] < slotCoordinate[index]:
                changePerStep = -1

            direction = [0,0]
            direction[index] = changePerStep
            self.centerDirection[(bigX,bigY)] = tuple(direction)

            startPos = [7,7]
            startPos[index] += changePerStep
            for i in range(0,12):
                startPos[index] += changePerStep
                if i in (5,6,):
                    continue
                floorPlate = src.items.itemMap["FloorPlate"](bigX*15+startPos[0],bigY*15+startPos[1])
                terrain.addItem(floorPlate)


        for pos in [(6,6),(6,7),(6,8),(7,8),(8,8),(8,7),(8,6),(7,6)]:
            floorPlate = src.items.itemMap["FloorPlate"](bigX*15+pos[0],bigY*15+pos[1])
            terrain.addItem(floorPlate)
        pathingNode = src.items.itemMap["PathingNode"](bigX*15+offsetX,bigY*15+offsetY)
        pathingNode.nodeName = nodeName

        self.pathingNodes[nodeName] = {"coordinate":(bigX,bigY)}
        terrain.addItem(pathingNode)

    def doClearPaths(self,x,y):
        terrain = self.getTerrain()

        minX = 15*x
        minY = 15*y
        maxX = minX+15
        maxY = minY+15
        toRemove = []
        for x in range(minX,maxX):
            for y in range(minY,maxY):
                if (not x%15 == 7) and (not y%15 == 7):
                    continue
                toRemove.extend(terrain.getItemByPosition((x,y)))
        terrain.removeItems(toRemove)

    def getLongInfo(self):
        text = """
roadNetwork:
%s

centerDirection:
%s

pathingNodes:
%s

"""%(self.roadNetwork,self.centerDirection,self.pathingNodes)
        return text


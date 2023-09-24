import src

# NIY: resources are teleported in instead of being carried around
class RoadManager(src.items.Item):
    """
    ingame item for handling roads 
    this means building roads and pathfinding on roads
    """


    type = "RoadManager"

    def __init__(self):
        """
        initialise internal state
        """

        super().__init__(display="RM")

        self.name = "road manager"
        self.runsJobOrders = True

        self.roadNetwork = {}
        self.centerDirection = {}
        self.connections = {}
        self.center = None
        self.pathingNodes = {}
        self.pathsToCenter = {}
        self.pathsFromCenter = {}

    def generatePaths(self, character):
        """
        calculate and store paths on the road network

        Parameters:
            character: the character triggering this action
        """

        for (
            key,
            value,
        ) in self.pathingNodes.items():
            node = tuple(value["coordinate"])
            counter = 0
            backPath = []
            while not node == tuple(self.center):
                counter += 1
                if counter == 100:
                    break
                    raise Exception  # pathfinding loop

                if node == tuple(self.center) or node not in self.centerDirection:
                    break

                backPath.append(list(node))
                direction = self.centerDirection[node]
                node = (node[0] + direction[0], node[1] + direction[1])
            backPath.append(self.center)

            self.pathsFromCenter[tuple(value["coordinate"])] = list(reversed(backPath))
            self.pathsToCenter[tuple(value["coordinate"])] = backPath

    def getJobOrderTriggers(self):
        """
        register handlers for handling job order tasks

        Returns:
            a dict of lists containing the handlers
        """

        result = super().getJobOrderTriggers()
        self.addTriggerToTriggerMap(result, "clear paths", self.jobOrderClearPaths)
        self.addTriggerToTriggerMap(
            result, "add pathing node", self.jobOrderAddPathingNode
        )
        self.addTriggerToTriggerMap(result, "add road", self.doAddRoad)
        self.addTriggerToTriggerMap(result, "print paths", self.doPrintPaths)
        return result

    def getCommandStringForPath(self, start, end):
        """
        get the keystrokes required to walk a path

        Parameters:
            start: the big coordiate to start on
            end: the big coordiate to end on
        """

        start = tuple(start)
        end = tuple(end)

        if not (start == tuple(self.center) or end == tuple(self.center)):
            raise Exception  # invalid path
            return "invalid"

        command = ""

        if start == tuple(self.center):
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
            if lastNode is None:
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

    def doPrintPaths(self, task, context):
        """
        handle the task of printing a path onto a job order

        Parameters:
            task: details about this task
            context: the context for this task
        """

        self.generatePaths(context["character"])
        self.character = context["character"]
        context["jobOrder"].information["pathTo"] = self.getCommandStringForPath(
            tuple(self.center), task["to"]
        )
        context["jobOrder"].information["pathFrom"] = self.getCommandStringForPath(
            task["to"], tuple(self.center)
        )

    def jobOrderAddPathingNode(self, task, context):
        """
        handle the task of adding a pathing node

        Parameters:
            task: details about this task
            context: the context for this task
        """

        if not self.center:
            self.center = [self.container.xPosition, self.container.yPosition]
            self.roadNetwork[tuple(self.center)] = {"type": "roomCenterBlocked"}

        if "offset" not in task:
            task["offset"] = [7, 7]
        self.doAddPathingNode(task)

    def jobOrderClearPaths(self, task, context):
        """
        handle the task of clearing paths on a big coordinate

        Parameters:
            task: details about this task
            context: the context for this task
        """

        self.doClearPaths(task["coordinate"][0], task["coordinate"][1])

    def doAddRoad(self, task, context):
        """
        handle the task of adding a road

        Parameters:
            task: details about this task
            context: the context for this task
        """

        terrain = self.getTerrain()

        bigX = task["coordinate"][0]
        bigY = task["coordinate"][1]

        for pos in [(6, 6), (6, 7), (6, 8), (7, 8), (8, 8), (8, 7), (8, 6), (7, 6)]:
            floorPlate = src.items.itemMap["Paving"]()
            terrain.addItem(floorPlate, (bigX * 15 + pos[0], bigY * 15 + pos[1], 0))
        commandItem = src.items.itemMap["Command"]()
        terrain.addItem(commandItem, (bigX * 15 + 7, bigY * 15 + 6, 0))

        if not self.roadNetwork:
            self.roadNetwork[(self.container.xPosition, self.container.yPosition)] = {
                "type": "centerBlocked"
            }

        neighbours = [
            (bigX + 1, bigY),
            (bigX - 1, bigY),
            (bigX, bigY - 1),
            (bigX, bigY + 1),
        ]
        import random

        random.shuffle(neighbours)

        foundNeighbourSlot = None
        for slot in neighbours:
            if slot in self.roadNetwork:
                foundNeighbourSlot = slot
                break

        if not foundNeighbourSlot:
            return

        slotCoordinate = (bigX, bigY)

        self.roadNetwork[(bigX, bigY)] = {"type": "centerBlocked"}

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

        direction = [0, 0]
        direction[index] = changePerStep
        self.centerDirection[(bigX, bigY)] = list(direction)

        startPos = [7, 7]
        startPos[index] += changePerStep
        for i in range(0, 12):
            startPos[index] += changePerStep
            if i in (
                5,
                6,
            ):
                continue
            floorPlate = src.items.itemMap["Paving"]()
            terrain.addItem(
                floorPlate, (bigX * 15 + startPos[0], bigY * 15 + startPos[1], 0)
            )

    def doAddPathingNode(self, task):
        """
        add a pathing node

        Parameters:
            task: details about the original task
        """

        terrain = self.getTerrain()

        nodeName = task["nodeName"]
        bigX = task["coordinate"][0]
        bigY = task["coordinate"][1]
        offsetX = task["offset"][0]
        offsetY = task["offset"][1]

        if not self.center:
            self.center == [bigX, bigY]
            self.roadNetwork[tuple(self.center)] = {"type": "centerBlocked"}
        else:
            neighbours = [
                (bigX + 1, bigY),
                (bigX - 1, bigY),
                (bigX, bigY - 1),
                (bigX, bigY + 1),
            ]
            import random

            random.shuffle(neighbours)

            foundNeighbourSlot = None
            for slot in neighbours:
                if slot in self.roadNetwork:
                    foundNeighbourSlot = slot
                    break

            if not foundNeighbourSlot:
                return

            slotCoordinate = (bigX, bigY)

            self.roadNetwork[(bigX, bigY)] = {"type": "centerBlocked"}

            index = 0
            if foundNeighbourSlot[0] == slotCoordinate[0]:
                index = 1

            changePerStep = 1
            if foundNeighbourSlot[index] < slotCoordinate[index]:
                changePerStep = -1

        pathingNode = src.items.itemMap["PathingNode"]()
        pathingNode.nodeName = nodeName

        self.pathingNodes[nodeName] = {"coordinate": [bigX, bigY]}
        terrain.addItem(pathingNode, (bigX * 15 + offsetX, bigY * 15 + offsetY, 0))

    def doClearPaths(self, x, y):
        """
        clear paths on a big coordiante

        Parameters:
            x: the x part of the coordinate
            y: the y part of the coordinate
        """

        terrain = self.getTerrain()

        minX = 15 * x
        minY = 15 * y
        maxX = minX + 15
        maxY = minY + 15
        toRemove = []
        for x in range(minX, maxX):
            for y in range(minY, maxY):
                if (not x % 15 == 7) and (not y % 15 == 7):
                    continue
                toRemove.extend(terrain.getItemByPosition((x, y, 0)))
        terrain.removeItems(toRemove)

    def getLongInfo(self):
        """
        return a longer than normal description text
        """

        text = super().getLongInfo()
        text += """
roadNetwork:
%s

centerDirection:
%s

pathingNodes:
%s

center:
%s

pathsFromCenter:
%s

pathsToCenter:
%s

connections:
%s

""" % (
            self.roadNetwork,
            self.centerDirection,
            self.pathingNodes,
            self.center,
            self.pathsFromCenter,
            self.pathsToCenter,
            self.connections,
        )
        return text


src.items.addType(RoadManager)

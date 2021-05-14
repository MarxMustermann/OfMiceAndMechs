import src

"""
gomode item for terraforming and things
"""


class RoadManager(src.items.Item):
    type = "RoadManager"

    """
    call superclass constructor with modified parameters
    """

    def __init__(self):
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

        self.attributesToStore.extend(
            [
                "center",
                "connections",
                "pathingNodes",
            ]
        )

        self.tupleDictsToStore.extend(
            [
                "roadNetwork",
                "centerDirection",
                "pathsToCenter",
                "pathsFromCenter",
                "pathingNodes",
            ]
        )

    def generatePaths(self, character):
        text = ""
        for (
            key,
            value,
        ) in self.pathingNodes.items():
            text += "%s: %s  => center\n" % (
                key,
                value["coordinate"],
            )
            text += "  "
            node = tuple(value["coordinate"])
            counter = 0
            backPath = []
            while not node == tuple(self.center):
                counter += 1
                if counter == 100:
                    break
                    raise Exception  # pathfinding loop

                if node == tuple(self.center) or not node in self.centerDirection:
                    break

                backPath.append(list(node))
                direction = self.centerDirection[node]
                node = (node[0] + direction[0], node[1] + direction[1])
            backPath.append(self.center)

            self.pathsFromCenter[tuple(value["coordinate"])] = list(reversed(backPath))
            self.pathsToCenter[tuple(value["coordinate"])] = backPath

            text += "  %s\n" % (list(reversed(backPath)),)
            text += "  %s\n" % (backPath,)

            commandItem = src.items.itemMap["Command"]()
            command = ""
            lastNode = None
            for node in self.pathsToCenter[tuple(value["coordinate"])]:
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
            commandItem.setPayload(list(command))

            terrain = self.getTerrain()
            terrain.addItem(
                commandItem,
                (value["coordinate"][0] * 15 + 7, value["coordinate"][1] * 15 + 6, 0),
            )

        self.submenue = src.interaction.OneKeystrokeMenu(text)
        character.macroState["submenue"] = self.submenue

    def getJobOrderTriggers(self):
        result = super().getJobOrderTriggers()
        self.addTriggerToTriggerMap(result, "clear paths", self.jobOrderClearPaths)
        self.addTriggerToTriggerMap(
            result, "add pathing node", self.jobOrderAddPathingNode
        )
        self.addTriggerToTriggerMap(result, "add road", self.doAddRoad)
        self.addTriggerToTriggerMap(result, "print paths", self.doPrintPaths)
        return result

    def getCommandStringForPath(self, start, end):
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
        self.generatePaths(context["character"])
        self.character = context["character"]
        context["jobOrder"].information["pathTo"] = self.getCommandStringForPath(
            tuple(self.center), task["to"]
        )
        context["jobOrder"].information["pathFrom"] = self.getCommandStringForPath(
            task["to"], tuple(self.center)
        )

    def jobOrderAddPathingNode(self, task, context):
        if not self.center:
            self.center = [self.container.xPosition, self.container.yPosition]
            self.roadNetwork[tuple(self.center)] = {"type": "roomCenterBlocked"}

        if not "offset" in task:
            task["offset"] = [7, 7]
        self.doAddPathingNode(task)

    def jobOrderClearPaths(self, task, context):
        self.doClearPaths(task["coordinate"][0], task["coordinate"][1])

    def doAddRoad(self, task, context):
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
        text = """
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

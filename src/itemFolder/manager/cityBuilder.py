import random

import src


class CityBuilder(src.items.Item):
    """
    a ingame item to build and extend cities
    is a representation of a city and holds the coresponding information
    takes tasks and delegates tasks to other manager
    """


    type = "CityBuilder"

    def __init__(self, name="CityBuilder", noId=False):
        """
        set up the initial state
        """

        super().__init__(display="CC", name=name)
        self.commands = {}
        self.tasks = []
        self.internalRooms = []
        self.scrapFields = []
        self.reservedPlots = []
        self.usedPlots = []
        self.stockPiles = []
        self.roadTiles = []
        self.unusedRoadTiles = []
        self.unusedTiles = []
        self.unfinishedRoadTiles = []
        self.plotPool = []
        self.stuck = False
        self.stuckReason = None
        self.runningTasks = []

        self.resources = {"TypedStockpileManager": 4, "Paving": 120}
        self.resources = {}

        # config options
        self.numReservedPathPlots = 5
        self.numBufferPlots = 3
        self.pathsOnAxis = False
        self.idleExtend = False
        self.hasMaintenance = True
        self.runsJobOrders = True

        self.error = {}

        self.applyOptions.extend(
                [
                    ("showMap", "show map"),
                    ("addResource", "add resource"),
                    ("clearTask", "clear one task"),
                    ("clearTasks", "clear tasks"),
                    ("clearError", "clear error"),
                ]
            )
        self.applyMap = {
            "showMap": self.showMap,
            "addResource": self.addResource,
            "clearTask": self.clearTask,
            "clearTasks": self.clearTasks,
            "clearError": self.clearError,
        }

    def apply(self,character):
        if not character.rank < 4:
            character.addMessage("you need to have rank 3 to use this machine")
            return
        super().apply()

    def getLongINfo(self):
        return f"plan your city with this item. {self.autoExtensionThreashold}"

    def addTasksToLocalRoom(self, tasks, character):
        """
        delegate tasks to the room the item is in

        Parameters:
            tasks: the tasks to delegate
            character: the character that can be used to carry the tasks to the room
        """

        jobOrder = src.items.itemMap["JobOrder"]()
        jobOrder.tasks = list(
            reversed(
                [
                    {
                        "task": "go to room manager",
                        "command": self.commands["go to room manager"],
                    },
                    {
                        "task": "insert job order",
                        "command": "scj",
                    },
                    {
                        "task": "add Tasks",
                        "command": None,
                        "tasks": list(reversed(tasks)),
                    },
                    {
                        "task": "return from room manager",
                        "command": self.commands["return from room manager"],
                    },
                ]
            )
        )
        jobOrder.taskName = "relay task to room"

        character.addMessage("running job order to add local room task")
        character.addJobOrder(jobOrder)

    def costGuard(self, cost, character):
        """
        check and remove required ressources

        Parameters:
            cost: the ressources needed
            character: the character tyig to do something
        """

        for (resourceType, amount) in cost.items():
            availableAmount = self.resources.get(resourceType)

            if availableAmount is None:
                character.addMessage(f"need resource {resourceType}")
                return False
            elif availableAmount < amount:
                character.addMessage(
                    f"need {amount - availableAmount} more {resourceType}"
                )
                return False

        for (resourceType, amount) in cost.items():
            self.resources[resourceType] -= amount
            return True
        return None

    def addResource(self, character):
        """
        handle a character trying to add ressources
        by trying to add the ressources from the characters inventory

        Parameters:
            character: the character trying to use the item
        """

        foundItems = []
        for item in character.inventory:
            foundItems.append(item)

            if item.type not in self.resources:
                self.resources[item.type] = 0
            self.resources[item.type] += 1

        for item in foundItems:
            character.inventory.remove(item)

    def clearTask(self, character):
        """
        handle a character trying to clear a task this items
        by clearing the most recent task

        Parameters:
            character: the character trying to use the item
        """

        if self.tasks:
            task = self.tasks.pop()
            character.addMessage("cleared task %s"%(task["task"]))
        else:
            character.addMessage("no task to clear")

    def clearTasks(self, character):
        """
        handle a character trying to clear this items tasks
        by clearing the tasks

        Parameters:
            character: the character trying to use the item
        """

        self.tasks = []
        self.runningTasks = []

    def clearError(self, character):
        """
        handle a character trying to clear errors
        by clearing the errors

        Parameters:
            character: the character trying to use the item
        """

        self.error = {}

    def doRegisterResult(self, task, context):
        """
        handle processing a report on something
        used to check if job orders were completed successful

        Parameters:
            tasks: the tasks to delegate
            character: the character that can be used to carry the tasks to the room
        """

        character = context["character"]

        error = context["jobOrder"].error
        if error:
            context["character"].addMessage("got error")
            if context["jobOrder"].error["type"] == "item not found":
                task = self.runningTasks.pop()
                self.tasks.append(task)
                self.addTasksToLocalRoom(
                    [
                        {"task": "add item", "type": error["itemType"]},
                    ],
                    context["character"],
                )
                context["character"].addMessage("handled error")
            else:
                self.registerError(error)
        else:
            character.addMessage("success")
            task = self.runningTasks[-1]
            if task["task"] == "build roads":
                character.addMessage("handle success")
                plot = context["jobOrder"].information["plot"]
                if plot in self.unfinishedRoadTiles:
                    self.unfinishedRoadTiles.remove(plot)
                    if not (
                        plot[0] == self.container.xPosition
                        and plot[1] == self.container.yPosition
                    ):
                        self.roadTiles.append(plot)
                        self.unusedRoadTiles.append(plot)

        self.runningTasks = []

    def registerError(self, error):
        """
        go into an error state

        Parameters:
            error: the error to register
        """

        task = self.runningTasks.pop()
        self.tasks.append(task)
        self.error = error

    def doIdleExtend(self, character):
        """
        try to expand the city due to having no other task

        Parameters:
            character: the character available to do the task
        """

        if self.idleExtend and len(self.plotPool) < self.numReservedPathPlots + self.numBufferPlots:
            self.tasks.append({"task": "expand"})
            character.addMessage("idle extend")
            return
        character.addMessage("no tasks left")

    def getTaskResolvers(self):
        """
        get list of resolvers

        Returns:
            a dictionary mapping resovers to tasks
        """

        taskDict = {}
        self.addTriggerToTriggerMap(taskDict, "expand", self.doExpand)
        self.addTriggerToTriggerMap(taskDict, "build roads", self.doBuildRoads)
        self.addTriggerToTriggerMap(
            taskDict, "set up basic production", self.doSetUpBasicProduction
        )
        self.addTriggerToTriggerMap(
            taskDict, "prepare scrap field", self.doPrepareScrapField
        )  # should be somewhere else?
        self.addTriggerToTriggerMap(taskDict, "extend storage", self.doExtendStorage)
        self.addTriggerToTriggerMap(
            taskDict, "set up internal storage", self.doSetUpInternalStorage
        )
        self.addTriggerToTriggerMap(taskDict, "build room", self.doSetUpRoom)
        self.addTriggerToTriggerMap(taskDict, "build mine", self.doSetUpMine)
        self.addTriggerToTriggerMap(taskDict, "build factory", self.doSetUpFactory)
        return taskDict

    def doSetUpRoom(self, context):
        """
        handle a task to set up a room

        Parameters:
            context: the context for this task
        """

        character = context["character"]
        task = context["task"]
        plot = task["plot"]

        self.useJoborderRelayToLocalRoom(
            character,
            [
                {"task": "set up", "type": "room", "coordinate": plot, "command": None},
            ],
            "ArchitectArtwork",
            information={"plot": plot},
        )
        self.plotPool.remove(tuple(plot))
        self.usedPlots.append(tuple(plot))

    def doSetUpInternalStorage(self, context):
        """
        handle a task to set up a system for internal item storage

        Parameters:
            context: the context for this task
        """

        self.tasks.append({"task": "extend storage"})

    def doExtendStorage(self, context):
        """
        handle a task to extend to storage space of the internal item storage

        Parameters:
            context: the context for this task
        """

        character = context["character"]
        task = context["task"]

        if "stockPileCoordinate" not in task:
            if not self.unusedRoadTiles:
                self.tasks.append(task)
                newTask = {"task": "build roads"}
                self.tasks.append(newTask)
                newTask = {"task": "expand"}
                self.tasks.append(newTask)
                self.runningTasks = []
                return

            # set the coordinate to build on
            if not task.get("coordinate"):
                plot = random.choice(self.unusedRoadTiles)

                # check if the selected plot was reserved
                if "reservedPlots" in task and list(plot) in task["reservedPlots"]:

                    # increment failure couner to not get stuck
                    if "failCounter" not in task:
                        task["failCounter"] = 1
                    else:
                        task["failCounter"] += 1

                    # retry task
                    self.runningTasks = []
                    self.tasks.append(task)

                    # expand the roads when stuck
                    if task["failCounter"] > 4:
                        newTask = {"task": "expand"}
                        self.tasks.append(newTask)
                        task["failCounter"] = 1

                    # abort
                    return
                task["stockPileCoordinate"] = plot
            else:
                task["stockPileCoordinate"] = task["coordinate"]
                self.unusedRoadTiles.remove(tuple(task["coordinate"]))
            self.usedPlots.append(task["stockPileCoordinate"])
            self.stockPiles.append(task["stockPileCoordinate"])
            self.tasks.append(task)
            self.runningTasks = []
            return

        task["stockPileName"] = "storage_{}_{}".format(
            task["stockPileCoordinate"][0],
            task["stockPileCoordinate"][1],
        )

        if not task.get("stockPileType"):
            task["stockPileType"] = "TypedStockpileManager"

        if not task.get("payed"):
            if not self.costGuard(
                {task["stockPileType"]: 1}, character
            ):  # actual costs happen here
                self.abortTask()
                return
            task["payed"] = True

        setupTask = {
            "task": "set up",
            "type": "stockPile",
            "name": task["stockPileName"],
            "coordinate": task["stockPileCoordinate"],
            "command": None,
        }

        setupTask["StockpileType"] = task["stockPileType"]
        if task["stockPileType"] == "UniformStockpileManager":
            setupTask["ItemType"] = task["itemType"]

        tasks = [
            setupTask,
        ]

        stockPileFunction = task.get("stockPileFunction")
        newTask = {
            "task": "connect stockpile",
            "type": "add to storage",
            "stockPile": task["stockPileName"],
            "stockPileCoordinate": task["stockPileCoordinate"],
            "command": None,
        }
        if stockPileFunction:
            newTask["function"] = stockPileFunction

        tasks.append(newTask)
        self.useJoborderRelayToLocalRoom(character, tasks, "ArchitectArtwork")

    def doPrepareScrapField(self, context):
        """
        handle a task to extend to storage space of the internal item storage

        Parameters:
            context: the context for this task
        """

        character = context["character"]
        self.useJoborderRelayToLocalRoom(
            character,
            [
                {
                    "task": "clear paths",
                    "coordinate": task["coordinate"],
                    "command": None,
                },
            ],
            "RoadManager",
        )

    def doSetUpBasicProduction(self, context):
        """
        handle a task to add basic production capabilities

        Parameters:
            context: the context for this task
        """

        self.addTasksToLocalRoom(
            [
                {"task": "add machine", "type": "FloorPlate"},
                {"task": "add machine", "type": "ScrapCompactor"},
                {"task": "add item", "type": "ProductionManager"},
            ]
        )

    def doBuildRoads(self, context):
        """
        handle a task to extend to storage space of the internal item storage

        Parameters:
            context: the context for this task
        """

        character = context["character"]
        task = context["task"]
        if self.unfinishedRoadTiles:
            plot = self.unfinishedRoadTiles[-1]
            if plot == (self.container.xPosition, self.container.yPosition):
                self.unfinishedRoadTiles.pop()
                self.abortTask()
                return

            terrain = self.getTerrain()
            for x in range(plot[0] * 15, plot[0] * 15 + 15):
                for y in range(plot[1] * 15, plot[1] * 15 + 15):
                    items = terrain.getItemByPosition((x, y, 0))
                    if items:
                        if (
                            x % 15 == 7
                            and y % 15 == 7
                            and len(items) == 1
                            and items[0].type == "MarkerBean"
                        ):
                            continue
                        character.addMessage(
                            f"building site {plot} blocked on {x}/{y}"
                        )
                        self.abortTask()
                        return

            if not task.get("payed"):
                if not self.costGuard(
                    {"Paving": 30}, character
                ):  # actual costs happen here
                    self.abortTask()
                    return
                task["payed"] = True

            self.useJoborderRelayToLocalRoom(
                character,
                [
                    {
                        "task": "set up",
                        "type": "road",
                        "coordinate": plot,
                        "command": None,
                    },
                ],
                "ArchitectArtwork",
                information={"plot": plot},
            )
        else:
            character.addMessage("no road tile found to build")
            self.runningTasks = []

    def abortTask(self):
        """
        abort the currently running task
        """
        self.tasks.append(self.runningTasks.pop())

    def doExpand(self, context):
        """
        handle the task of expandng the city

        Parameters:
            context: the context for this task
        """

        if not self.plotPool:
            return

        task = context["task"]
        character = context["character"]

        if "from" not in task:
            plot = random.choice(self.plotPool)
        else:
            plot = tuple(task["from"])

        if plot not in self.plotPool:
            self.abortTask()
            return

        self.expandFromPlot(plot)
        newTask = {"task": "build roads"}
        self.tasks.append(newTask)
        self.runningTasks = []
        return

    def doMaintenance(self, character):
        """
        handle a character trying to do a maintenance task

        Parameters:
            character: the character trying to do the maintenance task
        """

        if (
            "go to room manager" not in self.commands
            and "return from room manager" in self.commands
        ):
            character.addMessage("no room manager")
            return

        if self.error:
            character.addMessage("Error while running task")
            return

        if self.runningTasks:
            character.addMessage("item blocked tasks running")
            return

        if not self.tasks:
            self.doIdleExtend(character)
            return

        if not self.usedPlots:
            plot = (self.container.xPosition, self.container.yPosition)
            self.plotPool.append(plot)

            self.expandFromPlot(plot)

        task = self.tasks.pop()
        self.runningTasks.append(task)

        resolverMap = self.getTaskResolvers()
        if task["task"] in resolverMap:
            for taskResolver in resolverMap[task["task"]]:
                taskResolver({"character": character, "task": task})

    def doSetUpFactory(self, context):
        """
        handle the task of building a factory

        Parameters:
            context: the context for this task
        """

        character = context["character"]
        task = context["task"]

        if not task.get("basePlot"):
            random.shuffle(self.plotPool)
            plot = self.plotPool.pop()

        self.useJoborderRelayToLocalRoom(
            character,
            [
                {"task": "set up", "type": "factory", "coordinate": plot},
            ],
            "ArchitectArtwork",
        )

    def doSetUpMine(self, context):
        """
        handle the task of setting up a mine

        Parameters:
            context: the context for this task
        """

        character = context["character"]
        task = context["task"]

        if not self.scrapFields:
            self.tasks.append(task)
            newTask = {"task": "expand"}
            self.tasks.append(newTask)
            self.runningTasks = []
            return
        if not task.get("scrapField"):
            task["scrapField"] = list(random.choice(self.scrapFields))

        if not task.get("expanded storage"):
            self.tasks.append(task)
            newTask = {"task": "extend storage"}
            if task.get("reservedPlots"):
                newTask["reservedPlots"] = task["reservedPlots"]
            self.tasks.append(newTask)
            self.runningTasks = []
            task["expanded storage"] = True
            return

        if not task.get("stockPileCoordinate"):
            self.runningTasks = []
            directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            random.shuffle(directions)
            neighbourRoad = None
            neighbourPlot = None
            neighbourUndiscovered = None
            for direction in directions:
                position = (
                    task["scrapField"][0][0] + direction[0],
                    task["scrapField"][0][1] + direction[1],
                )
                if "reservedPlots" in task and list(position) in task["reservedPlots"]:
                    continue
                if position in self.unusedRoadTiles:
                    neighbourRoad = position
                    continue
                if position in self.plotPool:
                    neighbourPlot = position
                    continue
                if position not in self.usedPlots and position not in self.stockPiles:
                    neighbourUndiscovered = position
                    continue

            if neighbourRoad:
                self.tasks.append(task)
                task["stockPileCoordinate"] = neighbourRoad
                self.unusedRoadTiles.remove(neighbourRoad)
                character.addMessage("expand done")
                task["undiscoveredCounter"] = 0
                task["scrapRetryCounter"] = 0
                return
            elif neighbourPlot:
                self.tasks.append(task)
                newTask = {"task": "expand", "from": neighbourPlot}
                self.tasks.append(newTask)
                character.addMessage("expand plot")
                return
            elif neighbourUndiscovered:
                if "undiscoveredCounter" not in task:
                    task["undiscoveredCounter"] = 0
                task["undiscoveredCounter"] += 1
                if task["undiscoveredCounter"] > 5:
                    if "scrapRetryCounter" not in task:
                        task["scrapRetryCounter"] = 0

                    if task["scrapRetryCounter"] > 5:
                        return

                    self.tasks.append(task)
                    del task["scrapField"]
                    task["undiscoveredCounter"] = 0
                    return

                self.tasks.append(task)
                newTask = {"task": "expand", "target": neighbourPlot}
                self.tasks.append(newTask)
                character.addMessage("expand undiscovered")
                return
            else:
                character.addMessage("no way to place")
                return

        if not task.get("oreProcessingCoordinate"):
            self.runningTasks = []
            directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            random.shuffle(directions)
            neighbourRoad = None
            neighbourPlot = None
            neighbourUndiscovered = None
            for direction in directions:
                position = (
                    task["stockPileCoordinate"][0] + direction[0],
                    task["stockPileCoordinate"][1] + direction[1],
                )
                if "reservedPlots" in task and list(position) in task["reservedPlots"]:
                    continue
                if position in self.unusedRoadTiles:
                    neighbourRoad = position
                    continue
                if position in self.plotPool:
                    neighbourPlot = position
                    continue
                if position not in self.usedPlots and position not in self.stockPiles:
                    neighbourUndiscovered = position
                    continue

            if neighbourRoad:
                self.tasks.append(task)
                task["oreProcessingCoordinate"] = neighbourRoad
                self.unusedRoadTiles.remove(neighbourRoad)
                character.addMessage("expand done")
                return
            elif neighbourPlot:
                self.tasks.append(task)
                newTask = {"task": "expand", "from": neighbourPlot}
                self.tasks.append(newTask)
                character.addMessage("expand plot")
                return
            elif neighbourUndiscovered:
                if "undiscoveredCounter" not in task:
                    task["undiscoveredCounter"] = 0
                task["undiscoveredCounter"] += 1
                if task["undiscoveredCounter"] > 5:
                    if "scrapRetryCounter" not in task:
                        task["scrapRetryCounter"] = 0

                    if task["scrapRetryCounter"] > 5:
                        return

                    self.tasks.append(task)
                    del task["scrapField"]
                    task["undiscoveredCounter"] = 0
                    return

                self.tasks.append(task)
                newTask = {"task": "expand", "target": neighbourPlot}
                self.tasks.append(newTask)
                character.addMessage("expand undiscovered")
                return
            else:
                character.addMessage("no way to place")
                return

        if not task.get("metalBarStorageCoordinate"):
            self.runningTasks = []
            directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            random.shuffle(directions)
            neighbourRoad = None
            neighbourPlot = None
            neighbourUndiscovered = None
            for direction in directions:
                position = (
                    task["oreProcessingCoordinate"][0] + direction[0],
                    task["oreProcessingCoordinate"][1] + direction[1],
                )
                if "reservedPlots" in task and list(position) in task["reservedPlots"]:
                    continue
                if position in self.unusedRoadTiles:
                    neighbourRoad = position
                    continue
                if position in self.plotPool:
                    neighbourPlot = position
                    continue
                if position not in self.usedPlots and position not in self.stockPiles:
                    neighbourUndiscovered = position
                    continue

            if neighbourRoad:
                self.tasks.append(task)
                task["metalBarStorageCoordinate"] = neighbourRoad
                task["metalBarStorageName"] = "bardropoff {}".format(
                    task["metalBarStorageCoordinate"],
                )
                self.unusedRoadTiles.remove(neighbourRoad)
                character.addMessage("expand done")
                return
            elif neighbourPlot:
                self.tasks.append(task)
                newTask = {"task": "expand", "from": neighbourPlot}
                self.tasks.append(newTask)
                character.addMessage("expand plot")
                return
            elif neighbourUndiscovered:
                if "undiscoveredCounter" not in task:
                    task["undiscoveredCounter"] = 0
                task["undiscoveredCounter"] += 1
                if task["undiscoveredCounter"] > 5:
                    if "scrapRetryCounter" not in task:
                        task["scrapRetryCounter"] = 0

                    if task["scrapRetryCounter"] > 5:
                        return

                    self.tasks.append(task)
                    del task["scrapField"]
                    task["undiscoveredCounter"] = 0
                    return

                self.tasks.append(task)
                newTask = {"task": "expand", "target": neighbourPlot}
                self.tasks.append(newTask)
                character.addMessage("expand undiscovered")
                return
            else:
                character.addMessage("no way to place")
                return

        if not task.get("didBasicSetup"):
            task["stockPileName"] = "miningStockPile_{}_{}".format(
                task["stockPileCoordinate"][0],
                task["stockPileCoordinate"][1],
            )

            if "metalBarStorageName" not in task:
                task["metalBarStorageName"] = "bardropoff {}".format(
                    task["metalBarStorageCoordinate"],
                )

            self.useJoborderRelayToLocalRoom(
                character,
                [
                    {
                        "task": "set up",
                        "type": "stockPile",
                        "name": task["metalBarStorageName"],
                        "coordinate": task["metalBarStorageCoordinate"],
                        "command": None,
                        "StockpileType": "UniformStockpileManager",
                        "ItemType": "MetalBars",
                    },
                    {
                        "task": "connect stockpile",
                        "type": "add to storage",
                        "function": "source",
                        "stockPileCoordinate": task["metalBarStorageCoordinate"],
                        "stockPile": task["metalBarStorageName"],
                    },
                    {
                        "task": "set up",
                        "type": "oreProcessing",
                        "coordinate": task["oreProcessingCoordinate"],
                        "command": None,
                    },
                    {
                        "task": "set up",
                        "type": "stockPile",
                        "name": task["stockPileName"],
                        "coordinate": task["stockPileCoordinate"],
                        "command": None,
                        "StockpileType": "UniformStockpileManager",
                        "ItemType": "Scrap",
                    },
                    {
                        "task": "set up",
                        "type": "mine",
                        "stockPile": task["stockPileName"],
                        "stocKPileCoordinate": task["stockPileCoordinate"],
                        "scrapField": task["scrapField"],
                        "command": None,
                    },
                ],
                "ArchitectArtwork",
            )
            task["didBasicSetup"] = True
            self.tasks.append(task)
            return

        if not task.get("didExtendStorage"):
            newTask = {"task": "extend storage"}
            self.tasks.append(task)
            self.tasks.append(newTask)
            self.runningTasks = []
            task["didExtendStorage"] = True
            return

        self.useJoborderRelayToLocalRoom(
            character,
            [
                {
                    "task": "set up",
                    "setupInfo": {
                        "miningSpot": task["scrapField"],
                        "scrapStockPileName": task["stockPileName"],
                        "scrapStockPileCoordinate": task["stockPileCoordinate"],
                        "metalBarStockPileName": task["metalBarStorageName"],
                        "metalBarStockPileCoordinate": task[
                            "metalBarStorageCoordinate"
                        ],
                        "oreProcessing": task["oreProcessingCoordinate"],
                    },
                }
            ],
            "MiningManager",
        )

    def expandFromPlot(self, plot):
        """
        expand the city by converting a plot into a road

        Parameters:
            plot: the plot to convert
        """

        self.usedPlots.append(plot)
        self.plotPool.remove(plot)

        plotCandiates = [
            (plot[0] - 1, plot[1]),
            (plot[0] + 1, plot[1]),
            (plot[0], plot[1] - 1),
            (plot[0], plot[1] + 1),
        ]

        self.getTerrain().addItem(
            src.items.itemMap["MarkerBean"](), (plot[0] * 15 + 7, plot[1] * 15 + 7, 0)
        )
        self.unfinishedRoadTiles.append(plot)

        axisPlots = []
        for candidate in plotCandiates:
            if candidate not in self.usedPlots and candidate not in self.plotPool:
                if candidate[0] in (0, 14) or candidate[1] in (0, 14):
                    continue

                numScrap = 0
                for x in range(candidate[0] * 15 + 1, candidate[0] * 15 + 14):
                    for y in range(candidate[1] * 15 + 1, candidate[1] * 15 + 14):
                        for item in self.getTerrain().getItemByPosition((x, y, 0)):
                            if item.type == "Scrap":
                                numScrap += item.amount

                if numScrap > 1000:
                    self.scrapFields.append([list(candidate), numScrap])
                    self.usedPlots.append(candidate)
                    continue

                self.plotPool.append(candidate)
                if self.pathsOnAxis and 7 in (candidate):
                    axisPlots.append(candidate)

        if self.pathsOnAxis:
            for plot in axisPlots:
                if plot in self.plotPool:
                    self.expandFromPlot(plot)

    def showMap(self, character):
        """
        handle a character trying to view the map of the city
        (the map shows what this item thinks is true not actual truth)

        Parameters:
            character: the character to show the map to
        """

        # render empty map
        mapContent = []
        for x in range(15):
            mapContent.append([])
            for y in range(15):
                if x not in (0, 14) and y not in (0, 14):
                    char = "  "
                elif x != 7 and y != 7:
                    char = "##"
                else:
                    char = "  "
                mapContent[x].append(char)

        functionMap = {}

        # add known things for rendering
        for plot in self.plotPool:
            mapContent[plot[1]][plot[0]] = "__"
            if plot not in functionMap:
                functionMap[plot] = {}

            functionMap[plot]["e"] = {
                "function": {
                    "container":self,
                    "method":"expandFromMap",
                    "params":{"character":character},
                },
                "description":"expand city from that point",
            }
            functionMap[plot]["R"] = {
                "function": {
                    "container":self,
                    "method":"reservePlotFromMap",
                    "params":{"character":character},
                },
                "description":"reserve plot",
            }
            functionMap[plot]["r"] = {
                "function": {
                    "container":self,
                    "method":"addRoomFromMap",
                    "params":{"character":character},
                },
                "description":"add room",
            }
            functionMap[plot]["f"] = {
                "function": {
                    "container":self,
                    "method":"buildFactoryFromRoom",
                    "params":{"character":character},
                },
                "description":"add factory",
            }
        for plot in self.usedPlots:
            mapContent[plot[1]][plot[0]] = "xx"
        for plot in self.stockPiles:
            mapContent[plot[1]][plot[0]] = "pp"
        for scrapField in self.scrapFields:

            plot = tuple(scrapField[0])
            mapContent[plot[1]][plot[0]] = "*#"

            if plot not in functionMap:
                functionMap[plot] = {}

            functionMap[plot]["m"] = {
                "function": {
                    "container":self,
                    "method":"buildMineFromRoom",
                    "params":{"character":character,"amount":scrapField[1]},
                },
                "description":"build mine from room",
            }

        for plot in self.unfinishedRoadTiles:
            mapContent[plot[1]][plot[0]] = ".."
        for plot in self.roadTiles:
            if plot in self.unusedRoadTiles:
                mapContent[plot[1]][plot[0]] = "::"

                if plot not in functionMap:
                    functionMap[plot] = {}

                functionMap[plot]["u"] = {
                    "function": {
                        "container":self,
                        "method":"markUsedFromMap",
                        "params":{"character":character},
                    },
                    "description":"mark as used",
                }
                functionMap[plot]["S"] = {
                    "function": {
                        "container":self,
                        "method":"expandStorageFromMap",
                        "params":{"character":character},
                    },
                    "description":"set up internal storage space",
                }
            else:
                mapContent[plot[1]][plot[0]] = ";;"

                if plot not in functionMap:
                    functionMap[plot] = {}

                functionMap[plot]["u"] = {
                    "function": {
                        "container":self,
                        "method":"markUnusedFromMap",
                        "params":{"character":character},
                    },
                    "description":"mark as unused",
                }

        for plot in self.reservedPlots:
            mapContent[plot[1]][plot[0]] = "RR"

            if plot not in functionMap:
                functionMap[plot] = {}

            functionMap[plot]["R"] = {
                "function": {
                    "container":self,
                    "method":"unreservePlotFromMap",
                    "params":{"character":character},
                },
                "description":"remove reservation",
            }

        plot = (self.container.xPosition,self.container.yPosition)
        mapContent[plot[1]][plot[0]] = "CB"

        if not self.roadTiles and not self.tasks:
            if plot not in functionMap:
                functionMap[plot] = {}
            functionMap[plot]["c"] = {
                "function": {
                    "container":self,
                    "method":"startCityBuilding",
                "params":{"character":character},
                },
                "description":"start city building",
            }

        extraText = "\n\n"
        for task in reversed(self.tasks):
            extraText += f"{task}\n"

        self.submenue = src.menuFolder.MapMenu.MapMenu(mapContent=mapContent,functionMap=functionMap, extraText=extraText)
        character.macroState["submenue"] = self.submenue

    def startCityBuilding(self,character):
        """
        handle a character requesting to start building the city
        by scheduling a task to expand

        Parameters:
            character: the character using the item
        """

        newTask = {"task":"expand"}
        self.tasks.append(newTask)

    def buildFactoryFromRoom(self, params):
        """
        handle a character having selected building a factory
        by adding a task to the items task list

        Parameters:
            params: parameters given from the interaction menu
        """

        newTask = {"task": "build factory"}
        self.tasks.append(newTask)

    def buildMineFromRoom(self, params):
        """
        handle a character having selected building a mine
        by fetching more configuration info from the character
        and adding a task to the items task list

        Parameters:
            params: parameters given from the interaction menu
        """

        character = params["character"]

        if not params.get("scrapField"):
            params["scrapField"] = [params["coordinate"],params["amount"]]

        if "scrapStorageCoordinate" not in params:
            basePlot = params["coordinate"]

            options = [
                (None, "auto"),
                ]

            if basePlot[1] > 0:
                options.append(([basePlot[0],basePlot[1]-1], "north"))
                options.append(([basePlot[0],basePlot[1]+1], "south"))
                options.append(([basePlot[0]+1,basePlot[1]], "east"))
                options.append(([basePlot[0]-1,basePlot[1]], "west"))

            submenu = src.menuFolder.SelectionMenu.SelectionMenu(
                "Select scrapstockpile position", options,
                targetParamName="scrapStorageCoordinate",
            )
            character.macroState["submenue"] = submenu
            character.macroState["submenue"].followUp = {
                    "container": self,
                    "method": "buildMineFromRoom",
                    "params": params
            }
            return

        if "processingCoordinate" not in params and params["scrapStorageCoordinate"]:
            basePlot = params["scrapStorageCoordinate"]

            options = [
                (None, "auto"),
                ]

            if basePlot[1] > 0:
                options.append(([basePlot[0],basePlot[1]-1], "north"))
                options.append(([basePlot[0],basePlot[1]+1], "south"))
                options.append(([basePlot[0]+1,basePlot[1]], "east"))
                options.append(([basePlot[0]-1,basePlot[1]], "west"))

            submenu = src.menuFolder.SelectionMenu.SelectionMenu(
                "Select processing position", options,
                targetParamName="processingCoordinate",
            )
            character.macroState["submenue"] = submenu
            character.macroState["submenue"].followUp = {
                    "container": self,
                    "method": "buildMineFromRoom",
                    "params": params
            }
            return

        if "barStorageCoordinate" not in params and params["processingCoordinate"]:
            basePlot = params["processingCoordinate"]

            options = [
                (None, "auto"),
                ]

            if basePlot[1] > 0:
                options.append(([basePlot[0],basePlot[1]-1], "north"))
                options.append(([basePlot[0],basePlot[1]+1], "south"))
                options.append(([basePlot[0]+1,basePlot[1]], "east"))
                options.append(([basePlot[0]-1,basePlot[1]], "west"))

            submenu = src.menuFolder.SelectionMenu.SelectionMenu(
                "Select bar storage position", options,
                targetParamName="barStorageCoordinate",
            )
            character.macroState["submenue"] = submenu
            character.macroState["submenue"].followUp = {
                    "container": self,
                    "method": "buildMineFromRoom",
                    "params": params
            }
            return

        newTask = {
            "task": "build mine",
            "scrapField": list(params["scrapField"]),
            "reservedPlots": [list(params["scrapField"][0])],
        }

        if "scrapStorageCoordinate" in params and params["scrapStorageCoordinate"]:
            newTask["reservedPlots"].append(params["scrapStorageCoordinate"])
            newTask["stockPileCoordinate"] = params["scrapStorageCoordinate"]
        if "processingCoordinate" in params and params["processingCoordinate"]:
            newTask["reservedPlots"].append(params["processingCoordinate"])
            newTask["oreProcessingCoordinate"] = params["processingCoordinate"]
        if "barStorageCoordinate" in params and params["barStorageCoordinate"]:
            newTask["reservedPlots"].append(params["barStorageCoordinate"])
            newTask["metalBarStorageCoordinate"] = params["barStorageCoordinate"]
        self.tasks.append(newTask)

    def addRoomFromMap(self,params):
        """
        handle a character having selected building a room
        and adding a task to the items task list

        Parameters:
            params: parameters given from the interaction menu
        """

        character = params["character"]
        plot = params["coordinate"]

        if not plot:
            character.addMessage("no selection")
            return

        if plot not in self.plotPool:
            character.addMessage("not in plot pool")
            return

        newTask = {"task": "build room", "plot": list(plot)}
        self.tasks.append(newTask)


    def expandStorageFromMap(self, params):
        """
        handle a character having selected expanding the internal storage
        by fetching more configuration info from the character
        and adding a task to the items task list

        Parameters:
            params: parameters given from the interaction menu
        """

        character = params["character"]

        if "storageCoordinate" not in params:
            params["storageCoordinate"] = list(params["coordinate"])

        if "stockPileType" not in params:
            options = [
                ("UniformStockpileManager", "UniformStockpileManager"),
                ("TypedStockpileManager", "TypedStockpileManager"),
            ]
            submenu = src.menuFolder.SelectionMenu.SelectionMenu(
                "What type of stockpile should be placed?", options,
                targetParamName="stockPileType",
            )
            character.macroState["submenue"] = submenu
            character.macroState["submenue"].followUp = {
                "container":self,
                "method":"expandStorageFromMap",
                "params":params,
            }
            return

        if "stockPileFunction" not in params:
            options = [("storage", "storage"), ("source", "source"), ("sink", "sink")]
            submenu = src.menuFolder.SelectionMenu.SelectionMenu(
                "what function should the stockpile have?", options,
                targetParamName="stockPileFunction",
            )
            character.macroState["submenue"] = submenu
            character.macroState["submenue"].followUp = {
                "container":self,
                "method":"expandStorageFromMap",
                "params":params,
            }
            return

        if params["stockPileType"] == "UniformStockpileManager" and "stockPileItemType" not in params:
            submenu = src.menuFolder.InputMenu.InputMenu(
                "type ItemType",
                targetParamName="stockPileItemType"
            )
            character.macroState["submenue"] = submenu
            character.macroState["submenue"].followUp = {
                "container":self,
                "method":"expandStorageFromMap",
                "params":params,
            }
            return

        newTask = {
            "task": "extend storage",
            "coordinate": params["storageCoordinate"],
            "stockPileType": params["stockPileType"],
            "stockPileFunction": params["stockPileFunction"],
        }
        if params["stockPileType"] == "UniformStockpileManager":
            newTask["itemType"] = params["stockPileItemType"]
        self.tasks.append(newTask)

    def reservePlotFromMap(self, params):
        """
        handle a character having selected reserving a plot
        by reserving a plot

        Parameters:
            params: parameters given from the interaction menu
        """

        plot = params["coordinate"]
        character = params["character"]

        if not plot:
            character.addMessage("no selection")
            return

        if plot not in self.plotPool:
            character.addMessage("not in plot pool")
            return

        self.plotPool.remove(plot)
        self.reservedPlots.append(plot)

    def unreservePlotFromMap(self, params):
        """
        handle a character having selected to unreserve a plot
        by unreserve a plot

        Parameters:
            params: parameters given from the interaction menu
        """

        plot = params["coordinate"]
        character = params["character"]

        if not plot:
            character.addMessage("no selection")
            return

        if plot not in self.reservedPlots:
            character.addMessage("not in plot pool")
            return

        self.reservedPlots.remove(plot)
        self.plotPool.append(plot)

    def markUnusedFromMap(self,params):
        """
        handle a character having selected to mark a road tile as unused
        by marking the road tile as unused

        Parameters:
            params: parameters given from the interaction menu
        """

        plot = params["coordinate"]
        self.unusedRoadTiles.append(plot)

    def markUsedFromMap(self,params):
        """
        handle a character having selected to mark a road tile as used
        by marking the road tile as used

        Parameters:
            params: parameters given from the interaction menu
        """

        plot = params["coordinate"]
        self.unusedRoadTiles.remove(plot)

    def expandFromMap(self,params):
        """
        handle a character having selected to expand the city
        by adding a task to the task list

        Parameters:
            params: parameters given from the interaction menu
        """

        coordinate = params["coordinate"]

        newTask = {"task": "expand", "from":list(coordinate)}
        self.tasks.append(newTask)

    def getConfigurationOptions(self, character):
        """
        register the configuration options with superclass

        Parameters:
            character: the character trying to conigure the machine
        """

        options = super().getConfigurationOptions(character)
        options["x"] = ("show map", self.showMap)
        options["e"] = ("retry task", self.retryTask)
        return options

    def retryTask(self, character):
        """
        handle a character trying to restart the currently running task
        by restarting the current task

        Parameters:
            character: character using this item
        """

        self.error = {}
        if self.runningTasks:
            self.tasks.extend(self.runningTasks)
            self.runningTasks = []

    def getLongInfo(self):
        """
        return a longer than normal description text

        Returns:
            the description text
        """

        text = f"""
resources:
{self.resources}

commands:
{self.commands}

error:
{self.error}

runningTasks:
{self.runningTasks}

tasks:
{self.tasks}

reservedPlots:
{self.reservedPlots}

usedPlots:
{self.usedPlots}

roadTiles:
{self.roadTiles}

unfinishedRoadTiles:
{self.unfinishedRoadTiles}

plotPool:
{self.plotPool}

unusedRoadTiles:
{self.unusedRoadTiles}

scrapFields:
{self.scrapFields}
"""
        return text

src.items.addType(CityBuilder)

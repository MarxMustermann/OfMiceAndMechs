import random

import src


class RoomManager(src.items.Item):
    """
    is supposed to handle the task that concern a room by sending npc around
    """

    type = "RoomManager"
    applyOptions = {}

    def __init__(self, name="RoomManager", noId=False):
        """
        configures the superclass and resets
        """

        super().__init__(display="##", name=name, noId=noId)

        # set item config options
        self.runsJobOrders = True
        self.hasSettings = True
        self.runCommands = True
        self.canReset = True
        self.hasMaintenance = True
        self.tasks = []

        # set up interaction menu
        self.applyOptions.extend(
                [
                    ("doMaintence", "do maintenance"),
                    ("do action", "do action"),
                    ("addTaskSelection", "add task"),
                    ("clearTasks", "clear tasks"),
                ]
            )
        self.applyMap = {
            "doMaintence": self.doMaintence,
            "do action": self.actionSelection,
            "addTaskSelection": self.addTaskSelection,
            "clearTasks": self.clearTasks,
        }

        # set state by resetting
        self.reset()

    def reset(self, character=None):
        """
        configures the superclass and resets

        Parameters:
            character: the character doing the reset
        """

        super().reset(character)

        # the storage for how things are used
        self.itemSlotUsage = {}

        # the slots where items can be placed
        self.freeItemSlots = [
            [2, 2],
            [2, 4],
            [4, 2],
            [4, 4],
            [8, 2],
            [10, 2],
            [8, 4],
            [10, 4],
            [8, 8],
            [10, 8],
            [8, 10],
            [10, 10],
            [2, 8],
            [4, 8],
            [2, 10],
            [4, 10],
        ]
        random.shuffle(self.freeItemSlots)

        # the queue of tasks to do
        self.tasks = [
            {"task": "add CityBuilder"},
        ]

        # store information about error state
        self.stuck = False
        self.stuckReason = None

        # positions of special items
        self.machineMachinePos = None
        self.bluePrintingArtworkPos = None
        self.cityBuilderPos = None
        self.resourceTerminalPositions = {}
        self.machinePositions = {}
        self.itemPositions = {}
        self.itemPositions = {}

        # storage for information on what items depend on each other
        self.dependencies = {}

        # the name of the manager used for pathing
        self.managerName = "comandCenter"

    # abstraction: should use superclass ability
    def actionSelection(self, character):
        """
        offers a selection to run and triggers running them

        Parameters:
            character: the character to run the action on
        """

        options = [
            ("storeItem", "add item to storage"),
            ("spawnMaintenanceNpc", "spawn maintenance npc"),
            ("startJoborderLoop", "start job order loop"),
        ]
        submenu = src.menuFolder.selectionMenu.SelectionMenu(
            "what action do you want to do?", options
        )
        character.macroState["submenue"] = submenu
        character.macroState["submenue"].followUp = {
            "method": "doAction",
            "container": self,
            "params": {"character":character},
        }

    def clearTasks(self, character):
        """
        remove all tasks from this machine

        Parameters:
            character: the character triggering this action
        """

        character.addMessage("cleared tasks")
        self.tasks = []

    def addTaskSelection(self, character):
        """
        offers a selection of tasks to add and triggers adding them to the machine

        Parameters:
            character: the character triggering this action
        """

        options = [
            ("add item", "add item"),
            ("add manager", "add manager"),
            ("add machine", "add machine"),
            ("add resource terminal", "add resource terminal"),
            ("add machine machine", "add machine machine"),
            ("add CityBuilder", "add CityBuilder"),
            ("clear all", "clear all"),
            ("clear item slot", "clear item slot"),
        ]
        submenu = src.menuFolder.selectionMenu.SelectionMenu(
            "what task do you want to add?", options
        )
        character.macroState["submenue"] = submenu
        character.macroState["submenue"].followUp = {
            "method": "addTask",
            "container": self,
            "params": {"character": character},
        }

    def generatePathFromTo(self, start, end):
        """
        generate a path from the start postion to the en position

        Parameters:
           start: the start position
           end: the end position
        Returns:
            the generated path
        """

        path = ""
        path += "a" * (start[0] - 6) + "d" * (6 - start[0])
        if start[1] > 6 and end[1] < 6:
            path += "w" * (start[1] - 7)
            path += "awwd"
            path += "w" * (5 - end[1])
        elif start[1] < 6 and end[1] > 6:
            path += "s" * (5 - (start[1]))
            path += "assd"
            path += "s" * (end[1] - 7)
        else:
            path += "w" * (start[1] - end[1]) + "s" * (end[1] - start[1])
        path += "a" * (6 - end[0]) + "d" * (end[0] - 6)
        return path

    def characterDropMachine(self, character, itemSlot):
        """
        makes a character drop something at an itemSlot

        Parameters:
            character: the character to drop the machine
            itemSlot: the position to drop the machine on
        """

        characterPos = [character.xPosition, character.yPosition]
        itemSlot = itemSlot[:]
        itemSlot[1] -= 1
        command = ""
        command += self.generatePathFromTo(characterPos, itemSlot)
        command += "Ls"
        command += self.generatePathFromTo(itemSlot, characterPos)
        character.runCommandString(command)

    def addTask(self,params):
        """
        add a new task to the machines task list

        Parameters:
            params: parameters from the selection
        """

        if "selection" not in params:
            return

        character = params["character"]
        character.addMessage(params)

        if params.get("tasksType") is None:
            params["tasksType"] = params["selection"]

            if params["tasksType"] in ("add machine", "add item", "add resource terminal"):
                submenu = src.menuFolder.inputMenu.InputMenu("item type")
                character.macroState["submenue"] = submenu
                character.macroState["submenue"].followUp = {
                    "method": "addTask",
                    "container": self,
                    "params": params,
                }
                return

            if params["tasksType"] in ("add manager",):
                options = [
                    ("StockpileMetaManager", "StockpileMetaManager"),
                    ("ArchitectArtwork", "ArchitectArtwork"),
                    ("RoadManager", "RoadManager"),
                    ("MiningManager", "MiningManager"),
                ]
                submenu = src.menuFolder.selectionMenu.SelectionMenu(
                    "select manager type", options
                )
                character.macroState["submenue"] = submenu
                character.macroState["submenue"].followUp = {
                    "method": "addTask",
                    "container": self,
                    "params": params,
                }
                return

        typeParameter = None
        if params["tasksType"] in ("add machine", "add item", "add resource terminal"):
            typeParameter = params["text"]
        if params["tasksType"] in ("add manager",):
            typeParameter = params["selection"]
            self.tasksType = "add item"

        if params["tasksType"] == "add item" and typeParameter not in src.items.itemMap:
            character.addMessage("item not found")
            return

        newTask = {
            "task": params["tasksType"],
        }

        if typeParameter is not None:
            newTask["type"] = typeParameter

        self.tasks.append(newTask)
        self.stuck = False
        self.stuckReason = None
        self.dependencies = {}

    def doAction(self,params):
        """
        run an action on a character

        Parameters:
            params: parameters from the selection
        """

        if "selection" not in params:
            return

        character = params["character"]
        selection = params["selection"]

        if selection == "startJoborderLoop":
            jobOrder = src.items.itemMap["JobOrder"]()
            itemSlot = random.choice(self.itemPositions["JobBoard"])
            newTasks = [
                {
                    "task": "go to job board",
                    "command": self.generatePathFromTo(
                        [character.xPosition, character.yPosition],
                        [itemSlot[0], itemSlot[1] - 1],
                    ),
                },
                {"task": "add job order", "command": "Js.ssj"},
                {
                    "task": "go back",
                    "command": self.generatePathFromTo(
                        [itemSlot[0], itemSlot[1] - 1],
                        [character.xPosition, character.yPosition],
                    ),
                },
            ]
            jobOrder.addTasks(newTasks)
            character.addJobOrder(jobOrder)

            payloadJobOrder = src.items.itemMap["JobOrder"]()
            newTasks = [
                {
                    "task": "go to room manager",
                    "command": self.generatePathFromTo(
                        [itemSlot[0], itemSlot[1] - 1],
                        [self.xPosition, self.yPosition - 1],
                    ),
                },
                {
                    "task": "do maintenance",
                    "command": "Js.j",
                },
                {
                    "task": "continue loop",
                    "command": "Js.sjssj",
                },
                {
                    "task": "go back",
                    "command": self.generatePathFromTo(
                        [self.xPosition, self.yPosition - 1],
                        [itemSlot[0], itemSlot[1] - 1],
                    ),
                },
            ]
            payloadJobOrder.addTasks(newTasks)
            character.addToInventory(payloadJobOrder)

        if selection == "storeItem":
            jobOrder = src.items.itemMap["JobOrder"]()
            jobOrder.taskName = "add item to storage"

            itemSlot = random.choice(self.itemPositions["StockpileMetaManager"])

            newTasks = [
                {
                    "task": "go to item",
                    "command": self.generatePathFromTo(
                        [character.xPosition, character.yPosition],
                        [itemSlot[0], itemSlot[1] - 1],
                    ),
                },
                {"task": "insert job order", "command": "scj"},
                {"task": "store item", "command": None},
                {
                    "task": "go back",
                    "command": self.generatePathFromTo(
                        [itemSlot[0], itemSlot[1] - 1],
                        [character.xPosition, character.yPosition],
                    ),
                },
            ]
            jobOrder.tasks.extend(list(reversed(newTasks)))
            character.addJobOrder(jobOrder)

        if selection == "spawnMaintenanceNpc":
            character = src.characters.Character(name="roommanager npc")
            character.godMode = True
            character.xPosition = self.xPosition
            character.yPosition = self.yPosition - 1
            self.container.addCharacter(character, self.xPosition, self.yPosition - 1)
            character.runCommandString("Js.j")

        character.addMessage("unkown action")

    def doMaintence(self, character):
        """
        make a character do some maintenance

        Parameters:
            character: the character that will do the maintenance
        """

        if self.stuck:
            character.addMessage(
                "machine is stuck and doesn't respond. reason: %s" % (self.stuckReason)
            )
            return
        if not self.tasks:
            if self.cityBuilderPos:
                command = ""
                command += self.generatePathFromTo(
                    [character.xPosition, character.yPosition],
                    [self.cityBuilderPos[0], self.cityBuilderPos[1] - 1],
                )
                command += "scm"
                command += self.generatePathFromTo(
                    [self.cityBuilderPos[0], self.cityBuilderPos[1] - 1],
                    [character.xPosition, character.yPosition],
                )
                character.runCommandString(command)
                return
            else:
                character.addMessage("no tasks")
                return

        task = self.tasks.pop()

        if task["task"] in (
            "add machine machine",
            "add resource terminal",
            "add machine",
            "add item",
            "add BluePrintingArtwork",
            "add CityBuilder",
        ):
            if not self.freeItemSlots:
                self.tasks.append(task)
                character.addMessage("no item slots left")
                # if self.container.xPosition == 7 and self.container.yPosition == 7 and not self.cityBuilderPos:
                if not self.cityBuilderPos and 1 == 0:
                    newTask = {"task": "add CityBuilder task", "payload": ["setup"]}
                    self.tasks.append(newTask)
                    newTask = {"task": "add CityBuilder"}
                    self.tasks.append(newTask)
                    newTask = {"task": "clear item slot"}
                    self.tasks.append(newTask)
                elif 1 == 1:
                    newTask = {"task": "clear item slot"}
                    self.tasks.append(newTask)
                else:
                    self.stuckReason = "no item slots left"
                    self.stuck = True
                return
            itemSlot = self.freeItemSlots.pop()

        import random

        character.addMessage(task)
        if task["task"] == "add item":
            if task["type"] not in src.items.itemMap:
                character.addMessage("item not found")
                return
            item = src.items.itemMap[task["type"]]()

            character.inventory.append(item)

            jobOrder = src.items.itemMap["JobOrder"]()
            tasks = []
            tasks.extend(
                [
                    {
                        "task": "go to dropoff position",
                        "command": self.generatePathFromTo(
                            [character.xPosition, character.yPosition],
                            [itemSlot[0], itemSlot[1] - 1],
                        ),
                    },
                    {
                        "task": "dropoff machine",
                        "command": "Ls",
                    },
                ]
            )
            if task["type"] in (
                "MiningManager",
                "StockpileMetaManager",
                "ArchitectArtwork",
                "RoadManager",
                "JobBoard",
            ):
                commands = {}
                commands["go to room manager"] = self.generatePathFromTo(
                    [itemSlot[0], itemSlot[1] - 1],
                    [self.xPosition, self.yPosition - 1],
                )
                commands["return from room manager"] = self.generatePathFromTo(
                    [self.xPosition, self.yPosition - 1],
                    [itemSlot[0], itemSlot[1] - 1],
                )

                configureTask = {
                    "task": "configure machine",
                    "command": None,
                    "commands": commands,
                    "managerName": self.managerName,
                }

                tasks.extend(
                    [
                        {
                            "task": "insert job order",
                            "command": "scj",
                        },
                        configureTask,
                    ]
                )
            tasks.extend(
                [
                    {
                        "task": "return to start position",
                        "command": self.generatePathFromTo(
                            [itemSlot[0], itemSlot[1] - 1],
                            [character.xPosition, character.yPosition],
                        ),
                    }
                ]
            )
            jobOrder.tasks = list(reversed(tasks))
            jobOrder.taskName = "add item to room"
            character.addJobOrder(jobOrder)

            self.itemSlotUsage[tuple(itemSlot)] = task
            if task["type"] not in self.itemPositions:
                self.itemPositions[task["type"]] = []
            self.itemPositions[task["type"]].append(itemSlot)

        if task["task"] == "clear item slot":
            foundSlot = None
            itemSlots = random.choice(list(self.itemSlotUsage.keys()))
            for itemSlot in itemSlots:
                itemSlot = list(random.choice(list(self.itemSlotUsage.keys())))
                originalTask = self.itemSlotUsage[tuple(itemSlot)]
                if originalTask["task"] == "add machine":
                    foundSlot = itemSlot
                    break

            if not foundSlot:
                character.addMessage("no slot found")
                return

            toRemove = [foundSlot]
            while toRemove:
                removeSlot = toRemove.pop()
                if tuple(removeSlot) in self.dependencies:
                    toRemove.extend(self.dependencies[tuple(removeSlot)])
                    del self.dependencies[tuple(removeSlot)]

                for dependencyList in self.dependencies.values():
                    if removeSlot in dependencyList:
                        dependencyList.remove(removeSlot)

                if tuple(removeSlot) not in self.itemSlotUsage:
                    continue

                originalTask = self.itemSlotUsage[tuple(removeSlot)]
                if originalTask["task"] == "add machine":
                    self.machinePositions[originalTask["type"]].remove(removeSlot)
                    if not self.machinePositions[originalTask["type"]]:
                        del self.machinePositions[originalTask["type"]]

                self.container.clearCoordinate(removeSlot)
                self.freeItemSlots.append(removeSlot)
                del self.itemSlotUsage[tuple(removeSlot)]
            return

        if task["task"] == "clear all":
            toRemove = []
            for item in self.container.itemsOnFloor:
                if item == self:
                    continue
                if item.xPosition in (0, 12):
                    continue
                if item.yPosition in (0, 12):
                    continue
                toRemove.append(item)
            self.container.removeItems(toRemove)
            self.reset()

        if task["task"] == "add CityBuilder":
            machine = src.items.itemMap["CityBuilder"]()
            if not self.cityBuilderPos:
                self.cityBuilderPos = itemSlot
            character.inventory.append(machine)
            self.characterDropMachine(character, itemSlot)
            self.itemSlotUsage[tuple(itemSlot)] = task

            commands = {}
            commands["go to room manager"] = self.generatePathFromTo(
                [self.cityBuilderPos[0], self.cityBuilderPos[1] - 1],
                [self.xPosition, self.yPosition - 1],
            )
            commands["return from room manager"] = self.generatePathFromTo(
                [self.xPosition, self.yPosition - 1],
                [self.cityBuilderPos[0], self.cityBuilderPos[1] - 1],
            )

            jobOrder = src.items.itemMap["JobOrder"]()
            jobOrder.tasks = list(
                reversed(
                    [
                        {
                            "task": "go to dropoff position",
                            "command": self.generatePathFromTo(
                                [character.xPosition, character.yPosition],
                                [self.cityBuilderPos[0], self.cityBuilderPos[1] - 1],
                            ),
                        },
                        {
                            "task": "dropoff machine",
                            "command": "Ls",
                        },
                        {
                            "task": "insert job order",
                            "command": "scj",
                        },
                        {
                            "task": "configure machine",
                            "command": None,
                            "commands": commands,
                        },
                        {
                            "task": "return to start position",
                            "command": self.generatePathFromTo(
                                [self.cityBuilderPos[0], self.cityBuilderPos[1] - 1],
                                [character.xPosition, character.yPosition],
                            ),
                        },
                    ]
                )
            )
            jobOrder.taskName = "install city builder"

            character.addMessage("running job order to install machine")
            character.addJobOrder(jobOrder)

        if task["task"] == "add BluePrintingArtwork":
            machine = src.items.items["BluePrintingArtwork"]()
            if not self.bluePrintingArtworkPos:
                self.bluePrintingArtworkPos = itemSlot
            character.inventory.append(machine)
            self.characterDropMachine(character, itemSlot)
            self.itemSlotUsage[tuple(itemSlot)] = task
        if task["task"] == "add machine machine":
            if not self.bluePrintingArtworkPos:
                self.tasks.append(task)
                self.freeItemSlots.append(itemSlot)
                newTask = {"task": "add BluePrintingArtwork"}
                self.tasks.append(newTask)
                return
            if not self.resourceTerminalPositions.get("MetalBars"):
                self.tasks.append(task)
                self.freeItemSlots.append(itemSlot)
                newTask = {"task": "add resource terminal", "type": "MetalBars"}
                self.tasks.append(newTask)
                return

            machine = src.items.MachineMachine(None, None)
            self.machineMachinePos = itemSlot

            character.inventory.append(machine)
            self.characterDropMachine(character, itemSlot)
            self.itemSlotUsage[tuple(itemSlot)] = task

        if task["task"] == "add resource terminal":
            machine = src.items.ResourceTerminal(itemSlot[0], itemSlot[1])
            machine.balance = 1000
            machine.resource = task["type"]
            if "MetalBars" not in self.resourceTerminalPositions:
                self.resourceTerminalPositions["MetalBars"] = []
            self.resourceTerminalPositions["MetalBars"].append(itemSlot)

            character.inventory.append(machine)
            self.characterDropMachine(character, itemSlot)
            self.itemSlotUsage[tuple(itemSlot)] = task

        if task["task"] == "add machine":

            if not self.machineMachinePos:
                self.tasks.append(task)
                self.freeItemSlots.append(itemSlot)
                newTask = {"task": "add machine machine"}
                self.tasks.append(newTask)
                return

            needResources = src.items.rawMaterialLookup[task["type"]]

            missingResource = None
            needsMetalbars = False
            for resource in needResources:
                if resource not in self.machinePositions:
                    if resource == "MetalBars":
                        needsMetalbars = True
                        continue
                    missingResource = resource
                    break

            if missingResource:
                self.tasks.append(task)
                self.freeItemSlots.append(itemSlot)
                newTask = {"task": "add machine", "type": missingResource}
                self.tasks.append(newTask)
                return

            if needsMetalbars and not self.resourceTerminalPositions.get("MetalBars"):
                self.tasks.append(task)
                self.freeItemSlots.append(itemSlot)
                newTask = {"task": "add resource terminal", "type": "MetalBars"}
                self.tasks.append(newTask)
                return

            for resource in needResources:
                if resource == "MetalBars":
                    candidateList = self.resourceTerminalPositions.get(resource, [])
                else:
                    candidateList = self.machinePositions.get(resource, [])

                for candidate in candidateList:
                    desiredPos = candidate[:]
                    desiredPos[0] += 2

                    if desiredPos in self.freeItemSlots:
                        self.freeItemSlots.append(itemSlot)
                        itemSlot = desiredPos
                        self.freeItemSlots.remove(itemSlot)

            commands = {}
            commands["cooldown"] = "20.Js"

            itemCount = 0
            for resource in needResources:
                if resource == "MetalBars":
                    if self.resourceTerminalPositions.get("MetalBars"):
                        resourceTerminalPos = random.choice(
                            self.resourceTerminalPositions.get("MetalBars")
                        )
                        command = ""
                        command += self.generatePathFromTo(
                            [itemSlot[0], itemSlot[1] - 1],
                            [resourceTerminalPos[0], resourceTerminalPos[1] - 1],
                        )
                        command += "Js.ssj"
                        command += self.generatePathFromTo(
                            [resourceTerminalPos[0], resourceTerminalPos[1] - 1],
                            [itemSlot[0], itemSlot[1] - 1],
                        )
                        if itemCount == 0:
                            command += "aLsdJs"
                        else:
                            command += "lJs"
                        commands["material MetalBars"] = command
                        if tuple(resourceTerminalPos) not in self.dependencies:
                            self.dependencies[tuple(resourceTerminalPos)] = []
                        self.dependencies[tuple(resourceTerminalPos)].append(itemSlot)
                else:
                    if resource in self.machinePositions:
                        targetPos = random.choice(self.machinePositions[resource])
                        command = ""
                        command += self.generatePathFromTo(
                            [itemSlot[0], itemSlot[1] - 1],
                            [targetPos[0], targetPos[1] - 1],
                        )
                        command += "JsdKsa"
                        command += self.generatePathFromTo(
                            [targetPos[0], targetPos[1] - 1],
                            [itemSlot[0], itemSlot[1] - 1],
                        )
                        if itemCount == 0:
                            command += "aLsdJs"
                        else:
                            command += "lJs"
                        commands["material " + resource] = command

                        if tuple(targetPos) not in self.dependencies:
                            self.dependencies[tuple(targetPos)] = []
                        self.dependencies[tuple(targetPos)].append(itemSlot)
                itemCount += 1

            resourceTerminalPos = random.choice(
                self.resourceTerminalPositions.get("MetalBars")
            )
            jobOrder = src.items.itemMap["JobOrder"]()
            jobOrder.tasks = list(
                reversed(
                    [
                        {
                            "task": "go to blueprinting artwork",
                            "command": self.generatePathFromTo(
                                [character.xPosition, character.yPosition],
                                [
                                    self.bluePrintingArtworkPos[0],
                                    self.bluePrintingArtworkPos[1] - 1,
                                ],
                            ),
                        },
                        {
                            "task": "produce blueprint",
                            "command": [*list("Js" + task["type"]), "enter", *list("dKsa")],
                        },
                        {
                            "task": "go to resource terminal",
                            "command": self.generatePathFromTo(
                                [
                                    self.bluePrintingArtworkPos[0],
                                    self.bluePrintingArtworkPos[1] - 1,
                                ],
                                [resourceTerminalPos[0], resourceTerminalPos[1] - 1],
                            ),
                        },
                        {
                            "task": "fetch metal bars",
                            "command": "Js.ssj",
                        },
                        {
                            "task": "go to machine machine",
                            "command": self.generatePathFromTo(
                                [resourceTerminalPos[0], resourceTerminalPos[1] - 1],
                                [
                                    self.machineMachinePos[0],
                                    self.machineMachinePos[1] - 1,
                                ],
                            ),
                        },
                        {
                            "task": "load blueprint",
                            "command": "aLsdil"
                            + "s" * len(character.inventory)
                            + "jJs.j",
                        },
                        {
                            "task": "run job order",
                            "command": "scj",
                        },
                        {
                            "task": "produce machine",
                            "command": None,
                            "type": task["type"],
                        },
                        {
                            "task": "pick up machine",
                            "command": "dKsa",
                        },
                        {
                            "task": "go to dropoff position",
                            "command": self.generatePathFromTo(
                                [
                                    self.machineMachinePos[0],
                                    self.machineMachinePos[1] - 1,
                                ],
                                [6, 5],
                            )
                            + self.generatePathFromTo(
                                [6, 5], [itemSlot[0], itemSlot[1] - 1]
                            ),
                        },
                        {
                            "task": "dropoff machine",
                            "command": "Ls",
                        },
                        {
                            "task": "insert job order",
                            "command": "scj",
                        },
                        {
                            "task": "configure machine",
                            "command": None,
                            "commands": commands,
                        },
                        {
                            "task": "go to resource terminal",
                            "command": self.generatePathFromTo(
                                [itemSlot[0], itemSlot[1] - 1],
                                [resourceTerminalPos[0], resourceTerminalPos[1] - 1],
                            ),
                        },
                        {
                            "task": "return metal bars",
                            "command": "Js.sj",
                        },
                        {
                            "task": "return to start position",
                            "command": self.generatePathFromTo(
                                [resourceTerminalPos[0], resourceTerminalPos[1] - 1],
                                [character.xPosition, character.yPosition],
                            ),
                        },
                    ]
                )
            )
            jobOrder.taskName = "drop machine"

            newTask = {"task": "test machine", "itemSlot": itemSlot}
            self.tasks.append(newTask)

            character.addMessage("running job order to install machine")
            character.addJobOrder(jobOrder)

            if task["type"] not in self.machinePositions:
                self.machinePositions[task["type"]] = []
            self.machinePositions[task["type"]].append(itemSlot)

            self.itemSlotUsage[tuple(itemSlot)] = task

    def fetchSpecialRegisterInformation(self):
        """
        returns some of the objects state to be stored ingame in a characters registers
        this is intended to be overwritten to add more information

        Returns:
            a dictionary containing the information
        """

        result = super().fetchSpecialRegisterInformation()

        result["free item slots"] = self.freeItemSlots
        result["num free item slots"] = len(self.freeItemSlots)
        result["stuck"] = self.stuck
        result["stuckReason"] = self.stuckReason
        result["city builder position"] = self.cityBuilderPos
        result["machine machine position"] = self.machineMachinePos
        result["blue printing artwork position"] = self.bluePrintingArtworkPos
        result["resource terminal positions"] = self.resourceTerminalPositions
        result["machine positions"] = self.machinePositions

        return result

    def getJobOrderTriggers(self):
        """
        returns a dict of lists containing callbacks to be triggered by a job order

        Returns:
            a dict of lists
        """

        result = {}
        self.addTriggerToTriggerMap(result, "relay job order", self.relayJobOrder)
        self.addTriggerToTriggerMap(result, "add Tasks", self.addTasks)
        self.addTriggerToTriggerMap(result, "go to item", self.jobOrderGoToItem)
        return result

    def jobOrderGoToItem(self, task, context):
        character = context["character"]
        itemType = task["item"]

        import random
        itemSlot = random.choice(self.itemPositions[itemType])

        command = self.generatePathFromTo((character.xPosition,character.yPosition), (itemSlot[0],itemSlot[1]-1))

        character.runCommandString(command)

    def addTasks(self, task, context):
        """
        add new task using a job order

        Parameters:
            task: the task for setting the task. NOT the task to set
            context: the context for this task
        """

        self.tasks.extend(task["tasks"])

    def relayJobOrder(self, task, context):
        """
        make a character use the current job order on a different item

        Parameters:
            task: information about the task
            context: the context for this task
        """

        jobOrder = context["jobOrder"]
        character = context["character"]

        relayedTask = jobOrder.popTask()

        if (
            task["ItemType"] not in self.itemPositions
            and task["ItemType"] != "CityBuilder"
        ):
            jobOrder.error = {
                "message": "tried to relay task, but item %s was not found"
                % task["ItemType"],
                "itemType": task["ItemType"],
                "task": task,
                "type": "item not found",
            }
            character.addMessage("no such item found")
            return

        if task["ItemType"] == "CityBuilder":
            itemSlot = self.cityBuilderPos
        else:
            import random

            itemSlot = random.choice(self.itemPositions[task["ItemType"]])

        newTasks = [
            {
                "task": "go to item",
                "command": self.generatePathFromTo(
                    [character.xPosition, character.yPosition],
                    [itemSlot[0], itemSlot[1] - 1],
                ),
            },
            {"task": "insert job order", "command": "scj"},
            relayedTask,
            {
                "task": "go back",
                "command": self.generatePathFromTo(
                    [itemSlot[0], itemSlot[1] - 1],
                    [character.xPosition, character.yPosition],
                ),
            },
        ]
        jobOrder.tasks.extend(list(reversed(newTasks)))

    def getLongInfo(self):
        """
        return a longer than normal description text

        Returns:
            the description text
        """

        text = super().getLongInfo()
        text += f"""

itemPositions:
{self.itemPositions}

dependencies:
{self.dependencies}

itemSlotUsage:
{self.itemSlotUsage}

machines:

"""
        for (key, value) in self.machinePositions.items():
            text += f"\n{key}: {value}"

        text += """

tasks:
"""

        for task in self.tasks:
            text += f"{task} \n"
        text += f"""

commands:
{self.commands}

"""
        return text


src.items.addType(RoomManager)

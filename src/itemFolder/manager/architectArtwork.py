import src
import random
import json

class ArchitectArtwork(src.items.Item):
    """
    god mode item for terraforming and things
    also used to build stuff ingame
    """

    type = "ArchitectArtwork"

    def __init__(self):
        """
        configure super class and initialise internal state
        """

        super().__init__(display="AA")

        self.name = "architect artwork"
        self.runsJobOrders = True
        self.godMode = False

    def getJobOrderTriggers(self):
        """
        returns a dict of lists containing callbacks to be triggered by a job order

        Returns:
            a dict of lists
        """

        result = super().getJobOrderTriggers()
        self.addTriggerToTriggerMap(
            result, "add scrap field", self.jobOrderAddScrapField
        )
        self.addTriggerToTriggerMap(result, "set up", self.doSetUp)
        self.addTriggerToTriggerMap(
            result, "connect stockpile", self.doConnectStockpile
        )
        return result

    # obsolete: stockpile are build on existing roads only
    def doConnectStockpile(self, task, context):
        """
        connect a stockpile to something else
        this is done by sending npcs around and delegating tasks

        Parameters:
            task: detail for this task
            context: the context for this task
        """

        jobOrder = context["jobOrder"]

        if "pathFrom" not in jobOrder.information:
            tasks = [
                {
                    "task": "go to room manager",
                    "command": self.commands["go to room manager"],
                },
                {"task": "insert job order", "command": "scj"},
                {
                    "task": "relay job order",
                    "command": None,
                    "ItemType": "RoadManager",
                },
                {
                    "task": "print paths",
                    "command": None,
                    "to": task["stockPileCoordinate"],
                },
                {
                    "task": "return from room manager",
                    "command": self.commands["return from room manager"],
                },
                {"task": "reactivate architect", "command": "scj"},
                task,
            ]
            context["jobOrder"].tasks.extend(list(reversed(tasks)))
            return

        if task["type"] == "add to storage":
            newTask = {
                "task": "add stockpile",
                "nodeName": task["stockPile"],
                "pathFrom": jobOrder.information["pathFrom"],
                "pathTo": jobOrder.information["pathTo"],
            }

            if task.get("function"):
                newTask["function"] = task["function"]

            self.useJoborderRelayToLocalRoom(
                context["character"],
                [
                    newTask,
                    {"task": "do maintenance"},
                ],
                "StockpileMetaManager",
            )

            del jobOrder.information["pathFrom"]
            del jobOrder.information["pathTo"]

        if task["type"] == "set wrong item to storage":
            newJobOrder = src.items.itemMap["JobOrder"]()
            newJobOrder.taskName = "configure stockpile"

            storageCommand = (
                jobOrder.information["pathFrom"]
                + "Js.sjj"
                + jobOrder.information["pathTo"]
            )

            tasks = [
                {
                    "task": "go to room manager",
                    "command": self.commands["go to room manager"],
                },
                {"task": "go to stockPile", "command": jobOrder.information["pathTo"]},
                {"task": "insert job order", "command": "scj"},
                {
                    "task": "configure machine",
                    "command": None,
                    "commands": {"wrong": storageCommand},
                },
                {
                    "task": "return from stockPile",
                    "command": jobOrder.information["pathFrom"],
                },
                {
                    "task": "return from room manager",
                    "command": self.commands["return from room manager"],
                },
            ]

            newJobOrder.tasks = list(reversed(tasks))
            context["character"].addJobOrder(newJobOrder)
            del jobOrder.information["pathFrom"]
            del jobOrder.information["pathTo"]

        if task["type"] == "set source" and "sourceCommand" in task:
            newJobOrder = src.items.itemMap["JobOrder"]()
            newJobOrder.taskName = "configure stockpile"

            storageCommand = (
                jobOrder.information["pathFrom"]
                + "Js.sjj"
                + jobOrder.information["pathTo"]
            )

            tasks = [
                {
                    "task": "go to room manager",
                    "command": self.commands["go to room manager"],
                },
                {
                    "task": "go to stockPile",
                    "command": jobOrder.information["pathTo"],
                },
                {"task": "insert job order", "command": "scj"},
                {
                    "task": "configure machine",
                    "command": None,
                    "commands": {"empty": task["sourceCommand"]},
                },
                {
                    "task": "return from stockPile",
                    "command": jobOrder.information["pathFrom"],
                },
                {
                    "task": "return from room manager",
                    "command": self.commands["return from room manager"],
                },
            ]

            newJobOrder.tasks = list(reversed(tasks))
            context["character"].addJobOrder(newJobOrder)
            del jobOrder.information["pathFrom"]
            del jobOrder.information["pathTo"]

    def jobOrderAddScrapField(self, task, character):
        """
        spawn a scrap field (god mode)

        Parameters:
            task: detail for this task
            context: the context for this task
        """

        self.doAddScrapfield(
            task["coordinate"][0], task["coordinate"][1], task["amount"]
        )

    def doSetUp(self, task, context):
        """
        build a structure

        Parameters:
            task: detail for this task
            context: the context for this task
        """

        if task["type"] == "stockPile":
            self.useJoborderRelayToLocalRoom(
                context["character"],
                [
                    {
                        "task": "add pathing node",
                        "nodeName": task["name"],
                        "coordinate": task["coordinate"],
                        "command": None,
                        "offset": [7, 6],
                    },
                ],
                "RoadManager",
            )
            items = []
            if task.get("StockpileType") == "UniformStockpileManager":
                item = src.items.itemMap["UniformStockpileManager"]()
                if task.get("ItemType"):
                    item.storedItemType = task.get("ItemType")
                item.storedItemWalkable = None
                item.restrictStoredItemType = True
                item.restrictStoredItemWalkable = False
                items.append(
                    (
                        item,
                        (
                            task["coordinate"][0] * 15 + 7,
                            task["coordinate"][1] * 15 + 7,
                            0,
                        ),
                    )
                )
            else:
                items.append(
                    (
                        src.items.itemMap["TypedStockpileManager"](),
                        (
                            task["coordinate"][0] * 15 + 7,
                            task["coordinate"][1] * 15 + 7,
                            0,
                        ),
                    )
                )
            self.getTerrain().addItems(items)

        if task["type"] == "factory":
            self.doAddRoom(
                {
                    "coordinate": task["coordinate"],
                    "roomType": "EmptyRoom",
                    "doors": "0,6 6,0 12,6 6,12",
                    "offset": [1, 1],
                    "size": [13, 13],
                },
                context,
            )
        if task["type"] == "room":
            self.doAddRoom(
                {
                    "coordinate": task["coordinate"],
                    "roomType": "EmptyRoom",
                    "doors": "0,6 6,0 12,6 6,12",
                    "offset": [1, 1],
                    "size": [13, 13],
                },
                context,
            )
        if task["type"] == "oreProcessing":
            items = []
            positions = [
                (2, 2),
                (2, 4),
                (2, 6),
                (5, 4),
                (5, 2),
                (5, 13),
                (5, 11),
                (2, 9),
                (2, 11),
                (2, 13),
            ]
            for position in positions:
                items.append(
                    (
                        src.items.itemMap["ScrapCompactor"](),
                        (
                            task["coordinate"][0] * 15 + position[0],
                            task["coordinate"][1] * 15 + position[1],
                            0,
                        ),
                    )
                )

            positions = [
                (9, 2),
                (12, 2),
                (9, 4),
                (12, 4),
                (12, 6),
                (12, 9),
                (9, 11),
                (12, 11),
                (9, 13),
                (12, 13),
            ]
            for position in positions:
                items.append(
                    (
                        src.items.itemMap["PavingGenerator"](),
                        (
                            task["coordinate"][0] * 15 + position[0],
                            task["coordinate"][1] * 15 + position[1],
                            0,
                        ),
                    )
                )

            self.getTerrain().addItems(items)
        if task["type"] == "mine":
            if not task.get("cleared"):
                self.useJoborderRelayToLocalRoom(
                    context["character"],
                    [
                        {
                            "task": "clear paths",
                            "coordinate": task["scrapField"][0],
                        },
                    ],
                    "RoadManager",
                )
                task["cleared"] = True
                context["jobOrder"].tasks.append(task)
                context["jobOrder"].tasks.append(
                    {"task": "insert job order", "command": "scj"}
                )
                return

            item = src.items.itemMap["ItemCollector"]()
            stockPileCoordinate = task["stocKPileCoordinate"]
            if stockPileCoordinate:
                clearInventoryCommand = "Js.j" * 10
                if stockPileCoordinate[0] > task["scrapField"][0][0]:
                    item.commands["fullInventory"] = (
                        "12dwd" + clearInventoryCommand + "as12a"
                    )
                if stockPileCoordinate[0] < task["scrapField"][0][0]:
                    item.commands["fullInventory"] = (
                        "12awa" + clearInventoryCommand + "ds12d"
                    )
                if stockPileCoordinate[1] < task["scrapField"][0][1]:
                    item.commands["fullInventory"] = (
                        "12wawwd" + clearInventoryCommand + "assd12s"
                    )
                if stockPileCoordinate[1] > task["scrapField"][0][1]:
                    item.commands["fullInventory"] = (
                        "12s" + clearInventoryCommand + "12w"
                    )
            self.getTerrain().addItem(
                item,
                (
                    task["scrapField"][0][0] * 15 + 7,
                    task["scrapField"][0][1] * 15 + 7,
                    0,
                ),
            )

        if task["type"] == "road":
            self.doClearField(task["coordinate"][0], task["coordinate"][1])
            self.useJoborderRelayToLocalRoom(
                context["character"],
                [
                    {
                        "task": "add road",
                        "coordinate": task["coordinate"],
                    },
                ],
                "RoadManager",
            )

    def doRegisterResult(self, task, context):
        """
        handle getting a report about a job done

        Parameters:
            task: detail for this task
            context: the context for this task
        """

        if context["jobOrder"].error and not context["jobOrder"].getTask() and len(context["character"].jobOrders) > 1:
            jobOrder = context["character"].jobOrders[-2]
            jobOrder.error = context["jobOrder"].error

    def apply(self, character):
        """
        handle a character trying to use his item
        by offering a selection of possible actions

        Parameters:
            character: the character trying to use this item
        """

        options = [
            ("showMap", "shop map of the area"),
            ("addScrapField", "add scrap field"),
            ("shapeTerrain", "shape terrain"),
            ("addRoom", "add room"),
            ("clearField", "clear coordinate"),
            ("addRemnant", "add remnant"),
            ("fill map", "fill map"),
            ("generate maze", "generate maze"),
            ("test", "test"),
        ]
        self.submenue = src.interaction.SelectionMenu(
            "what do you want to do?", options
        )
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.apply2
        self.character = character

    # bad code: should not exist
    def test(self):
        """
        show debug info or trigger a test function
        """


    def addRemants(self,character):
        terrain = self.getTerrain()

        roomsPositions = []

        with open("states/abandondedCityCore.json") as stateFile:
            roomData = json.loads(stateFile.read())
        room = src.rooms.getRoomFromState(roomData,src.gamestate.gamestate.terrain)
        terrain.addRoom(room)
        character.addMessage("added abandoned city core")
        roomsPositions.append((7,7))

        streets = []
        connections = {}
        for _i in range(5):
            xPosition = random.randint(1,13)
            yPosition = random.randint(1,13)

            if xPosition in (7,8,9) and yPosition in (7,8,9):
                continue
            if (xPosition,yPosition) in roomsPositions:
                continue

            with open("states/emptyRoom.json") as stateFile:
                roomData = json.loads(stateFile.read())
            room = src.rooms.getRoomFromState(roomData,src.gamestate.gamestate.terrain)
            room.xPosition = xPosition
            room.yPosition = yPosition

            for _j in range(1,random.randint(4,10)):
                enemy = src.characters.Spider()
                enemy.godMode = True
                room.addCharacter(enemy,random.randint(1,11),random.randint(1,11))
                enemy.startDefending()
            for _j in range(1,random.randint(4,40)):
                net = src.items.itemMap["SpiderNet"]()
                room.addItem(net,(random.randint(1,11),random.randint(1,11),0))
            for _j in range(1,random.randint(4,10)):
                net = src.items.itemMap["AcidBladder"]()
                room.addItem(net,(random.randint(1,11),random.randint(1,11),0))

            terrain.addRoom(room)
            roomsPositions.append((xPosition,yPosition))

            adjustedPosition = [xPosition,yPosition]

            while 1:
                if adjustedPosition[0] > 7:
                    direction = (-1,0)
                    backDirection = (1,0)
                elif adjustedPosition[0] < 7:
                    direction = ( 1,0)
                    backDirection = (-1,0)
                else:
                    if adjustedPosition[1] > 7:
                        direction = (0,-1)
                        backDirection = (0,1)
                    elif adjustedPosition[1] < 7:
                        direction = (0, 1)
                        backDirection = (0,-1)
                    else:
                        break

                if tuple(adjustedPosition) in connections:
                    connections[tuple(adjustedPosition)].append(direction)

                adjustedPosition[0] += direction[0]
                adjustedPosition[1] += direction[1]

                if not tuple(adjustedPosition) in streets:
                    streets.append(tuple(adjustedPosition))
                    connections[tuple(adjustedPosition)] = []

                connections[tuple(adjustedPosition)].append(backDirection)

        enemy = src.characters.Spider()
        enemy.godMode = True
        terrain.addCharacter(enemy,96,115)


        character.addMessage("added empty rooms")
        character.addMessage(f"{roomsPositions}")
        character.addMessage(f"{streets}")

        for street in streets:
            xPosition = street[0]
            yPosition = street[1]

            positions = [(6,6),(6,7),(6,8),(7,6),(8,6),(8,7),(8,8),(7,8)]
            roadPart = []
            directions = [(1,0),(0,-1)]
            for direction in connections[street]:
                start = [7,7]
                for _j in range(1,7):
                    start[0] += direction[0]
                    start[1] += direction[1]
                    positions.append(tuple(start))

            for position in positions:
                paving = src.items.itemMap["Paving"]()
                pos = (xPosition*15+position[0],yPosition*15+position[1],0)
                if terrain.getItemByPosition(pos):
                    continue
                terrain.addItem(paving,pos)
            #character.addMessage("added remnant paving to %s/%s"%(xPosition,yPosition,))

    def generateMaze(self):
        """
        build a maze
        """

        self.fillMap()
        self.doClearField(self.xPosition//15,self.xPosition//15)

        terrain = self.getTerrain()
        center = (self.xPosition//15,self.xPosition//15)

        # generate room slots
        roomSlots = []
        ringrooms = []
        ringrooms.append((5,7))
        ringrooms.append((7,5))
        ringrooms.append((9,7))
        ringrooms.append((7,9))
        roomSlots.extend(ringrooms)
        for _i in range(1,50):
            x = random.randint(1,13)
            y = random.randint(1,13)

            if abs(x-7) < 2 and abs(y-7) < 2:
                continue

            if not (x,y) in roomSlots:
                roomSlots.append((x,y))

        freeRoomSlots = roomSlots[:]
        roomMap = []
        for y in range(15):
            roomMap.append([])
            for _x in range(15):
                roomMap[y].append("  ")

        # add target room
        targetRoomSlot = random.choice(freeRoomSlots)
        while targetRoomSlot in freeRoomSlots:
            freeRoomSlots.remove(targetRoomSlot)
            roomMap[targetRoomSlot[1]][targetRoomSlot[0]] = "RC"
        memoryCellRoom = random.choice(freeRoomSlots)
        while memoryCellRoom in freeRoomSlots:
            freeRoomSlots.remove(memoryCellRoom)
            roomMap[memoryCellRoom[1]][memoryCellRoom[0]] = "mc"
        pocketFrameRoom = random.choice(freeRoomSlots)
        while pocketFrameRoom in freeRoomSlots:
            freeRoomSlots.remove(pocketFrameRoom)
            roomMap[pocketFrameRoom[1]][pocketFrameRoom[0]] = "pf"

        pathSlots = []
        crossroads = []

        """
        # sort rooms by distance
        sortingHelper = {}
        for roomSlot in roomSlots:
            distance = abs(roomSlot[0]-7)-abs(roomSlot[1]-7)
        roomSlots = sorted(roomSlots,key=abs(roomSlot[0]-7)-abs(roomSlot[1]-7)
        """

        # clear paths to rooms
        for roomSlot in roomSlots:
            self.doClearField(roomSlot[0],roomSlot[1])

        connectedRooms = []
        for roomSlot in roomSlots:

            x = roomSlot[0]
            y = roomSlot[1]

            hasNeighbour = False
            for pos in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
                if pos in connectedRooms:
                    hasNeighbour = True

            if hasNeighbour:
                pass
                #continue

            last = None
            while x != 7 or y != 7:

                items = []
                if x > 7:
                    direction = "west"
                elif x < 7:
                    direction = "east"
                elif y > 7:
                    direction = "north"
                elif y < 7:
                    direction = "south"

                # bug: does not work as intended
                if (x-1,y) in pathSlots and last != (x - 1, y) and x > 7:
                    direction = "west"
                if (x+1,y) in pathSlots and last != (x + 1, y) and x < 7:
                    direction = "east"
                if (x,y-1) in pathSlots and last != (x, y - 1) and y > 7:
                    direction = "north"
                if (x,y+1) in pathSlots and last != (x, y + 1) and y < 7:
                    direction = "south"

                if x > 7 and (x-1,y) in roomSlots:
                    direction = "west"
                if x < 7 and (x+1,y) in roomSlots:
                    direction = "east"
                if y > 7 and (x,y-1) in roomSlots:
                    direction = "north"
                if y < 7 and (x,y+1) in roomSlots:
                    direction = "south"

                if abs(x-7) < 2 and abs(y-7) < 2:
                    if y < 7:
                        direction = "south"
                    if y > 7:
                        direction = "north"
                    if x > 7:
                        direction = "west"
                    if x < 7:
                        direction = "east"

                if direction == "west":
                    for pathPos in range(-8,8):
                        items.extend(terrain.getItemByPosition((x*15+pathPos,y*15+7,0)))
                    x = x-1
                elif direction == "east":
                    for pathPos in range(8,23):
                        items.extend(terrain.getItemByPosition((x*15+pathPos,y*15+7,0)))
                    x = x+1
                elif direction == "north":
                    for pathPos in range(-8,8):
                        items.extend(terrain.getItemByPosition((x*15+7,y*15+pathPos,0)))
                    y = y-1
                elif direction == "south":
                    for pathPos in range(8,23):
                        items.extend(terrain.getItemByPosition((x*15+7,y*15+pathPos,0)))
                    y = y+1

                last = (x,y)

                while self in items:
                    items.remove(self)
                terrain.removeItems(items)

                if x == 7 and y == 7:
                    break

                if (x,y) in roomSlots:
                    note = src.items.itemMap["Note"]()
                    note.text = random.choice([
                        f"The the reserve city core is on coordinate {targetRoomSlot[0]}/{targetRoomSlot[1]}",
                        f"The the reserve city core is on coordinate {targetRoomSlot[0]}/{targetRoomSlot[1]}",
                        f"The memorycell production is on coordinate {memoryCellRoom[0]}/{memoryCellRoom[1]}",
                        f"The pocketframe production is on coordinate {pocketFrameRoom[0]}/{pocketFrameRoom[1]}",
                        ])
                    terrain.addItem(note,(x*15+7,y*15+7,0))
                    break
                if (x,y) in pathSlots:
                    if not (x,y) in crossroads:
                        crossroads.append((x,y))
                    else:
                        break

                    if not (abs(x-7) > 2 or abs(y-7) > 2):
                        break

                    if random.choice([True,False]):
                        enemy = src.characters.Monster(x*15+7, y*15+7)
                        enemy.health = 10 + random.randint(1, 100)
                        enemy.baseDamage = random.randint(1, 10)
                        enemy.godMode = True
                        enemy.aggro = 1000000
                        terrain.addCharacter(enemy, x*15+7, y*15+7)
                    break

                pathSlots.append((x,y))
                connectedRooms.append((x,y))

        oldCityCore = src.items.itemMap["BrokenCityBuilder"]()
        terrain.addItem(oldCityCore,(7*15+7,7*15+7,0))

        # set up target room
        targetItem = src.items.itemMap["ReserveCityBuilder"]()
        targetRoom = self.doAddRoom(
                {
                    "coordinate": targetRoomSlot,
                    "roomType": "EmptyRoom",
                    "doors": "0,6 6,0 12,6 6,12",
                    "offset": [1,1],
                    "size": [13, 13],
                },
                None,
                )
        for _i in range(random.randint(0,10)):
            targetRoom.damage()
        for _i in range(random.randint(50,60)):
            pos = (random.randint(1,11),random.randint(1,11),0)
            if pos == (6,6,0):
                continue

            if targetRoom.getItemByPosition(pos):
                continue

            loot = None
            if random.choice([True,True,True,False]):
                if random.choice([True,False]):
                    loot = src.items.itemMap[random.choice(["Armor","Rod"])]()
                    targetRoom.addItem(loot,pos)
                    loot.bolted = False
                elif random.choice([True,False]):
                    loot = src.items.itemMap[random.choice(["Bolt"])]()
                    targetRoom.addItem(loot,pos)
                    loot.bolted = False
                else:
                    loot = src.items.itemMap[random.choice(src.items.commons)]()
                    if loot.type == "Vial":
                        loot.uses = random.randint(1,4)
                    if loot.type == "GooFlask":
                        loot.uses = random.randint(1,100)
                    loot.bolted = False
                    if not loot.walkable:
                        loot = src.items.itemMap[random.choice(["Bolt","Bolt","Rod"])]()
                    targetRoom.addItem(loot,pos)

            amount = random.randint(1,15)
            if pos[0] == 6 or pos[1] == 6 or abs(pos[0]-6)+abs(pos[1]-6) < 2:
                amount = random.randint(1,4)
            scrap = src.items.itemMap["Scrap"](amount=amount)
            targetRoom.addItem(scrap,pos)
        targetRoom.addItem(targetItem,(6,6,0))

        memoryCellMachine = src.items.itemMap["Machine"]()
        memoryCellMachine.setToProduce("MemoryCell")
        terrain.addItem(memoryCellMachine,(memoryCellRoom[0]*15+7,memoryCellRoom[1]*15+7,0))

        pocketFrameMachine = src.items.itemMap["Machine"]()
        pocketFrameMachine.setToProduce("PocketFrame")
        terrain.addItem(pocketFrameMachine,(pocketFrameRoom[0]*15+7,pocketFrameRoom[1]*15+7,0))

        # insert theme rooms
        numRuns = 0
        ensuredConnectorMachine = False
        ensuredPocketFrameMachine = False

        roomMap[7][7] = "CB"

        for slot in pathSlots:
            roomMap[slot[1]][slot[0]] = "++"

        for roomSlot in freeRoomSlots[:]:
            if random.choice([True,True,True,False]):
                continue

            room = None

            numRuns += 1

            freeRoomSlots.remove(roomSlot)

            theme = random.choice(["machine","food","military","stockpile","stockpile"])

            if numRuns == 1:
                theme = "machine"
            if numRuns == 2:
                theme = "food"
            if numRuns == 4:
                theme = "machine"
            if numRuns == 5:
                theme = "food"


            if theme == "machine":
                """
                room = self.doAddRoom(
                        {
                            "coordinate": roomSlot,
                            "roomType": "EmptyRoom",
                            "doors": "0,6 6,0 12,6 6,12",
                            "offset": [1,1],
                            "size": [13, 13],
                        },
                        None,
                )
                for i in range(0,random.randint(20,30)):
                    room.damage()
                """

                for _i in range(random.randint(4,8)):
                    machine = src.items.itemMap["Machine"]()
                    toProduceType = random.choice(["Rod","Rod","Vial","Rod","Heater","puller","Stripe","Bolt","Case","Tank","Armor","GooFlask","MemoryCell","Connector","PocketFrame"])
                    if not ensuredConnectorMachine:
                        toProduceType = "Connector"
                        ensuredConnectorMachine = True
                    elif not ensuredPocketFrameMachine:
                        toProduceType = "PocketFrame"
                        ensuredPocketFrameMachine = True
                    machine.setToProduce(toProduceType)
                    #room.addItem(machine,(random.randint(2,10),random.randint(2,10),0))
                    terrain.addItem(machine,(roomSlot[0]*15+random.randint(2,11),roomSlot[1]*15+random.randint(2,11),0))
                for _i in range(random.randint(0,10)):
                    gooFlask = src.items.itemMap[random.choice(["MetalBars","Rod","Rod","Vial","Rod","Heater","puller","Stripe","Bolt","Case","Tank","Mount"])]()
                    #room.addItem(gooFlask,(random.randint(2,10),random.randint(2,10),0))
                    terrain.addItem(gooFlask,(roomSlot[0]*15+random.randint(2,11),roomSlot[1]*15+random.randint(2,11),0))
                roomMap[roomSlot[1]][roomSlot[0]] = "mm"


            if theme == "food":
                """
                room = self.doAddRoom(
                        {
                            "coordinate": roomSlot,
                            "roomType": "EmptyRoom",
                            "doors": "0,6 6,0 12,6 6,12",
                            "offset": [1,1],
                            "size": [13, 13],
                        },
                        None,
                )
                for i in range(0,random.randint(20,30)):
                    room.damage()
                """

                for _i in range(random.randint(4,10)):
                    machine = src.items.itemMap[random.choice(["CorpseShredder","MaggotFermenter","SporeExtractor","GooDispenser","BioPress","BloomShredder"])]()
                    if machine.type == "GooDispenser":
                        machine.charges = random.randint(0,3)
                    #room.addItem(machine,(random.randint(2,10),random.randint(2,10),0))
                    terrain.addItem(machine,(roomSlot[0]*15+random.randint(1,11),roomSlot[1]*15+random.randint(1,11),0))

                for _i in range(random.randint(0,4)):
                    gooFlask = src.items.itemMap["GooFlask"]()
                    gooFlask.uses = random.choice([0,0,1,2,3,5,7,8,25,45,100])
                    #room.addItem(gooFlask,(random.randint(2,10),random.randint(2,10),0))
                    terrain.addItem(gooFlask,(roomSlot[0]*15+random.randint(1,11),roomSlot[1]*15+random.randint(1,11),0))
                roomMap[roomSlot[1]][roomSlot[0]] = "FF"

            if theme == "military":
                for _i in range(random.randint(4,20)):
                    bomb = src.items.itemMap["Bomb"]()
                    terrain.addItem(bomb,(roomSlot[0]*15+random.randint(1,13),roomSlot[1]*15+random.randint(1,13),0))

                enemy = src.characters.Monster(x, y)
                enemy.health = 10 + random.randint(1, 1000)
                enemy.baseDamage = random.randint(1, 100)
                enemy.godMode = True
                enemy.aggro = 1000000
                enemy.faction = "animals"
                terrain.addCharacter(enemy, roomSlot[0]*15+7, roomSlot[1]*15+7)
                roomMap[roomSlot[1]][roomSlot[0]] = "MM"

            if theme == "stockpile":
                manager = src.items.itemMap["UniformStockpileManager"]()
                terrain.addItem(manager,(roomSlot[0]*15+7,roomSlot[1]*15+7,0))

                itemType = random.choice(src.items.commons)
                for _i in range(random.randint(4,20)):
                    bomb = src.items.itemMap[itemType]()
                    terrain.addItem(bomb,(roomSlot[0]*15+random.randint(1,13),roomSlot[1]*15+random.randint(1,13),0))

                roomMap[roomSlot[1]][roomSlot[0]] = "ss"

            for _i in range(random.randint(0,5)):
                enemy = src.characters.Monster(x, y)
                enemy.health = 10 + random.randint(1, 100)
                enemy.baseDamage = random.randint(1, 5)
                enemy.godMode = True
                enemy.aggro = 1000000
                enemy.faction = "animals"

                if not room:
                    terrain.addCharacter(enemy, roomSlot[0]*15+random.randint(1,13), roomSlot[1]*15+random.randint(1,13))

            if not terrain.getItemByPosition((roomSlot[0]*15+7,roomSlot[1]*15+7,0)):
                note = src.items.itemMap["Note"]()
                note.text = random.choice([
                    f"The the reserve city core is on coordinate {targetRoomSlot[0]}/{targetRoomSlot[1]}",
                    f"The the reserve city core is on coordinate {targetRoomSlot[0]}/{targetRoomSlot[1]}",
                    f"The memorycell production is on coordinate {memoryCellRoom[0]}/{memoryCellRoom[1]}",
                    f"The pocketframe production is on coordinate {pocketFrameRoom[0]}/{pocketFrameRoom[1]}",
                    ])
                terrain.addItem(note,(roomSlot[0]*15+7,roomSlot[1]*15+7,0))

        ensuredMountDrop = False

        # fill up remaining rooms
        """
        for roomSlot in freeRoomSlots:
            room = self.doAddRoom(
                    {
                        "coordinate": roomSlot,
                        "roomType": "EmptyRoom",
                        "doors": "0,6 6,0 12,6 6,12",
                        "offset": [1,1],
                        "size": [13, 13],
                    },
                    None,
            )
            for i in range(2,8):
                room.damage()

            roomMap[roomSlot[1]][roomSlot[0]] = "rr"

        for roomSlot in pathSlots:
            if roomSlot in crossroads:
                continue
        """

        for roomSlot in freeRoomSlots:
            roomMap[roomSlot[1]][roomSlot[0]] = "rr"

            self.doClearField(roomSlot[0],roomSlot[1])
            distance = abs(roomSlot[0]-7)+abs(roomSlot[1]-7)

            for _i in range(random.randint(0,distance)):
                lootType = random.choice(["Frame","Mount","FireCrystals","FireCrystals","Rod","Rod","Vial","Vial","Rod","Heater","puller","Stripe","Bolt","Bolt","Case","Tank","Armor","GooFlask"])
                if not ensuredMountDrop:
                    lootType = "Mount"
                    ensuredMountDrop = True
                loot = src.items.itemMap[lootType]()
                loot.bolted = False
                terrain.addItem(loot,(roomSlot[0]*15+random.randint(1,13),roomSlot[1]*15+random.randint(1,13),0))

                if loot.type == "Vial":
                    loot.uses = distance//3+1
                if loot.type == "Rod":
                    loot.baseDamage = distance+random.randint(0,3)
                if loot.type == "Armor":
                    loot.armorValue = distance//3+random.randint(0,1)+1
                if loot.type == "GooFlask":
                    loot.uses = min(distance+random.randint(0,100),100)

            numScrap = random.randint(0,50)
            #numScrap += random.choice((0,0,10,40,100))
            for _i in range(numScrap):
                pos = (random.randint(1,13),random.randint(1,13))
                if not pos in ((7,1),(1,7),(13,7),(7,13)) and not terrain.getItemByPosition((roomSlot[0]*15+pos[0],roomSlot[1]*15+pos[1],0)):
                    if random.randint(0,3) == 1:
                        loot = src.items.itemMap[random.choice(["MetalBars","Rod","Frame"]+src.items.commons)]()
                        loot.bolted = False
                        if loot.walkable:
                            terrain.addItem(loot,(roomSlot[0]*15+pos[0],roomSlot[1]*15+pos[1],0))
                        loot.bolted = False
                    scrap = src.items.itemMap["Scrap"](amount=random.randint(1,30))
                    terrain.addItem(scrap,(roomSlot[0]*15+pos[0],roomSlot[1]*15+pos[1],0))

            for _i in range(random.randint(0,14)):
                pos = (random.randint(1,13),random.randint(1,13))
                if not pos in ((7,1),(1,7),(13,7),(7,13)) and not terrain.getItemByPosition((roomSlot[0]*15+pos[0],roomSlot[1]*15+pos[1],0)):
                    mold = src.items.itemMap["Mold"]()
                    terrain.addItem(mold,(roomSlot[0]*15+pos[0],roomSlot[1]*15+pos[1],0))
                    mold.startSpawn()
            for _i in range(random.randint(0,2)):
                enemy = src.characters.Monster(x, y)
                enemy.health = 10 + random.randint(1, distance*10)
                enemy.baseDamage = random.randint(1, distance)
                enemy.godMode = True
                enemy.aggro = 1000000
                enemy.faction = "animals"

                terrain.addCharacter(enemy, roomSlot[0]*15+random.randint(1,13), roomSlot[1]*15+random.randint(1,13))

        text = ""

        for row in roomMap:
            text += "".join(row)+"\n"

        targetItem.mapString = text

    def fillMap(self):
        """
        fill the whole map
        """

        terrain = self.getTerrain()

        for bigX in range(1,14):
            for bigY in range(1, 14):
                for x in range(1,14):
                    for y in range(1,14):
                        if bigX*15+x == self.xPosition and bigY*15+y == self.yPosition:
                            continue
                        item = src.items.itemMap["Scrap"](amount=random.randint(0,20))
                        terrain.addItem(item,(bigX*15+x,bigY*15+y,0))


    def apply2(self):
        """
        handle a character having selected an action
        by running the action
        """

        if self.submenue.selection == "addRemnant":
            self.addRemants(self.character)
        if self.submenue.selection == "generate maze":
            self.generateMaze()
        if self.submenue.selection == "fill map":
            self.fillMap()
        if self.submenue.selection == "test":
            self.test()
        if self.submenue.selection == "shapeTerrain":
            terrain = self.getTerrain()
            for _i in range(1, 10):
                self.doAddScrapfield(
                    random.randint(1, 13),
                    random.randint(1, 13),
                    random.randint(200, 400),
                )
            for _i in range(1, 30):
                self.doAddScrapfield(
                    random.randint(1, 13), random.randint(1, 13), random.randint(20, 40)
                )
            for _i in range(1, 5):
                item = src.items.itemMap["Rod"]()
                item.baseDamage = i
                itemPos = (
                    random.randint(1, 13) * 15 + random.randint(1, 13),
                    random.randint(1, 13) * 15 + random.randint(1, 13),
                    0,
                )
                terrain.addItem(item, itemPos)
            for _i in range(1, 5):
                item = src.items.itemMap["Armor"]()
                item.armorValue = i
                itemPos = (
                    random.randint(1, 13) * 15 + random.randint(1, 13),
                    random.randint(1, 13) * 15 + random.randint(1, 13),
                    0,
                )
                terrain.addItem(item, itemPos)
            """
            for i in range(1,20):
                enemy = src.characters.Monster()
                terrain.addCharacter(enemy,random.randint(1,13)*15+random.randint(1,13),random.randint(1,13)*15+random.randint(1,13))
                enemy.godMode = True
            for i in range(1,5):
                enemy = src.characters.Exploder()
                terrain.addCharacter(enemy,random.randint(1,13)*15+random.randint(1,13),random.randint(1,13)*15+random.randint(1,13))
                enemy.godMode = True
            for i in range(1,5):
                enemy = src.characters.Character()
                enemy.faction = "enemy"
                terrain.addCharacter(enemy,random.randint(1,13)*15+random.randint(1,13),random.randint(1,13)*15+random.randint(1,13))
                enemy.godMode = True
            """
            for _i in range(1, 2):
                item = src.items.itemMap["GooFlask"]()
                item.uses = 100
                itemPos = (
                    random.randint(1, 13) * 15 + random.randint(1, 13),
                    random.randint(1, 13) * 15 + random.randint(1, 13),
                    0,
                )
                terrain.addItem(item, itemPos)
            for _i in range(1, 30):
                item = src.items.itemMap["Mold"]()
                itemPos = (
                    random.randint(1, 13) * 15 + random.randint(1, 13),
                    random.randint(1, 13) * 15 + random.randint(1, 13),
                    0,
                )
                terrain.addItem(item, itemPos)
                item.startSpawn()
        if self.submenue.selection == "showMap":
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

            for (
                coordinate,
                rooms,
            ) in self.getTerrain().roomByCoordinates.items():
                if not rooms:
                    continue
                mapContent[coordinate[1]][coordinate[0]] = "RR"

            mapText = ""
            for x in range(15):
                mapText += "".join(mapContent[x]) + "\n"
            self.submenue = src.interaction.TextMenu(text=mapText)
            self.character.macroState["submenue"] = self.submenue
        elif self.submenue.selection == "addScrapField":
            self.submenue = None
            self.addScrapField(wipe=True)
        elif self.submenue.selection == "addRoom":
            self.submenue = None
            self.addRoom(wipe=True)
        elif self.submenue.selection == "clearField":
            self.submenue = None
            self.clearField(wipe=True)

    def clearField(self, wipe=False):
        """
        handle a character trying to clear a field

        Parameters:
            wipe: flag to rerequest settings
        """

        if not self.submenue:
            self.submenue = src.interaction.InputMenu(
                f"enter the coordinate ( x,y ) current: {self.character.xPosition // 15},{self.character.yPosition // 15}"
            )
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.clearField
            return

        targetX = int(self.submenue.text.split(",")[0])
        targetY = int(self.submenue.text.split(",")[1])

        self.doClearField(targetX, targetY)

    def doClearField(self, x, y):
        """
        remove all item from a big coordinate

        Parameters:
            x: the big x position
            y: the big y position
        """

        terrain = self.getTerrain()

        minX = 15 * x
        minY = 15 * y
        maxX = minX + 15
        maxY = minY + 15
        toRemove = []
        for x in range(minX, maxX):
            for y in range(minY, maxY):
                toRemove.extend(terrain.getItemByPosition((x, y, 0)))
        if self in toRemove:
            toRemove.remove(self)
        terrain.removeItems(toRemove)

        if (x, y) in terrain.roomByCoordinates:
            for room in terrain.roomByCoordinates[(x, y)]:
                terrain.removeRoom(room)

    def addScrapField(self, wipe=False):
        """
        handle a character trying to add a scrap field

        Parameters:
            wipe: flag to rerequest settings
        """

        if wipe:
            self.targetX = None
            self.targetY = None
            self.targetAmount = None

        if not self.submenue:
            self.submenue = src.interaction.InputMenu(
                f"enter the coordinate ( x,y ) current: {self.character.xPosition // 15},{self.character.yPosition // 15}"
            )
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.addScrapField
            return

        if not self.targetY:
            self.targetX = int(self.submenue.text.split(",")[0])
            self.targetY = int(self.submenue.text.split(",")[1])

            self.submenue = src.interaction.InputMenu(
                "enter the amount of scrap piles (AMOUNt)"
            )
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.addScrapField
            return

        amount = int(self.submenue.text)

        terrain = self.getTerrain()

        if not terrain:
            self.character.addMessage("no terrain found")
            return

        self.doAddScrapfield(self.targetX, self.targetY, amount)

    def doAddMinefield(self, x, y, amount):
        terrain = self.getTerrain()

        counter = 0
        minX = 15 * x
        minY = 15 * y
        maxX = minX + 13
        maxY = minY + 13
        maxItems = amount
        maxItems = amount
        items = []
        while counter < maxItems:
            itemPair = (
                    src.items.itemMap["LandMine"](),
                    (random.randint(minX, maxX), random.randint(minY, maxY), 0),
                )
            items.append(itemPair)
            counter += 1

        terrain.addItems(items)

    def doFillWith(self, x, y, itemTypes):

        terrain = self.getTerrain()
        for smallX in range(1,14):
            for smallY in range(1,14):
                pos = (x*15+smallX,y*15+smallY,0)
                if terrain.getItemByPosition(pos):
                    continue

                itemType = random.choice(itemTypes)
                terrain.addItem(src.items.itemMap[itemType](),pos)

    def doSpawnItems(self, x, y, itemTypes, amount, repeat=1):
        terrain = self.getTerrain()
        for _i in range(amount):
            selectedPos = None
            for _j in range(repeat):
                pos = (x*15+random.randint(1,13),y*15+random.randint(1,13),0)
                if terrain.getItemByPosition(pos):
                    continue
                selectedPos = pos
                break

            if not selectedPos:
                continue

            itemType = random.choice(itemTypes)
            terrain.addItem(src.items.itemMap[itemType](),selectedPos)

    def doAddScrapfield(self, x, y, amount, leavePath=False):
        """
        spawn a scrap field to a big coordinate
        (god mode)

        Parameters:
            x: the big x position
            y: the big y position
        """

        terrain = self.getTerrain()
        terrain.scrapFields.append((x,y,0))

        counter = 0
        minX = 15 * x + 1
        minY = 15 * y + 1
        maxX = minX + 12
        maxY = minY + 12
        maxItems = amount
        items = []
        while counter < maxItems:
            xPos = random.randint(minX, maxX)
            yPos = random.randint(minY, maxY)
            pos = (xPos,yPos,0)

            if (leavePath and (xPos%15 == 7 or yPos%15 == 7)):
                continue

            if random.randint(1, 15) != 10:
                itemPair = (src.items.itemMap["Scrap"](amount=random.randint(1, 20)), pos, )
            else:
                if random.randint(1, 10) != 2:
                    itemPair = (src.items.itemMap[random.choice(src.items.commons)](), pos, )
                else:
                    itemPair = (src.items.itemMap[random.choice(src.items.semiCommons)](), pos, )

                item = itemPair[0]
                item.bolted = False
                if item.type == "Machine":
                    if random.randint(1, 10) != 2:
                        item.setToProduce(random.choice(src.items.commons))
                    else:
                        item.setToProduce(random.choice(src.items.semiCommons))
                if item.type == "HealingStation":
                    item.charges = random.randint(0, 10)

            items.append(itemPair)
            counter += 1

        terrain.addItems(items)

    def addRoom(self, wipe=False):
        """
        handle a character trying to add a room

        Parameters:
            wipe: flag to rerequest settings
        """

        if wipe:
            self.targetX = None
            self.targetY = None
            self.targetOffsetX = None
            self.targetOffsetY = None
            self.targetRoomType = None

        if not self.submenue:
            self.submenue = src.interaction.InputMenu(
                f"enter the coordinate ( x,y ) current: {self.character.xPosition // 15},{self.character.yPosition // 15}"
            )
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.addRoom
            return

        if not self.targetY:
            self.targetX = int(self.submenue.text.split(",")[0])
            self.targetY = int(self.submenue.text.split(",")[1])

            self.submenue = src.interaction.InputMenu("enter the offset ( x,y )")
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.addRoom
            return

        if not self.targetOffsetY:
            self.targetOffsetX = int(self.submenue.text.split(",")[0])
            self.targetOffsetY = int(self.submenue.text.split(",")[1])

            options = []
            for key, _value in src.rooms.roomMap.items():
                options.append((key, key))
            self.submenue = src.interaction.SelectionMenu(
                "select the room to produce", options
            )
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.addRoom
            return

        if not self.targetRoomType:
            self.targetRoomType = self.submenue.selection
            if self.targetRoomType == "EmptyRoom":
                self.emptyRoomSizeX = None
                self.emptyRoomSizeY = None
                self.entryPointX = None
                self.entryPointY = None

                self.submenue = src.interaction.InputMenu(
                    "enter the rooms size ( x,y )"
                )
                self.character.macroState["submenue"] = self.submenue
                self.character.macroState["submenue"].followUp = self.addRoom
                return

        if self.targetRoomType == "EmptyRoom" and not self.emptyRoomSizeY:
            self.emptyRoomSizeX = int(self.submenue.text.split(",")[0])
            self.emptyRoomSizeY = int(self.submenue.text.split(",")[1])

            self.submenue = src.interaction.InputMenu(
                "enter the doors positions ( x,y x,y x,y )"
            )
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.addRoom
            return

        self.doAddRoom(
            {
                "doors": self.submenue.text,
                "size": [self.emptyRoomSizeX, self.emptyRoomSizeY],
                "coordinate": [self.targetX, self.targetY],
                "offset": [self.targetOffsetX, self.targetOffsetY],
                "roomType": self.targetRoomType,
            },
            {"character": self.character},
        )

    def doAddRoom(self, task, context):
        """
        add a room

        Parameters:
            task: details about this task
            context: the context for this task
        """

        room = src.rooms.roomMap[task["roomType"]](
            task["coordinate"][0],
            task["coordinate"][1],
            task["offset"][0],
            task["offset"][1],
        )
        if task["roomType"] in ("EmptyRoom","TrapRoom","WorkshopRoom","ComandCenter","StorageRoom","TeleporterRoom","TempleRoom"):
            entryPoints = []
            for part in task["doors"].split(" "):
                entryPointX = int(part.split(",")[0])
                entryPointY = int(part.split(",")[1])
                entryPoint = (
                    entryPointX,
                    entryPointY,
                )

                entryPoints.append(entryPoint)

            if context:
                context["character"].addMessage(entryPoints)

            room.reconfigure(task["size"][0], task["size"][1], doorPos=entryPoints)

        faction = task.get("faction")
        if faction:
            room.faction = faction

        terrain = self.getTerrain()

        if not terrain:
            if context:
                context["character"].addMessage("no terrain found")
            return

        terrain.addRooms([room])
        return room

src.items.addType(ArchitectArtwork)

import json
import random

import src

def SpawnStorageRoom(terrain, coordinate, controlRoom, teleporter_group):
    '''
    spawn storage room
    '''
    room = spawnRoomFromFloorPlan(terrain, coordinate, "storage1.json")
    pos = room.getPosition()

    controlRoom.storageRooms.append(room)

    for otherRoom in terrain.rooms:
        otherRoom.sources.insert(0, (pos, "Corpse"))
        otherRoom.sources.insert(0, (pos, "Scrap"))
        otherRoom.sources.insert(0, (pos, "Sheet"))
        otherRoom.sources.insert(0, (pos, "Frame"))
        otherRoom.sources.insert(0, (pos, "ScrapCompactor"))
        otherRoom.sources.insert(0, (pos, "Rod"))
        otherRoom.sources.insert(0, (pos, "Armor"))
        otherRoom.sources.insert(0, (pos, "MetalBars"))
        otherRoom.sources.insert(0, (pos, "Sword"))
        otherRoom.sources.insert(0, (pos, "Painter"))
        otherRoom.sources.insert(0, (pos, "ScratchPlate"))
        otherRoom.sources.insert(0, (pos, "CorpseAnimator"))
        otherRoom.sources.insert(0, (pos, "LightningRod"))

    teleporter = src.items.itemMap["DimensionTeleporter"]()
    teleporter.group = teleporter_group
    teleporter.mode = random.choice([0, 1])
    teleporter.boltAction(None)
    room.addItem(teleporter, (1, 1, 0))


def spawnRoomFromFloorPlan(terrain, coordinate, floorplan):
    '''
    spawn room based on a floor plan
    '''
    room = spawnRoom(terrain, "EmptyRoom", coordinate)
    with open("data/floorPlans/" + floorplan) as fileHandle:
        rawFloorplan = json.load(fileHandle)
        room.floorPlan = getFloorPlanFromDict(rawFloorplan)
    room.spawnPlaned()
    room.spawnPlaned()
    return room


def getFloorPlanFromDict(rawFloorplan):
    '''
    create floor plan from dictionary
    '''
    converted = {}
    if "buildSites" in rawFloorplan:
        buildSites = []
        for item in rawFloorplan["buildSites"]:
            buildSites.append((tuple(item[0]), item[1], item[2]))
        converted["buildSites"] = buildSites
    if "inputSlots" in rawFloorplan:
        inputSlots = []
        for item in rawFloorplan["inputSlots"]:
            inputSlots.append((tuple(item[0]), item[1], item[2]))
        converted["inputSlots"] = inputSlots
    if "outputSlots" in rawFloorplan:
        outputSlots = []
        for item in rawFloorplan["outputSlots"]:
            outputSlots.append((tuple(item[0]), item[1], item[2]))
        converted["outputSlots"] = outputSlots
    if "storageSlots" in rawFloorplan:
        outputSlots = []
        for item in rawFloorplan["storageSlots"]:
            outputSlots.append((tuple(item[0]), item[1], item[2]))
        converted["storageSlots"] = outputSlots
    if "walkingSpace" in rawFloorplan:
        walkingSpace = []
        for item in rawFloorplan["walkingSpace"]:
            walkingSpace.append(tuple(item))
        converted["walkingSpace"] = walkingSpace
    return converted

def convertFloorPlanToDict(self, floorPlan):
    '''
    convert floor plan to dictionary
    '''
    converted = {}
    if "buildSites" in floorPlan:
        buildSites = []
        for item in floorPlan["buildSites"]:
            buildSites.append([list(item[0]), item[1], item[2]])
        converted["buildSites"] = buildSites
    if "inputSlots" in floorPlan:
        inputSlots = []
        for item in floorPlan["inputSlots"]:
            inputSlots.append([list(item[0]), item[1], item[2]])
        converted["inputSlots"] = inputSlots
    if "outputSlots" in floorPlan:
        outputSlots = []
        for item in floorPlan["outputSlots"]:
            outputSlots.append([list(item[0]), item[1], item[2]])
        converted["outputSlots"] = outputSlots
    if "storageSlots" in floorPlan:
        outputSlots = []
        for item in floorPlan["storageSlots"]:
            outputSlots.append([list(item[0]), item[1], item[2]])
        converted["storageSlots"] = outputSlots
    if "walkingSpace" in floorPlan:
        walkingSpace = []
        for item in floorPlan["walkingSpace"]:
            walkingSpace.append(list(item))
        converted["walkingSpace"] = walkingSpace
    return converted


def spawnScrapField(terrain, coordinate):
    '''
    spawn a scrap field
    '''
    bigX, bigY = coordinate
    for x in range(1, 14):
        for y in range(1, 14):
            amount = random.randint(1, 10)
            if x in (
                1,
                13,
            ) or y in (
                1,
                13,
            ):
                amount = random.randint(8, 15)
            scrap = src.items.itemMap["Scrap"](amount=amount)
            terrain.addItem(scrap, (bigX * 15 + x, bigY * 15 + y, 0))
    terrain.scrapFields.append((bigX, bigY, 0))

def spawnTrapRoom(terrain, coordinate, faction, doors="0,6 6,0 6,12 12,6"):
    '''
    spawn a trap room
    '''
    trapRoom2 = spawnRoom(terrain, "EmptyRoom", coordinate, doors)

    trapRoom2.tag = "traproom"

    # add walking space in the center
    trapRoom2.addWalkingSpace((6, 6, 0))

    # add north-south trap line
    for y in (1, 2, 3, 4, 5, 7, 8, 9, 10, 11):
        triggerPlate = src.items.itemMap["TriggerPlate"]()
        triggerPlate.faction = faction
        triggerPlate.bolted = True
        trapRoom2.addItem(triggerPlate, (6, y, 0))
        trapRoom2.addWalkingSpace((6, y, 0))
        for x in (5, 7):
            rodTower = src.items.itemMap["RodTower"]()
            trapRoom2.addItem(rodTower, (x, y, 0))
            triggerPlate.targets.append((x, y, 0))

    # add west-east trap line
    for x in (1, 2, 3, 4, 5, 7, 8, 9, 10):
        triggerPlate = src.items.itemMap["TriggerPlate"]()
        triggerPlate.faction = faction
        triggerPlate.bolted = True
        trapRoom2.addItem(triggerPlate, (x, 6, 0))
        trapRoom2.addWalkingSpace((x, 6, 0))
        for y in (5, 7):
            if x not in (
                5,
                7,
            ):
                rodTower = src.items.itemMap["RodTower"]()
                trapRoom2.addItem(rodTower, (x, y, 0))
            triggerPlate.targets.append((x, y, 0))
    trapRoom2.addWalkingSpace((11, 6, 0))

    # add alarm bell
    alarmBell = src.items.itemMap["AlarmBell"]()
    alarmBell.bolted = True
    trapRoom2.addItem(alarmBell, (11, 7, 0))

    alarmBell = src.items.itemMap["Wall"]()
    alarmBell.bolted = True
    trapRoom2.addItem(alarmBell, (11, 5, 0))

    # block some of the trap
    for pos in ((1, 6, 0), (2, 6, 0), (6, 1, 0), (6, 2, 0), (6, 11, 0), (6, 10, 0)):
        moldFeed = src.items.itemMap["MoldFeed"]()
        trapRoom2.addItem(moldFeed, pos)


def spawnArenaRoom(terrain, coordinate, difficulty, doors="0,6 6,0 6,12 12,6"):
    '''
    generates an arena room
    '''
    trapRoom1 = spawnRoom(terrain, "EmptyRoom", coordinate, doors)
    trapRoom1.tag = "arena"

    sword = src.items.itemMap["Sword"]()
    sword.baseDamage = 15
    if difficulty == "easy":
        sword.baseDamage = 18
    if difficulty == "difficult":
        sword.baseDamage = 10
    sword.bolted = False
    trapRoom1.addItem(sword, (11, 3, 0))
    sword = src.items.itemMap["Sword"]()
    sword.baseDamage = 15
    if difficulty == "easy":
        sword.baseDamage = 18
    if difficulty == "difficult":
        sword.baseDamage = 10
    sword.bolted = False
    trapRoom1.addItem(sword, (11, 3, 0))
    trapRoom1.addStorageSlot((11, 3, 0), "Sword")

    armor = src.items.itemMap["Armor"]()
    armor.armorValue = 3
    if difficulty == "easy":
        armor.armorValue = 5
    if difficulty == "difficult":
        armor.armorValue = 1
    armor.bolted = False
    trapRoom1.addItem(armor, (11, 4, 0))
    armor = src.items.itemMap["Armor"]()
    armor.armorValue = 3
    if difficulty == "easy":
        armor.armorValue = 5
    if difficulty == "difficult":
        armor.armorValue = 1
    armor.bolted = False
    trapRoom1.addItem(armor, (11, 4, 0))
    trapRoom1.addStorageSlot((11, 4, 0), "Armor")

    for x in range(4, 12):
        for i in range(10):
            bloom = src.items.itemMap["Bloom"]()
            bloom.dead = True
            trapRoom1.addItem(bloom, (x, 1, 0))

    coalBurner = src.items.itemMap["CoalBurner"]()
    coalBurner.bolted = True
    trapRoom1.addItem(coalBurner, (11, 8, 0))

    swordSharpener = src.items.itemMap["SwordSharpener"]()
    swordSharpener.bolted = True
    trapRoom1.addItem(swordSharpener, (11, 5, 0))

    armorReinforcer = src.items.itemMap["ArmorReinforcer"]()
    armorReinforcer.bolted = True
    trapRoom1.addItem(armorReinforcer, (11, 7, 0))

    trapRoom1.addInputSlot((11, 9, 0), "MoldFeed", {})
    moldFeed = src.items.itemMap["MoldFeed"]()
    trapRoom1.addItem(moldFeed, (11, 9, 0))
    moldFeed = src.items.itemMap["MoldFeed"]()
    trapRoom1.addItem(moldFeed, (11, 9, 0))
    moldFeed = src.items.itemMap["MoldFeed"]()
    trapRoom1.addItem(moldFeed, (11, 9, 0))
    moldFeed = src.items.itemMap["MoldFeed"]()
    trapRoom1.addItem(moldFeed, (11, 9, 0))
    moldFeed = src.items.itemMap["MoldFeed"]()
    trapRoom1.addItem(moldFeed, (11, 9, 0))
    moldFeed = src.items.itemMap["MoldFeed"]()
    trapRoom1.addItem(moldFeed, (11, 9, 0))
    moldFeed = src.items.itemMap["MoldFeed"]()
    trapRoom1.addItem(moldFeed, (11, 9, 0))

    for x in range(1, 12):
        for y in range(2, 11):
            if (x, y) in ((11, 9), (11, 8), (11, 5), (11, 7), (11, 4), (11, 3)):
                continue
            trapRoom1.walkingSpace.add((x, y, 0))

    # added ghoul automation for harvesting
    corpseAnimator = src.items.itemMap["CorpseAnimator"]()
    corpseAnimator.bolted = True
    trapRoom1.addItem(corpseAnimator, (2, 1, 0))
    command = src.items.itemMap["Command"]()
    command.bolted = True
    command.command = ""
    command.command += "5s5a6a"  # move to traproom center
    command.command += "14sj"  # activate field
    command.command += "13sj"  # activate field
    command.command += "13aj"  # activate field
    command.command += "13wj"  # activate field
    command.command += "13wj"  # activate field
    command.command += "13d"  # move to traproom center
    command.command += "11d5w"  # move to traproom center
    command.command += "s" + "dLw" * 8  # fill output stockpiles
    command.command += "8aw"  # return to start position
    command.repeat = True
    trapRoom1.addItem(command, (3, 1, 0))
    trapRoom1.addInputSlot((1, 1, 0), "Corpse")
    for x in range(4, 12):
        trapRoom1.addOutputSlot((x, 1, 0), None)

    # added ghoul automation for trap room clearing
    corpseAnimator = src.items.itemMap["CorpseAnimator"]()
    corpseAnimator.bolted = True
    trapRoom1.addItem(corpseAnimator, (2, 11, 0))
    command = src.items.itemMap["Command"]()
    command.bolted = True
    command.command = ""
    command.command += "5w5a6a"  # move to traproom center
    command.command += "Kdd" * 5 + "5a"  # clear east line
    command.command += "Kaa" * 5 + "5d"  # clear west line
    command.command += "Kss" * 5 + "5w"  # clear south line
    command.command += "Kww" * 5 + "5s"  # clear north line
    command.command += "6d" + "5d5s"  # return to start position
    command.command += "w" + "dLs" * 8  # fill output stockpiles
    command.command += "8as"  # return to start position
    command.command += "100."  # wait
    command.repeat = True
    trapRoom1.addItem(command, (3, 11, 0))
    trapRoom1.addInputSlot((1, 11, 0), "Corpse")
    for x in range(4, 12):
        trapRoom1.addOutputSlot((x, 11, 0), None)


def spawnTempleRoom(terrain, coordinate, faction, doors="0,6 6,0 6,12 12,6"):
    '''
    spawn a temple
    '''
    throneRoom = spawnRoom(terrain, "EmptyRoom", coordinate, doors)
    throneRoom.tag = "temple"
    for item in throneRoom.itemsOnFloor:
        if item.type != "Door":
            continue
        if item.getPosition() == (6, 12, 0):
            continue
        item.walkable = False
    throneRoom.priority = 5

    for x in (
        2,
        10,
    ):
        for y in range(1, 12):
            throneRoom.walkingSpace.add((x, y, 0))
    for x in range(3, 10):
        for y in (
            3,
            6,
        ):
            throneRoom.walkingSpace.add((x, y, 0))
    for x in range(5, 8):
        for y in range(7, 12):
            if (x, y) in ((6, 9), (6, 8), (6, 10)):
                continue
            throneRoom.walkingSpace.add((x, y, 0))

    for godId in range(1, 8):
        shrine = src.items.itemMap["Shrine"]()
        shrine.god = godId
        throneRoom.addItem(shrine, (godId + 2, 2, 0))

        statue = src.items.itemMap["GlassStatue"]()
        statue.itemID = godId
        statue.charges = 4
        throneRoom.addItem(statue, (godId + 2, 5, 0))

        throneRoom.addInputSlot((godId + 2, 4, 0), src.gamestate.gamestate.gods[godId]["sacrifice"][0], {})

    throne = src.items.itemMap["Throne"]()
    throne.bolted = True
    throneRoom.addItem(throne, (6, 8, 0))
    dutyBeacon = src.items.itemMap["DutyBeacon"]()
    dutyBeacon.bolted = True
    throneRoom.addItem(dutyBeacon, (6, 9, 0))
    throneRoom.addItem(src.items.itemMap["Regenerator"](), (6, 10, 0))

    for basePos in [(1, 2, 0), (11, 2, 0), (1, 10, 0), (11, 10, 0)]:
        motionSensor = src.items.itemMap["MotionSensor"]()
        motionSensor.target = (basePos[0], basePos[1], basePos[2])
        throneRoom.addItem(motionSensor, (basePos[0], basePos[1] - 1, basePos[2]))
        motionSensor.boltAction(None)
        motionSensor.faction = faction
        shocktower = src.items.itemMap["ShockTower"]()
        throneRoom.addItem(shocktower, (basePos[0], basePos[1], basePos[2]))
        throneRoom.addInputSlot((basePos[0], basePos[1] + 1, basePos[2]), "LightningRod")

        for i in range(1, 10):
            lightningRod = src.items.itemMap["LightningRod"]()
            throneRoom.addItem(lightningRod, (basePos[0], basePos[1] + 1, basePos[2]))

        if basePos == (1, 2, 0):
            shocktower.charges = 10


def spawnSpawnRoom(terrain, coordinate, faction, doors="0,6 6,0 6,12 12,6"):
    '''
    spawn a room with equipment to spawn clones
    '''
    spawnedRoom = spawnRoom(terrain, "EmptyRoom", coordinate, doors)
    for item in spawnedRoom.itemsOnFloor:
        if item.type != "Door":
            continue
        if item.getPosition() == (6, 0, 0):
            continue
        item.walkable = False

    factionChanger = src.items.itemMap["FactionSetter"]()
    factionChanger.faction = faction
    spawnedRoom.addItem(factionChanger, (5, 3, 0))

    for y in range(1, 12):
        spawnedRoom.walkingSpace.add((1, y, 0))
        if y not in (10,):
            spawnedRoom.walkingSpace.add((6, y, 0))
        spawnedRoom.walkingSpace.add((11, y, 0))
    for x in range(1, 12):
        for y in (11, 9, 4, 1):
            if x in (
                1,
                6,
                11,
            ):
                continue
            spawnedRoom.walkingSpace.add((x, y, 0))

    integrator = src.items.itemMap["Integrator"]()
    spawnedRoom.addItem(integrator, (7, 3, 0))

    spawnedRoom.addStorageSlot(
        (3, 2, 0),
        "Implant",
    )
    implant = src.items.itemMap["Implant"]()
    spawnedRoom.addItem(implant, (3, 2, 0))

    spawnedRoom.addStorageSlot((2, 3, 0), "GooFlask", {"desiredState": "filled"})
    growthTank = src.items.itemMap["GrowthTank"]()
    spawnedRoom.addItem(growthTank, (3, 3, 0))

    command = src.items.itemMap["Command"]()
    command.command = list("dj") + ["enter"] + list("sdddJwaaaw")
    command.bolted = True
    spawnedRoom.addItem(command, (4, 3, 0))

    flask = src.items.itemMap["GooFlask"]()
    flask.uses = 100
    spawnedRoom.addItem(flask, (2, 3, 0))

    spawnedRoom.addStorageSlot((7, 5, 0), "Flask", {"desiredState": "filled"})
    item = src.items.itemMap["AlchemyTable"]()
    item.bolted = True
    spawnedRoom.addItem(item, (8, 5, 0))

    spawnedRoom.addInputSlot((2, 10, 0), "Bloom")
    item = src.items.itemMap["BloomShredder"]()
    spawnedRoom.addItem(item, (3, 10, 0))
    item = src.items.itemMap["BioPress"]()
    spawnedRoom.addItem(item, (5, 10, 0))
    item = src.items.itemMap["GooProducer"]()
    spawnedRoom.addItem(item, (7, 10, 0))
    item = src.items.itemMap["GooDispenser"]()
    item.charges = 5
    spawnedRoom.addItem(item, (8, 10, 0))

    door = src.items.itemMap["Door"]()
    door.bolted = False
    spawnedRoom.addItem(door, (2, 8, 0))
    door = src.items.itemMap["Door"]()
    door.bolted = False
    spawnedRoom.addItem(door, (3, 8, 0))
    door = src.items.itemMap["Door"]()
    door.bolted = False
    spawnedRoom.addItem(door, (4, 8, 0))
    door = src.items.itemMap["Door"]()
    door.bolted = False
    spawnedRoom.addItem(door, (5, 8, 0))
    door = src.items.itemMap["Door"]()
    door.bolted = False
    spawnedRoom.addItem(door, (2, 7, 0))
    door = src.items.itemMap["Door"]()
    door.bolted = False
    spawnedRoom.addItem(door, (3, 7, 0))
    door = src.items.itemMap["Door"]()
    door.bolted = False
    spawnedRoom.addItem(door, (4, 7, 0))
    door = src.items.itemMap["Door"]()
    door.bolted = False
    spawnedRoom.addItem(door, (5, 7, 0))

    spawnedRoom.addStorageSlot((7, 8, 0), "ManaCrystal", {"desiredState": "filled"})
    spawnedRoom.addStorageSlot((8, 8, 0), "SpiderEye", {"desiredState": "filled"})
    spawnedRoom.addStorageSlot((9, 8, 0), "ChitinPlates", {"desiredState": "filled"})
    spawnedRoom.addStorageSlot((10, 8, 0), "Grindstone", {"desiredState": "filled"})

    spawnedRoom.addStorageSlot((2, 5, 0), "Door", {"desiredState": "filled"})
    spawnedRoom.addStorageSlot((3, 5, 0), "Door", {"desiredState": "filled"})
    spawnedRoom.addStorageSlot((4, 5, 0), "Door", {"desiredState": "filled"})
    spawnedRoom.addStorageSlot((5, 5, 0), "Door", {"desiredState": "filled"})


def spawnControlRoom(terrain, coordinate, spawnReportArchive=False):
    '''
    spawn a main control room for the base
    '''
    mainRoom = spawnRoom(terrain, "EmptyRoom", coordinate, "0,6 6,0 6,12 12,6")
    mainRoom.storageRooms = []
    for item in mainRoom.getItemByPosition((12, 6, 0)):
         if item.type != "Door":
             continue
         item.walkable = False

    # place anvil
    anvilPos = (10, 2, 0)
    machinemachine = src.items.itemMap["Anvil"]()
    mainRoom.addItem(machinemachine, (anvilPos[0], anvilPos[1], 0))
    mainRoom.addInputSlot((anvilPos[0] - 1, anvilPos[1], 0), "Scrap")
    mainRoom.addInputSlot((anvilPos[0] + 1, anvilPos[1], 0), "Scrap")
    mainRoom.addOutputSlot((anvilPos[0], anvilPos[1] - 1, 0), None)
    mainRoom.walkingSpace.add((anvilPos[0], anvilPos[1] + 1, 0))

    # place metal working bench
    metalWorkBenchPos = (8, 3, 0)
    machinemachine = src.items.itemMap["MetalWorkingBench"]()
    mainRoom.addItem(machinemachine, (metalWorkBenchPos[0], metalWorkBenchPos[1], 0))
    mainRoom.addInputSlot((metalWorkBenchPos[0] + 1, metalWorkBenchPos[1], 0), "MetalBars")
    mainRoom.addOutputSlot((metalWorkBenchPos[0], metalWorkBenchPos[1] - 1, 0), None)
    mainRoom.addOutputSlot((metalWorkBenchPos[0], metalWorkBenchPos[1] + 1, 0), None)
    mainRoom.walkingSpace.add((metalWorkBenchPos[0] - 1, metalWorkBenchPos[1], 0))

    # add walking space cross
    for y in range(1, 12):
        mainRoom.walkingSpace.add((6, y, 0))
    for x in range(1, 6):
        mainRoom.walkingSpace.add((x, 6, 0))

    # add storage section
    mainRoom.walkingSpace.add((11, 6, 0))
    for y in (11, 9, 8, 6):
        for x in range(7, 12):
            if (x, y) == (11, 6):
                continue
            mainRoom.addStorageSlot((x, y, 0), None, {})
            # if y == 11:
            #    scrap = src.items.itemMap["Scrap"](amount=20)
            #    mainRoom.addItem(scrap,(x,y,0))
            if y == 9 and x in (
                8,
                9,
                10,
            ):
                flask = src.items.itemMap["GooFlask"]()
                flask.uses = 100
                mainRoom.addItem(flask, (x, y, 0))

    # add walking space in storage section
    for y in (10, 7, 5):
        for x in range(7, 12):
            mainRoom.walkingSpace.add((x, y, 0))
    for y in (8, 11):
        for x in range(1, 7):
            mainRoom.walkingSpace.add((x, y, 0))

    for x in range(2, 6):
        mainRoom.walkingSpace.add((x, 3, 0))

    # add items
    painter = src.items.itemMap["Painter"]()
    mainRoom.addItem(painter, (7, 8, 0))

    # add mini wall production
    mainRoom.addInputSlot((1, 7, 0), "MetalBars")
    manufacturingTable = src.items.itemMap["ManufacturingTable"]()
    manufacturingTable.bolted = True
    manufacturingTable.toProduce = "Rod"
    mainRoom.addItem(manufacturingTable, (2, 7, 0))
    mainRoom.addStorageSlot((3, 7, 0), "Rod", {"desiredState": "filled"})
    manufacturingTable = src.items.itemMap["ManufacturingTable"]()
    manufacturingTable.bolted = True
    manufacturingTable.toProduce = "Frame"
    mainRoom.addItem(manufacturingTable, (4, 7, 0))
    mainRoom.addStorageSlot((5, 7, 0), "Frame", {"desiredState": "filled"})
    mainRoom.addInputSlot((1, 10, 0), "Frame", None)
    manufacturingTable = src.items.itemMap["ManufacturingTable"]()
    manufacturingTable.bolted = True
    manufacturingTable.toProduce = "Case"
    mainRoom.addItem(manufacturingTable, (2, 10, 0))
    mainRoom.addStorageSlot((3, 10, 0), "Case", {"desiredState": "filled"})
    mainRoom.addInputSlot((4, 9, 0), "MetalBars")
    manufacturingTable = src.items.itemMap["ManufacturingTable"]()
    manufacturingTable.bolted = True
    manufacturingTable.toProduce = "Wall"
    mainRoom.addItem(manufacturingTable, (4, 10, 0))
    mainRoom.addStorageSlot((5, 10, 0), "Wall")

    # add scrap compactor
    mainRoom.addInputSlot((1, 9, 0), "Scrap")
    scrapCompactor = src.items.itemMap["ScrapCompactor"]()
    scrapCompactor.bolted = True
    mainRoom.addItem(scrapCompactor, (2, 9, 0))
    mainRoom.addStorageSlot((3, 9, 0), "MetalBars", None)

    # add management items
    cityPlaner = src.items.itemMap["CityPlaner"]()
    cityPlaner.bolted = True
    cityPlaner.autoExtensionThreashold = 0
    mainRoom.addItem(cityPlaner, (2, 2, 0))
    promoter = src.items.itemMap["Promoter"]()
    promoter.bolted = True
    mainRoom.addItem(promoter, (4, 2, 0))
    if spawnReportArchive:
        reportArchive = src.items.itemMap["ReportArchive"]()
        reportArchive.bolted = True
        mainRoom.addItem(reportArchive, (5, 1, 0))
    communicator = src.items.itemMap["Communicator"]()
    communicator.bolted = True
    mainRoom.addItem(communicator, (1, 3, 0))
    dutyArtwork = src.items.itemMap["DutyArtwork"]()
    dutyArtwork.bolted = True
    mainRoom.addItem(dutyArtwork, (2, 4, 0))
    siegeManager = src.items.itemMap["SiegeManager"]()
    siegeManager.bolted = True
    mainRoom.addItem(siegeManager, (4, 4, 0))
    siegeManager.handleTick()
    knowledge_base = src.items.itemMap["KnowledgeBase"]()
    knowledge_base.bolted = True
    mainRoom.addItem(knowledge_base, (4, 5, 0))

    # add most basic items
    painter = src.items.itemMap["Painter"]()
    painter.bolted = False
    mainRoom.addItem(painter, (7, 11, 0))
    roomBuilder = src.items.itemMap["RoomBuilder"]()
    roomBuilder.bolted = False
    mainRoom.addItem(roomBuilder, (8, 11, 0))
    roomBuilder = src.items.itemMap["RoomBuilder"]()
    roomBuilder.bolted = False
    mainRoom.addItem(roomBuilder, (9, 11, 0))

    return mainRoom


def spawnRoom(terrain, roomType, coordinate, doors="0,6 6,0 6,12 12,6"):
    '''
    spawn a room
    '''
    architect = getArchitect(terrain)

    return architect.doAddRoom(
        {
            "coordinate": coordinate,
            "roomType": roomType,
            "doors": doors,
            "offset": [1, 1],
            "size": [13, 13],
        },
        None,
    )


def getArchitect(terrain):
    '''
    get an architect item able to do things
    '''
    items = terrain.getItemByPosition((1, 1, 0))
    if len(items):
        for item in items:
            if isinstance(item, src.items.itemMap["ArchitectArtwork"]):
                architect = item
                break
    else:
        architect = src.items.itemMap["ArchitectArtwork"]()
        architect.godMode = True
        terrain.addItem(architect, (1, 1, 0))
    return architect


def spawnForest(terrain,coordinate):
    '''
    spawn a forrest
    '''
    terrain.forests.append(coordinate)
    
    tree = src.items.itemMap["Tree"]()
    terrain.addItem(tree,(15*coordinate[0]+7,15*coordinate[1]+7,0))

def spawnWaves():
    '''
    spawn waves of enemies
    '''
    for (godId,god) in src.gamestate.gamestate.gods.items():
        if ( (god["lastHeartPos"][0] != god["home"][0]) or
             (god["lastHeartPos"][1] != god["home"][1])):

            terrain = src.gamestate.gamestate.terrainMap[god["lastHeartPos"][1]][god["lastHeartPos"][0]]

            spectreHome = (god["home"][0],god["home"][1],0)

            numEnemies = 1
            numSpectres = 0
            numSpectres += numEnemies

            numGlassHeartsOnPos = 0
            for checkGod in src.gamestate.gamestate.gods.values():
                if god["lastHeartPos"] == checkGod["lastHeartPos"]:
                    numGlassHeartsOnPos += 1

            multipliers = (1.1,1.2,1.1,1.2)
            baseHealth = 50
            baseDamage = 5
            if src.gamestate.gamestate.difficulty == "easy":
                baseHealth = 10
                baseDamage = 3
                multipliers = (1.01,1.02,1.01,1.02)
            elif src.gamestate.gamestate.difficulty == "difficulty":
                baseHealth = 100
                baseDamage = 10
                multipliers = (1.3,1.5,1.3,1.5)

            for _i in range(numSpectres):
                enemy = src.characters.characterMap["Spectre"](6,6)
                enemy.health = int(baseHealth*2*multipliers[0]**numGlassHeartsOnPos)
                enemy.maxHealth = enemy.health
                enemy.baseDamage = int(baseDamage+1*multipliers[1]**numGlassHeartsOnPos)
                enemy.faction = "spectre"
                enemy.tag = "spectre"
                enemy.name = "stealerSpectre"
                enemy.movementSpeed = 2
                enemy.registers["HOMETx"] = spectreHome[0]
                enemy.registers["HOMETy"] = spectreHome[1]
                enemy.registers["HOMEx"] = 7
                enemy.registers["HOMEy"] = 7
                enemy.personality["moveItemsOnCollision"] = False

                numTries = 0
                while True:
                    numTries += 1

                    bigPos = (random.randint(1,13),random.randint(1,13),0)
                    rooms = terrain.getRoomByPosition(bigPos)
                    if rooms:
                        if numTries < 10:
                            continue
                        rooms[0].addCharacter(enemy,6,6)
                        break
                    else:
                        terrain.addCharacter(enemy,15*bigPos[0]+7,15*bigPos[1]+7)
                        break

                quest = src.quests.questMap["DelveDungeon"](targetTerrain=(terrain.xPosition,terrain.yPosition,0),itemID=godId)
                quest.autoSolve = True
                quest.assignToCharacter(enemy)
                quest.activate()
                enemy.quests.append(quest)

                quest = src.quests.questMap["GoHome"]()
                quest.autoSolve = True
                quest.assignToCharacter(enemy)
                quest.activate()
                enemy.quests.append(quest)

                quest = src.quests.questMap["Vanish"]()
                quest.autoSolve = True
                quest.assignToCharacter(enemy)
                quest.activate()
                enemy.quests.append(quest)

                enemy = src.characters.characterMap["Spectre"](6,6)
                #enemy.health = int(src.gamestate.gamestate.tick//(15*15*15)*1.5**numGlassHeartsOnPos)*2
                enemy.health = int(baseHealth*multipliers[2]**numGlassHeartsOnPos)
                enemy.maxHealth = enemy.health
                #enemy.baseDamage = int((5+(src.gamestate.gamestate.tick//(15*15*15))/10)*1.1**numGlassHeartsOnPos)
                enemy.baseDamage = int(baseDamage+3*multipliers[3]**numGlassHeartsOnPos)
                enemy.faction = "spectre"
                enemy.tag = "spectre"
                enemy.name = "killerSpectre"
                enemy.movementSpeed = 1.8
                enemy.registers["HOMETx"] = spectreHome[0]
                enemy.registers["HOMETy"] = spectreHome[1]
                enemy.registers["HOMEx"] = 7
                enemy.registers["HOMEy"] = 7
                enemy.personality["moveItemsOnCollision"] = False

                numTries = 0
                while True:
                    numTries += 1

                    bigPos = (random.randint(1,13),random.randint(1,13),0)
                    rooms = terrain.getRoomByPosition(bigPos)
                    if rooms:
                        if numTries < 10:
                            continue
                        rooms[0].addCharacter(enemy,6,6)
                        break
                    else:
                        terrain.addCharacter(enemy,15*bigPos[0]+7,15*bigPos[1]+7)
                        break

                quest = src.quests.questMap["ClearTerrain"]()
                quest.autoSolve = True
                quest.assignToCharacter(enemy)
                quest.activate()
                enemy.quests.append(quest)

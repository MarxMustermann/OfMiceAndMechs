import src
import pytest

def test_creation():
    for itemType in src.items.itemMap.values():
        if itemType.isAbstract:
            continue
        item = itemType()

@pytest.mark.parametrize("itemType", src.items.itemMap.values())
def test_simple_apply(itemType,character_room):
    if itemType.isAbstract:
        return

    (character,room) = character_room

    item = itemType()

    room.addItem(item,(1,2,0))

    character.runCommandString("Ja")
    for i in range(10):
        character.timeTaken = 0
        character.advance(advanceMacros=True)

@pytest.mark.parametrize("itemType", src.items.itemMap.values())
def test_simple_configure(itemType,character_room):
    if itemType.isAbstract:
        return

    (character,room) = character_room

    item = itemType()

    room.addItem(item,(1,2,0))

    character.runCommandString("Ca")
    for i in range(10):
        character.timeTaken = 0
        character.advance(advanceMacros=True)

@pytest.mark.parametrize("itemType", src.items.itemMap.values())
def test_simple_examine(itemType,character_room):
    if itemType.isAbstract:
        return

    (character,room) = character_room

    item = itemType()

    room.addItem(item,(1,2,0))

    character.runCommandString("ae")
    for i in range(10):
        character.timeTaken = 0
        character.advance(advanceMacros=True)

@pytest.fixture
def anvil_room(character_room):
    (character,room) = character_room
    anvil = src.items.itemMap["Anvil"]()
    room.addItem(anvil,(1,2,0))
    return (character,room)

def test_Anvil_1_from_inventory_to_inventory(anvil_room):
    character = anvil_room[0]

    scrap = src.items.itemMap["Scrap"]()
    character.inventory.append(scrap)

    character.runCommandString("Jaj")

    for i in range(100):
        character.timeTaken = 0
        character.advance(advanceMacros=True)

    assert len(character.inventory) == 1
    assert character.inventory[0].type == "MetalBars"

def test_Anvil_10_from_inventory_to_inventory(anvil_room):
    character = anvil_room[0]

    for i in range(10):
        scrap = src.items.itemMap["Scrap"]()
        character.inventory.append(scrap)

    character.runCommandString("Jasj")

    for i in range(500):
        character.timeTaken = 0
        character.advance(advanceMacros=True)

    assert len(character.inventory) == 10
    for item in character.inventory:
        assert item.type == "MetalBars"

def test_Anvil_show_schedule(anvil_room):
    character = anvil_room[0]

    character.runCommandString("Jassj")

    for i in range(10):
        character.timeTaken = 0
        character.advance(advanceMacros=True)

def test_Anvil_schedule_production(anvil_room):
    character = anvil_room[0]

    character.runCommandString("Jasssj")

    for i in range(10):
        character.timeTaken = 0
        character.advance(advanceMacros=True)

@pytest.fixture
def metalWorking_room(character_room):
    (character,room) = character_room
    item = src.items.itemMap["MetalWorkingBench"]()
    room.addItem(item,(1,2,0))
    return (character,room)

def test_MetalWorkingBench_production1(metalWorking_room):
    character = metalWorking_room[0]

    item = src.items.itemMap["MetalBars"]()
    character.inventory.append(item)

    character.runCommandString("Jajj")

    for i in range(1000):
        character.timeTaken = 0
        character.advance(advanceMacros=True)

    assert len(character.inventory) == 1
    assert character.inventory[0].type != "MetalBars"

def test_MetalWorkingBench_production2(metalWorking_room):
    character = metalWorking_room[0]

    item = src.items.itemMap["MetalBars"]()
    character.inventory.append(item)
    item = src.items.itemMap["MetalBars"]()
    character.inventory.append(item)

    character.runCommandString("Jajj")

    for i in range(1000):
        character.timeTaken = 0
        character.advance(advanceMacros=True)

    assert len(character.inventory) == 2
    assert character.inventory[0].type == "MetalBars"
    assert character.inventory[-1].type != "MetalBars"

def test_MetalWorkingBench_production3(metalWorking_room):
    character = metalWorking_room[0]

    item = src.items.itemMap["MetalBars"]()
    character.inventory.append(item)
    item = src.items.itemMap["MetalBars"]()
    character.inventory.append(item)

    character.runCommandString("Jajk")

    for i in range(1000):
        character.timeTaken = 0
        character.advance(advanceMacros=True)

    assert len(character.inventory) == 1
    assert character.inventory[0].type == "MetalBars"

def test_MetalWorkingBench_production4(metalWorking_room):
    character = metalWorking_room[0]

    item = src.items.itemMap["MetalBars"]()
    character.inventory.append(item)
    item = src.items.itemMap["MetalBars"]()
    character.inventory.append(item)
    item = src.items.itemMap["MetalBars"]()
    character.inventory.append(item)
    item = src.items.itemMap["MetalBars"]()
    character.inventory.append(item)
    item = src.items.itemMap["MetalBars"]()
    character.inventory.append(item)

    character.runCommandString(list("JajJ3")+["enter"])

    for i in range(1000):
        character.timeTaken = 0
        character.advance(advanceMacros=True)

    assert len(character.inventory) == 5
    assert character.inventory[0].type == "MetalBars"
    assert character.inventory[1].type == "MetalBars"
    assert character.inventory[-1].type != "MetalBars"
    assert character.inventory[-2].type != "MetalBars"
    assert character.inventory[-3].type != "MetalBars"

def test_MetalWorkingBench_production5(metalWorking_room):
    character = metalWorking_room[0]

    item = src.items.itemMap["MetalBars"]()
    character.inventory.append(item)
    item = src.items.itemMap["MetalBars"]()
    character.inventory.append(item)
    item = src.items.itemMap["MetalBars"]()
    character.inventory.append(item)
    item = src.items.itemMap["MetalBars"]()
    character.inventory.append(item)
    item = src.items.itemMap["MetalBars"]()
    character.inventory.append(item)

    character.runCommandString(list("JajK3")+["enter"])

    for i in range(1000):
        character.timeTaken = 0
        character.advance(advanceMacros=True)

    assert len(character.inventory) == 2
    assert character.inventory[0].type == "MetalBars"
    assert character.inventory[1].type == "MetalBars"

def test_shrine_usage(character_room):
    (character,room) = character_room

    src.gamestate.gamestate.gods[2] = {}
    src.gamestate.gamestate.gods[2]["lastHeartPos"] = (6,5,0)

    terrain = character.getTerrain()
    terrain.mana = 300

    terrain.scrapFields.append((9,9,0))

    characterPos = character.getPosition()
    itemPos = (characterPos[0]-1,characterPos[1],characterPos[2])

    shrine = src.items.itemMap["Shrine"]()
    shrine.god = 2
    room.addItem(shrine,itemPos)

    character.runCommandString("Jasjsj")

    for i in range(50):
        character.timeTaken = 0
        character.advance(advanceMacros=True)

def test_regenerator_usage(character_room):
    (character,room) = character_room

    characterPos = character.getPosition()
    itemPos = (characterPos[0]-1,characterPos[1],characterPos[2])

    regenerator = src.items.itemMap["Regenerator"]()
    room.addItem(regenerator,itemPos)

    character.runCommandString(list("Jaj")+["enter"])

    for i in range(50):
        character.timeTaken = 0
        character.advance(advanceMacros=True)

    print(regenerator)
    print(regenerator.activated)
    
    for i in range(50):
        room.advance()
        src.gamestate.gamestate.tick += 1

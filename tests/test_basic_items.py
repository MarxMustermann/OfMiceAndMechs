import src
import pytest

def test_creation():
    #src.canvas.displayChars = src.canvas.DisplayMapping("pureASCII")
    #src.interaction.urwid = src.pseudoUrwid
    #src.gamestate.gamestate = src.gamestate.GameState(11)

    for itemType in src.items.itemMap.values():
        if itemType.isAbstract:
            continue
        item = itemType()

def test_apply():
    for itemType in src.items.itemMap.values():
        if itemType.isAbstract:
            continue

        item = itemType()

        room = src.rooms.EmptyRoom()
        character = src.characters.characterMap["Clone"]()
        room.addCharacter(character,2,2)
        room.addItem(item,(1,2,0))
        room.xPosition = 7
        room.yPosition = 7
        room.hidden = False
        room.reconfigure(15, 15, doorPos=[])

        terrain = src.terrains.Nothingness()
        terrain.addRooms([room])

        character.runCommandString("Ja")
        for i in range(10):
            character.timeTaken = 0
            character.advance(advanceMacros=True)

@pytest.fixture
def anvil_room():
    room = src.rooms.EmptyRoom()
    character = src.characters.characterMap["Clone"]()
    room.addCharacter(character,2,2)
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
def metalWorking_room():
    room = src.rooms.EmptyRoom()
    character = src.characters.characterMap["Clone"]()
    room.addCharacter(character,2,2)
    item = src.items.itemMap["MetalWorkingBench"]()
    room.addItem(item,(1,2,0))
    return (character,room)

def test_MetalWorkingBench_schedule_production(metalWorking_room):
    character = metalWorking_room[0]

    character.runCommandString("Jajj")

    for i in range(10):
        character.timeTaken = 0
        character.advance(advanceMacros=True)

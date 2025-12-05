import src
import pytest

src.canvas.displayChars = src.canvas.DisplayMapping("pureASCII")
src.interaction.urwid = src.pseudoUrwid
src.gamestate.gamestate = src.gamestate.GameState(11)

@pytest.fixture
def terrain():
    terrain = src.terrains.Nothingness()
    terrain.xPosition = 7
    terrain.yPosition = 7
    return terrain

@pytest.fixture
def character():
    character = src.characters.characterMap["Clone"]()
    character.registers["HOMETx"] = 7
    character.registers["HOMETy"] = 7
    character.registers["HOMEx"] = 7
    character.registers["HOMEy"] = 7

    return character

@pytest.fixture
def character_room(terrain,character):
    room = src.rooms.EmptyRoom()
    room.addCharacter(character,2,2)

    room.xPosition = 7
    room.yPosition = 7
    room.offsetX = 0
    room.offsetY = 0
    room.hidden = False
    room.reconfigure(15, 15, doorPos=[])

    terrain.addRooms([room])

    return (character,room)


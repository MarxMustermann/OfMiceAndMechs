import src
import pytest

@pytest.fixture
def character_room():
    room = src.rooms.EmptyRoom()
    character = src.characters.characterMap["Clone"]()
    room.addCharacter(character,2,2)
    character.registers["HOMETx"] = 7
    character.registers["HOMETy"] = 7
    character.registers["HOMEx"] = 7
    character.registers["HOMEy"] = 7

    room.xPosition = 7
    room.yPosition = 7
    room.offsetX = 0
    room.offsetY = 0
    room.hidden = False
    room.reconfigure(15, 15, doorPos=[])

    terrain = src.terrains.Nothingness()
    terrain.addRooms([room])
    terrain.xPosition = 7
    terrain.yPosition = 7

    return (character,room)


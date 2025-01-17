import src
import pytest

@pytest.fixture
def character_room():
    room = src.rooms.EmptyRoom()
    character = src.characters.characterMap["Clone"]()
    room.addCharacter(character,2,2)

    room.xPosition = 7
    room.yPosition = 7
    room.offsetX = 0
    room.offsetY = 0
    room.hidden = False
    room.reconfigure(15, 15, doorPos=[])

    terrain = src.terrains.Nothingness()
    terrain.addRooms([room])

    return (character,room)


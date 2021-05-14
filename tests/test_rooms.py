import unittest
import src


class TestBasicRoomFunction(unittest.TestCase):
    def setUp(self):
        src.quests.debugMessages = []

    def test_create(self):
        # test direct creation
        for roomType in src.rooms.roomMap.values():
            item = roomType()

    def test_adding(self):
        room = src.rooms.EmptyRoom()
        item = src.items.Coal()
        item.yPosition = 1
        item.xPosition = 1
        room.addItems([item])
        self.assertEqual(item in room.itemsOnFloor, True)
        self.assertEqual(item.xPosition, 1)
        self.assertEqual(item.yPosition, 1)
        char = src.characters.Character()
        room.addCharacter(char, 2, 1)
        self.assertEqual(room.characters, [char])
        self.assertEqual(char.xPosition, 2)
        self.assertEqual(char.yPosition, 1)


if __name__ == "__main__":
    unittest.main()

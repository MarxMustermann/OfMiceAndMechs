import unittest
import src

class TestBasicTerrainFunction(unittest.TestCase):

    def setUp(self):
        src.items.displayChars = src.canvas.DisplayMapping("pureASCII")
        src.rooms.displayChars = src.canvas.DisplayMapping("pureASCII")
        src.terrains.displayChars = src.canvas.DisplayMapping("pureASCII")
        src.items.gamestate = src.gamestate.GameState()

    def test_create(self):
        for itemType in src.items.itemMap.values():
            item = itemType()

    def test_basicInteractionWithoutFix(self):
        for itemType in src.items.itemMap.values():
            char = src.characters.Character()
            item = itemType()
            char.examine(item)

        for itemType in src.items.itemMap.values():
            char = src.characters.Character()
            item = itemType()
            item.apply(char)

    def test_basicInteractionInRoom(self):
        for itemType in src.items.itemMap.values():
            for characterType in src.characters.characterMap.values():
                char = characterType()
                item = itemType()
                room = src.rooms.EmptyRoom()
                item.xPosition = 1
                item.yPosition = 1
                room.addItems([item])
                room.addCharacter(char,2,1)

                item.apply(char)

    def test_basicInteractionOnTerrain(self):
        for itemType in src.items.itemMap.values():
            for characterType in src.characters.characterMap.values():
                char = characterType()
                item = itemType()
                terrain = src.terrains.EmptyTerrain()
                item.xPosition = 127
                item.yPosition = 112
                terrain.addItems([item])
                terrain.addCharacter(char,128,112)

                item.apply(char)

    def test_basicInteractionInInventory(self):
        for itemType in src.items.itemMap.values():
            for characterType in src.characters.characterMap.values():
                char = characterType()
                item = itemType()
                char.inventory.append(item)
                item.apply(char)

if __name__ == '__main__':
    unittest.main()

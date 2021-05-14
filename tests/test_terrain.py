import unittest
import src


class TestBasicTerrainFunction(unittest.TestCase):
    def setUp(self):
        src.terrains.displayChars = src.canvas.DisplayMapping("pureASCII")
        src.rooms.displayChars = src.canvas.DisplayMapping("pureASCII")
        src.quests.debugMessages = []

    def test_create(self):
        # test direct creation
        terrain = src.terrains.EmptyTerrain()
        terrain = src.terrains.Nothingness()
        terrain = src.terrains.GameplayTest()
        terrain = src.terrains.ScrapField()
        terrain = src.terrains.TutorialTerrain()


if __name__ == "__main__":
    unittest.main()

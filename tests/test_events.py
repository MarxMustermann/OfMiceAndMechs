import unittest
import src


class TestBasicTerrainFunction(unittest.TestCase):
    def setUp(self):
        pass

    def test_create(self):
        for eventType in src.events.eventMap.values():
            event = eventType(10)


if __name__ == "__main__":
    unittest.main()

import unittest
import src
import config


class TestBasicCharacterFunction(unittest.TestCase):
    def setUp(self):
        src.characters.mainChar = None
        src.characters.displayChars = src.canvas.DisplayMapping("pureASCII")
        src.characters.commandChars = config.commandChars
        src.characters.debugMessages = []

        self.character = src.characters.Character()

    def test_create(self):
        for charType in src.characters.characterMap.values():
            char = charType()

    def test_die(self):
        self.assertEqual(self.character.dead, False)
        self.character.die()
        self.assertEqual(self.character.dead, True)

    def test_hunger(self):
        self.character.satiation = 1000
        self.character.advance()
        self.assertEqual(self.character.satiation, 999)

        self.character.satiation = 1
        self.character.advance()
        self.assertEqual(self.character.dead, False)

        self.character.satiation = 0
        self.character.advance()
        self.assertEqual(self.character.dead, True)


if __name__ == "__main__":
    unittest.main()

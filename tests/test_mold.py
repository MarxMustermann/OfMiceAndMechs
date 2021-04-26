import unittest
import src

class TestBasicMoldFunction(unittest.TestCase):

    def setUp(self):
        pass

    def test_create(self):
        # test direct creation
        src.items.displayChars = src.canvas.DisplayMapping("pureASCII")
        mold = src.items.Mold()
        bloom = src.items.Bloom()
        sickBloom = src.items.SickBloom()
        bush = src.items.Bush()
        encrustedBush = src.items.EncrustedBush()
        poisonBloom = src.items.PoisonBloom()
        encrustedPoisionBush = src.items.EncrustedPoisonBush()
        commandBloom = src.items.CommandBloom()
        hiveMind = src.items.HiveMind()

        # test indirect creation
        mold = src.items.itemMap["Mold"]()
        bloom = src.items.itemMap["Bloom"]()
        sickBloom = src.items.itemMap["SickBloom"]()
        bush = src.items.itemMap["Bush"]()
        encrustedBush = src.items.itemMap["EncrustedBush"]()
        poisonBloom = src.items.itemMap["PoisonBloom"]()
        encrustedPoisionBush = src.items.itemMap["EncrustedPoisonBush"]()
        commandBloom = src.items.itemMap["CommandBloom"]()
        hiveMind = src.items.itemMap["HiveMind"]()

class TestCommandBloom(unittest.TestCase):

    def setUp(self):
        src.terrains.displayChars = src.canvas.DisplayMapping("pureASCII")
        self.terrain = src.terrains.EmptyTerrain()
        self.command_bloom = src.items.CommandBloom()
        self.command_bloom.xPosition = 112
        self.command_bloom.yPosition = 112
        self.terrain.addItems([self.command_bloom])
        self.character = src.characters.Character()
        terrain.addCharacter(character,112,112)

    def test_creatureFoodSupply(self):
        self.command_bloom.charges += 1
        self.character.satiation = 10

class TestMoldExpand(unittest.TestCase):

    def setUp(self):
        src.terrains.displayChars = src.canvas.DisplayMapping("pureASCII")
        self.terrain = src.terrains.EmptyTerrain()

    def test_moldExpand(self):
        mold = src.items.Mold()
        mold.spawn()
        mold.spawn()
        mold.spawn()

class TestHiveMind(unittest.TestCase):
    def setUp(self):
        import urwid
        src.interaction.urwid = urwid

    def test_hiveMindExpansion(self):
        hivemind = src.items.HiveMind()
        hivemind.xPosition = 10*15+7
        hivemind.yPosition = 7*15+7

    def test_hiveMindHealthCheck(self):
        print("\n========================================================================")
        print("testing health check")
        print("")
        testPathings = [
                {"start":(5,5),"target":(7,8),"paths":{(7,8):[(5,6),(5,7),(6,7),(7,7)]}},
                {"start":(5,5),"target":(3,8),"paths":{(3,8):[(4,5),(4,6),(4,7),(4,8)]}},
                {"start":(5,5),"target":(8,8),"paths":{(8,8):[(5,6),(5,7),(6,7),(7,7),(8,7)]}},
                {"start":(5,5),"target":(8,3),"paths":{(8,3):[(6,5),(6,4),(6,3),(7,3)]}},
                {"start":(5,5),"target":(3,3),"paths":{(3,3):[(5,4),(4,4),(3,4)]}},
                ]
        for testPathing in testPathings:
            hivemind = src.items.HiveMind()
            hivemind.xPosition = testPathing["start"][0]*15+7
            hivemind.yPosition = testPathing["start"][1]*15+7
            hivemind.paths = testPathing["paths"]
            terrain = src.terrains.EmptyTerrain()
            character = src.characters.Character()
            terrain.addCharacter(character,testPathing["start"][0]*15+7,testPathing["start"][1]*15+7)

            command = hivemind.doHealthCheck(character,testPathing["target"])

            print(command+"\n")

            for char in command:
                character.macroState["commandKeyQueue"].append((char,[]))

            path = [(testPathing["start"][0]*15+7,testPathing["start"][1]*15+7)]
            while character.macroState["commandKeyQueue"]:
                src.interaction.processInput(character.macroState["commandKeyQueue"][0],charState=character.macroState,noAdvanceGame=True,char=character)
                character.macroState["commandKeyQueue"].remove(character.macroState["commandKeyQueue"][0])
                if not path[-1] == (character.xPosition,character.yPosition):
                    path.append((character.xPosition,character.yPosition))

            for step in path:
                self.assertTrue((step[0]%15 == 7) or (step[1]%15 == 7))

            self.assertEqual(path[-1],(testPathing["target"][0]*15+7,testPathing["target"][1]*15+7))

            itemsOnTarget = terrain.getItemByPosition((testPathing["target"][0]*15+7,testPathing["target"][1]*15+7))
            self.assertEqual(len(itemsOnTarget),1)
            self.assertEqual(itemsOnTarget[-1].type,"CommandBloom")

    def test_hiveMindPath(self):
        print("\n========================================================================")
        print("testing hivemind paths")
        print("")

        testPathings = [
                {"start":(10,7),"paths":{(11,9):[(11,7),(11,8)]},"target":(11,9),"secondToLast":(11,8),"outsiders":[(6,8)]},
                {"start":(10,7),"paths":{(9,9):[(9,7),(9,8)]},"target":(9,9),"secondToLast":(9,8),"outsiders":[(13,12)]},
                {"start":(10,7),"paths":{(9,11):[(9,7),(9,8),(9,9),(9,10)]},"target":(9,11),"secondToLast":(9,10),"outsiders":[(7,8)]},
                {"start":(10,7),"paths":{(11,11):[(11,7),(11,8),(11,9),(11,10)]},"target":(11,11),"secondToLast":(11,10),"outsiders":[(6,8)]},
                {"start":(10,7),"paths":{(8,6):[(9,7),(8,7)]},"target":(8,6),"secondToLast":(8,7),"outsiders":[(6,8)]},
                ]

        for testPathing in testPathings:
            print(testPathing["target"])

            hivemind = src.items.HiveMind()
            hivemind.xPosition = testPathing["start"][0]*15+7
            hivemind.yPosition = testPathing["start"][1]*15+7

            hivemind.paths = testPathing["paths"]
            for outsider in testPathing["outsiders"]:
                (movementPath,secondToLastnode) = hivemind.calculateMovementUsingPaths(outsider)
                self.assertEqual(secondToLastnode,None)
                self.assertEqual(movementPath,"")
            (movementPath,secondToLastnode) = hivemind.calculateMovementUsingPaths(testPathing["target"])
            self.assertEqual(secondToLastnode,testPathing["secondToLast"])
        
            print(movementPath)

            terrain = src.terrains.EmptyTerrain()
            character = src.characters.Character()
            terrain.addCharacter(character,testPathing["start"][0]*15+7,testPathing["start"][1]*15+7)

            for char in movementPath:
                character.macroState["commandKeyQueue"].append((char,[]))

            path = [(testPathing["start"][0]*15+7,testPathing["start"][1]*15+7)]
            while character.macroState["commandKeyQueue"]:
                src.interaction.processInput(character.macroState["commandKeyQueue"][0],charState=character.macroState,noAdvanceGame=True,char=character)
                character.macroState["commandKeyQueue"].remove(character.macroState["commandKeyQueue"][0])
                if not path[-1] == (character.xPosition,character.yPosition):
                    path.append((character.xPosition,character.yPosition))

            for step in path:
                self.assertTrue((step[0]%15 == 7) or (step[1]%15 == 7))

            self.assertEqual(path[-1],(testPathing["target"][0]*15+7,testPathing["target"][1]*15+7))

if __name__ == '__main__':
    unittest.main()

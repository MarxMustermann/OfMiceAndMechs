import src
from src.CharcFolder.Monster import Monster


class Hunter(Monster):
    def __init__(self,):
        super().__init__(name= "Hunter")
        quest = src.quests.questMap["ClearTerrain"]()
        quest.autoSolve = True
        quest.assignToCharacter(self)
        quest.activate()
        self.quests.append(quest)

        self.movementSpeed = 3
        self.solvers = []
        self.specialDisplay = "Hu"
        self.baseDamage = 15

        self.charType = "Hunter"

src.characters.add_character(Hunter)

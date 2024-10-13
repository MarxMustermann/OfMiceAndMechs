import src
from src.CharcFolder.Monster import Monster


class Hunter(Monster):
    def __init__(self,):
        super().__init__(name= "Hunter")
        quest = src.quests.questMap["Huntdown"](target=src.gamestate.gamestate.mainChar,alwaysfollow = True)
        quest.autoSolve = True
        quest.assignToCharacter(self)
        quest.activate()
        self.quests.append(quest)

        self.movementSpeed = 3
        self.solvers = []
        self.specialDisplay = "Hu"
        self.baseDamage = 15


src.characters.add_character(Hunter)

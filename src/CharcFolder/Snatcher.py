import random
import src
from src.CharcFolder.Monster import Monster


class Snatcher(Monster):
    def __init__(self,):
        super().__init__(name= "Snatcher")

        self.movementSpeed = 0.7
        self.solvers = []
        self.specialDisplay = "sn"
        self.baseDamage = 20
        self.maxHealth = 20
        self.health = self.maxHealth

        self.homeTile = None

        self.charType = "Snatcher"
        self.autoAdvance = True

    def generateQuests(self):

        if random.random() < 0.5:
            quest = src.quests.questMap["ClearTerrain"](outsideOnly=True)
            quest.autoSolve = True
            quest.assignToCharacter(self)
            quest.activate()
            self.quests.append(quest)
        else:
            if not self.homeTile:
                self.homeTile = self.getBigPosition()

            quest = src.quests.questMap["SecureTile"](toSecure=self.homeTile,lifetime=random.randint(20,30), wandering=True, endWhenCleared=False)
            quest.autoSolve = True
            quest.assignToCharacter(self)
            quest.activate()
            self.quests.append(quest)

        return super().generateQuests()

src.characters.add_character(Snatcher)

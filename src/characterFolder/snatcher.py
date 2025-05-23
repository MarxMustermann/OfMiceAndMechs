import random
import src

class Snatcher(src.monster.Monster):
    def __init__(self,):
        super().__init__(name= "Snatcher")

        self.movementSpeed = 0.7
        self.solvers = []
        self.specialDisplay = "sn"
        self.baseDamage = 20
        self.maxHealth = 18
        self.health = self.maxHealth
        if src.gamestate.gamestate.difficulty == "difficult":
            self.baseDamage *= 2
            self.health *= 2
            self.maxHealth = 2

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

    def applyNativeMeleeAttackEffects(self,target):
        target.statusEffects.append(src.statusEffects.statusEffectMap["Slowed"](duration=2,slowDown=0.02,reason="You were caught by a Snatcher"))
        super().applyNativeMeleeAttackEffects(target)

src.characters.add_character(Snatcher)

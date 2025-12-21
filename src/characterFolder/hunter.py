import src

class Hunter(src.monster.Monster):
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

    def getLoreDescription(self):
        return f"The Hunters needle like teeth stand in contrast to its thick four legs.\nEach step taken sends waves rippling over his reflective smooth white skin.";

    def getFunctionalDescription(self):
        return f"Hunters are slow, but can be a danger to weaker Clones."

    def description(self):
        return self.getLoreDescription()+"\n\n---- "+self.getFunctionalDescription()

src.characters.add_character(Hunter)

import src

class Pony(src.monster.Monster):
    def __init__(self,):
        super().__init__(name= "Pony")
        quest = src.quests.questMap["WaitQuest"]()
        quest.autoSolve = True
        quest.assignToCharacter(self)
        quest.activate()
        self.quests.append(quest)

        self.agressive = False
        self.movementSpeed = 0.4
        self.solvers = []
        self.specialDisplay = "Po"
        self.baseDamage = 150
        self.maxHealth = 500
        self.health = 500

        self.charType = "Pony"
        self.faction = "ponies"

    def changed(self, tag="default", info=None):
        if not self.agressive:

            for quest in self.quests[:]:
                quests.fail("aborted")

            quest = src.quests.questMap["ClearTerrain"]()
            quest.autoSolve = True
            quest.assignToCharacter(self)
            quest.activate()
            self.quests.append(quest)

            self.agressive = True
        super().changed(tag=tag,info=info)

src.characters.add_character(Pony)

import src
import random

class MonsterSpawner(src.items.Item):
    type = "MonsterSpawner"
    def __init__(self,strength=None):
        super().__init__(display=src.canvas.displayChars.sparkPlug)
        self.name = "monster spawner"

        if strength is None:
            strength = random.randint(1,10)

        self.walkable = False
        self.bolted = True
        self.disabled = False
        self.strength = 1

    def apply(self, character):
        try:
            self.strength
        except:
            self.strength = random.randint(1,10)

        pos = self.getPosition()
        room = self.container
        enemy = src.characters.characterMap["Guardian"](modifier=self.strength)
        room.addCharacter(enemy,pos[0],pos[1])

        quest = src.quests.questMap["ClearTerrain"]()
        quest.autoSolve = True
        quest.assignToCharacter(enemy)
        quest.activate()
        enemy.quests.append(quest)

        self.destroy()

    def render(self):
        return "MS"

src.items.addType(MonsterSpawner)

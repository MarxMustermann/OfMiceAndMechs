import src


class MonsterSpawner(src.items.Item):
    type = "MonsterSpawner"
    def __init__(self):
        super().__init__(display=src.canvas.displayChars.sparkPlug)
        self.name = "monster spawner"

        self.walkable = False
        self.bolted = True
        self.disabled = False

    def apply(self, character):
        pos = self.getPosition()
        room = self.container
        enemy = src.characters.characterMap["Guardian"]()
        enemy.health = 100
        enemy.baseDamage = 7
        enemy.faction = "invader"
        room.addCharacter(enemy,pos[0],pos[1])

        quest = src.quests.questMap["ClearTerrain"]()
        quest.autoSolve = True
        quest.assignToCharacter(enemy)
        quest.activate()
        enemy.quests.append(quest)

    def render(self):
        return "MS"

src.items.addType(MonsterSpawner)

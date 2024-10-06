import src


class Spawner(src.items.Item):
    type = "Spawner"

    def __init__(self):
        super().__init__(display=src.canvas.displayChars.fireCrystals)

        self.name = "spawner"
        self.charges = 1

    def apply(self, character):
        self.spawn()

    def configure(self, character):
        self.spawn()

    def spawn(self):
        if not self.charges:
            return

        enemy = src.characters.characterMap["Monster"](6,6)
        enemy.health = 50
        enemy.maxHealth = enemy.health
        enemy.baseDamage = 5
        enemy.faction = "spectre"
        enemy.tag = "spectre"
        enemy.name = "killerSpectre"
        enemy.movementSpeed = 1.8
        enemy.registers["HOMETx"] = 7
        enemy.registers["HOMETy"] = 7
        enemy.registers["HOMEx"] = 7
        enemy.registers["HOMEy"] = 7
        enemy.personality["moveItemsOnCollision"] = False

        self.container.addCharacter(enemy,6,6)

        quest = src.quests.questMap["ClearTerrain"]()
        quest.autoSolve = True
        quest.assignToCharacter(enemy)
        quest.activate()
        enemy.quests.append(quest)

    def getLongInfo(self):
        return """
item: Spawner

description:
spawner with %s charges
""" % (
            self.charges
        )


src.items.addType(Spawner)

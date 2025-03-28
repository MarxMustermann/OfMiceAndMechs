import random

import src


class EnemyCaller(src.items.Item):
    type = "EnemyCaller"
    name = "Enemy Caller"
    bolted = True
    walkable = False

    enemy_limit = 50

    def __init__(self):
        super().__init__(display="EC")

    def SpawnEnemiesEveryEpoch(self):
        terrain = self.getTerrain()
        if not len(terrain.characters) >= self.enemy_limit:
            for x in range(1, 14):
                for y in range(1, 14):
                    if terrain.getRoomByPosition((x, y)):
                        continue

                    for _i in range(random.randint(0, 2)):
                        monsterType = random.choice(["Golem", "ShieldBug"])
                        pos = (random.randint(1, 11), random.randint(1, 11), 0)
                        golem = src.characters.characterMap[monsterType]()
                        golem.godMode = True
                        quest = src.quests.questMap["SecureTile"](toSecure=(x, y), wandering=False)
                        quest.autoSolve = True
                        quest.assignToCharacter(golem)
                        quest.activate()
                        golem.quests.append(quest)
                        terrain.addCharacter(golem, pos[0] + x * 15, pos[1] + y * 15)

        self.event = src.events.RunCallbackEvent(
            src.gamestate.gamestate.tick + (15 * 15 * 15 - src.gamestate.gamestate.tick % (15 * 15 * 15)) + 10
        )
        self.event.setCallback({"container": self, "method": "handleEpochChange"})
        self.container.addEvent(self.event)

    def apply(self, character):
        if self.event:
            character.addMessage("you disabled the enemy caller")
            self.container.removeEvent(self.event)
            self.event = None
        else:
            character.addMessage("you already disabled the enemy caller")


src.items.addType(EnemyCaller)

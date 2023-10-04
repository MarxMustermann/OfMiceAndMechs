import src


class MonsterSpawner(src.items.Item):
    """
    """

    type = "MonsterSpawner"

    def __init__(self):
        """
        configure the superclass
        """

        super().__init__(display=src.canvas.displayChars.sparkPlug)
        self.name = "monster spawner"

        self.walkable = False
        self.bolted = True
        self.disabled = False

    def apply(self, character):
        if isinstance(character,src.characters.Monster):
            return
        character.addMessage("you rip the spawner apart")

        new = src.items.itemMap["Explosion"]()
        self.container.addItem(new,(self.xPosition,self.yPosition,self.zPosition))
        event = src.events.RunCallbackEvent(
                src.gamestate.gamestate.tick + 1
            )
        event.setCallback({"container": new, "method": "explode"})
        self.container.addEvent(event)
        self.destroy()

    def spawnMonster(self,mass=1):
        for _i in range(mass):
            pos = self.getPosition()
            room = self.container
            enemy = src.characters.Monster(pos[0],pos[1])
            enemy.health = 100
            enemy.baseDamage = 7
            enemy.faction = "invader"
            room.addCharacter(enemy,pos[0],pos[1])

            quest = src.quests.questMap["ClearTerrain"]()
            quest.autoSolve = True
            quest.assignToCharacter(enemy)
            quest.activate()
            enemy.quests.append(quest)

    def destroy(self):
        self.disabled = True
        self.changed("spawner will be destroyed")

        foundSpawner = False
        terrain = self.getTerrain()
        for room in terrain.rooms:
            items = room.getItemByPosition((6,6,0))
            for item in items:
                if item == self:
                    continue
                if isinstance(item, src.items.itemMap["MonsterSpawner"]):
                    foundSpawner = True
                    break

        terrain = self.getTerrain()
        for character in terrain.characters:
            if character.faction != "invader":
                continue
            if foundSpawner:
                distance = character.getBigDistance(self.container.getPosition())
                if distance > 3:
                    continue
                if character.tag != "hiveGuard":
                    continue

            quest = src.quests.questMap["ClearTerrain"]()
            quest.autoSolve = True
            character.assignQuest(quest,active=True)
        for room in terrain.rooms:
            if foundSpawner:
                distance = room.getDistance(self.container.getPosition())
                if distance > 3:
                    continue

            for character in room.characters:
                if character.faction != "invader":
                    continue
                quest = src.quests.questMap["ClearTerrain"]()
                quest.autoSolve = True
                character.assignQuest(quest,active=True)

        room = self.container
        super().destroy()
        room.destroy()
        src.gamestate.gamestate.save()


    def render(self):
        return "MS"

src.items.addType(MonsterSpawner)

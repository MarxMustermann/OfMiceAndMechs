import src

class DestroySpawner(src.quests.MetaQuestSequence):
    type = "DestroySpawner"

    def __init__(self, description="destroy hive",targetPosition=None):
        super().__init__()
        self.metaDescription = description+f" {targetPosition}"
        self.targetPosition = targetPosition
        self.spawnedPrepared = False

    def generateTextDescription(self):
        text = f"""
Destroy the hive on tile {self.targetPosition}.


To destroy the hive, go to the monster spawner (MS) in the middle of the hive and activate it.
You may want to plan an escape route."""
        return text

    def handleSpawnerKill(self):
        self.triggerCompletionCheck(self.character)

    def assignToCharacter(self,character):
        if self.character:
            return

        foundSpawner = False
        terrain = character.getTerrain()
        rooms = terrain.getRoomByPosition(self.targetPosition)
        for room in rooms:
            items = room.getItemByPosition((6,6,0))
            for item in items:
                if isinstance(item, src.items.itemMap["MonsterSpawner"]):
                    foundSpawner = item

        if foundSpawner:
            self.startWatching(foundSpawner,self.handleSpawnerKill, "spawner will be destroyed")

        super().assignToCharacter(character)

    def triggerCompletionCheck(self,character=None):
        if not character:
            return

        if not self.active:
            return

        foundSpawner = False
        terrain = character.getTerrain()
        rooms = terrain.getRoomByPosition(self.targetPosition)
        for room in rooms:
            items = room.getItemByPosition((6,6,0))
            for item in items:
                if isinstance(item, src.items.itemMap["MonsterSpawner"]) and not item.disabled:
                    foundSpawner = True

        if not foundSpawner:
            self.postHandler()
            return True
        return

    def solver(self,character):

        if self.triggerCompletionCheck(character):
            return
        if not self.subQuests:
            if not self.spawnedPrepared:
                quest = src.quests.questMap["PrepareAttack"](targetPosition=self.targetPosition)
                self.addQuest(quest)
                self.spawnedPrepared = True
                return

            if not character.getBigPosition() == self.targetPosition:
                quest = src.quests.questMap["GoToTile"](targetPosition=self.targetPosition)
                self.addQuest(quest)
                return
            if character.getDistance((6,6,0)) > 1:
                quest = src.quests.questMap["GoToPosition"](targetPosition=(6,6,0),ignoreEndBlocked=True)
                self.addQuest(quest)
                return

            offset = (6-character.xPosition,6-character.yPosition,0-character.zPosition)
            commandMap = {
                    (1,0,0):"Jd",
                    (0,1,0):"Js",
                    (-1,0,0):"Ja",
                    (0,-1,0):"Jw",
                    (0,0,0):"j",
                }

            if offset in commandMap:
                quest = src.quests.questMap["RunCommand"](command=commandMap[offset])
                self.addQuest(quest)
                return

        super().solver(character)

src.quests.addType(DestroySpawner)

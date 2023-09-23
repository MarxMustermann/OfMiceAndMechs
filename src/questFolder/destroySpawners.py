import src
import random

class DestroySpawners(src.quests.MetaQuestSequence):
    type = "DestroySpawners"

    def __init__(self, description="destroy hives"):
        super().__init__()
        self.metaDescription = description

    def generateTextDescription(self):
        hiveText = """Insects near to the hive"""
        text = []
        text.extend(["""
Hives have developed in the abandoned farms.
Insect grow there and attack the base.
Put an end to those attacks by destroying those hives.

Keep in mind that destroying the hives will agitate the insects.
"""+hiveText+""" will try to kill anybody on the terrain.

This will likely result in a wave of enemies attacking the base.
This may destroy the base so prepare for that attack.

There are hives on the following tiles:

"""])
        for spawner in self.getSpawners(self.character):
            text.extend([str(spawner.getPosition()),"\n"])
        text.extend(["""
The Hives are shown on the minimap as: """,(src.interaction.urwid.AttrSpec("#484", "black"), "##")])
        return text

    def getSpawners(self,character):
        currentTerrain = character.getTerrain()
        spawnersFound = []
        for room in currentTerrain.rooms:
            for item in room.getItemByPosition((6,6,0)):
                if isinstance(item, src.items.itemMap["MonsterSpawner"]):
                    spawnersFound.append(item.container)

        return spawnersFound

    def triggerCompletionCheck(self,character=None):
        if not character:
            return

        if not self.getSpawners(character):
            self.postHandler()
            return True
        return

    def solver(self,character):
        if self.triggerCompletionCheck(character):
            return

        if not self.subQuests:
            quest = src.quests.questMap["Heal"]()
            self.addQuest(quest)
            quest = src.quests.questMap["GetEpochReward"](doEpochEvaluation=True)
            self.addQuest(quest)
            spawner = random.choice(self.getSpawners(character))
            quest = src.quests.questMap["DestroySpawner"](targetPosition=spawner.getPosition())
            self.addQuest(quest)
        super().solver(character)

src.quests.addType(DestroySpawners)

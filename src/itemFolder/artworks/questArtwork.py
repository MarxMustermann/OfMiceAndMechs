import src
import random


class QuestArtwork(src.items.Item):
    """

    """

    type = "QuestArtwork"

    def __init__(self):
        """
        call superclass constructor with modified parameters
        """

        self.tasks = []

        super().__init__(display="QA")

        self.name = "quest artwork"

        self.applyOptions.extend(
            [
                ("returnQuest", "return quest"),
                ("getQuest", "get quest"),
            ]
        )
        self.applyMap = {
            "returnQuest": self.returnQuest,
            "getQuest": self.getQuest,
        }
        self.numQuestsGiven = 0

        self.attributesToStore.extend(
            [
                "numQuestsGiven",
            ]
        )

    def returnQuest(self, character):
        foundQuests = []
        for quest in character.quests:
            if quest.completed:
                foundQuests.append(quest)

        if not foundQuests:
            character.addMessage("no quest finished")
            return

        for quest in foundQuests:
            character.quests.remove(quest)
            item = src.items.itemMap["GooFlask"]()
            item.uses = 100
            character.inventory.append(item)
            character.addMessage("quest reward issued: GooFlask")

    def getQuest(self, character):
        if len(character.quests) > 2:
            character.addMessage("too many quests")
            return

        self.numQuestsGiven += 1

        bigX = random.randint(1, 13)
        bigY = random.randint(1, 13)
        x = bigX * 15 + random.randint(1, 13)
        y = bigY * 15 + random.randint(1, 13)
        enemy = src.characters.Monster(x, y)
        enemy.health = 10 + self.numQuestsGiven + random.randint(1, 100)
        enemy.baseDamage = self.numQuestsGiven // 5 + random.randint(1, 10)
        enemy.godMode = True
        terrain = self.getTerrain()
        terrain.addCharacter(enemy, x, y)
        quest = src.quests.MurderQuest2()
        quest.setTarget(enemy)
        quest.information = "lastSeen: %s/%s" % (
            bigX,
            bigY,
        )
        character.assignQuest(quest)
        character.addMessage("quest was assigned")

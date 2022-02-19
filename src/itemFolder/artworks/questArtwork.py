import src
import random


class QuestArtwork(src.items.Item):
    """
    ingame item spawning quests and giving rewards
    used to add more excitement and ressources to the game
    """

    type = "QuestArtwork"

    def __init__(self):
        """
        call superclass constructor with modified parameters
        """

        super().__init__(display="QA")

        self.name = "quest artwork"

        self.applyOptions.extend(
                [
                    ("getQuest", "get quest"),
                ]
            )
        self.applyMap = {
            "getQuest": self.getQuest,
        }
        self.numQuestsGiven = 0

        self.attributesToStore.extend(
                [
                    "numQuestsGiven",
                ]
            )

    def getQuest(self, character):
        for room in self.container.container.rooms:
            for target in room.characters:
                if target.faction == character.faction:
                    continue
                containerQuest = src.quests.MetaQuestSequence()
                quest = src.quests.GoToTile()
                quest.setParameters({"targetPosition":(self.container.xPosition,self.container.yPosition)})
                quest.assignToCharacter(character)
                containerQuest.addQuest(quest)
                quest = src.quests.SecureTile()
                quest.setParameters({"targetPosition":(room.xPosition,room.yPosition)})
                quest.assignToCharacter(character)
                quest.activate()
                containerQuest.addQuest(quest)
                containerQuest.assignToCharacter(character)
                containerQuest.activate()

                if character.quests and isinstance(character.quests[0],src.quests.BeUsefull):
                    character.quests[0].addQuest(containerQuest)
                else:
                    character.quests.insert(0,containerQuest)
                character.addMessage("quest assigned")
                return

        for line in src.gamestate.gamestate.terrainMap:
            for terrain in line:
                if isinstance(terrain,src.terrains.Ruin):
                    quest = src.quests.LootRuin()
                    quest.setParameters({"targetPosition":(terrain.xPosition,terrain.yPosition,0)})
                    quest.assignToCharacter(character)
                    quest.activate()

                    if character.quests and isinstance(character.quests[0],src.quests.BeUsefull):
                        quest.assignToCharacter(character)
                        quest.activate()
                        character.quests[0].addQuest(quest)
                    else:
                        character.quests.insert(0,quest)
                    character.addMessage("quest assigned")
                    return

        character.addMessage("no quest assigned")
        return

src.items.addType(QuestArtwork)

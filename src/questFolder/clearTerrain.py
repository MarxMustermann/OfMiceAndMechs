import src
import random

class ClearTerrain(src.quests.MetaQuestSequence):
    type = "ClearTerrain"

    def __init__(self, description="clear terrain", creator=None, command=None, lifetime=None):
        questList = []
        super().__init__(questList, creator=creator, lifetime=lifetime)
        self.metaDescription = description

    def generateTextDescription(self):
        text = """
Clear the whole terrain from enemies.

Just clear the whole terrain tile for tile.
"""

    def triggerCompletionCheck(self,character=None):
        if not character:
            return
        if not character.container:
            return

        if isinstance(character.container,src.rooms.Room):
            terrain = character.container.container
        else:
            terrain = character.container

        for otherChar in terrain.characters:
            if otherChar.faction == character.faction:
                continue
            return
        for room in terrain.rooms:
            for otherChar in room.characters:
                if otherChar.faction == character.faction:
                    continue
                return

        super().triggerCompletionCheck()
        return False

    def solver(self, character):
        if len(self.subQuests):
            return super().solver(character)
        else:
            self.triggerCompletionCheck(character)

            if character.yPosition%15 == 14:
                character.runCommandString("w")
                return
            if character.yPosition%15 == 0:
                character.runCommandString("s")
                return
            if character.xPosition%15 == 14:
                character.runCommandString("a")
                return
            if character.xPosition%15 == 0:
                character.runCommandString("d")
                return

            if isinstance(character.container,src.rooms.Room):
                terrain = character.container.container
            else:
                terrain = character.container

            steps = ["clearOutside","clearRooms"]
            if random.random() < 0.3:
                steps = ["clearRooms","clearOutside"]

            for step in steps:
                if step == "clearRooms":
                    for otherChar in terrain.characters:
                        if otherChar.faction == character.faction:
                            continue
                        quest = src.quests.questMap["SecureTile"](toSecure=(otherChar.xPosition//15,otherChar.yPosition//15),endWhenCleared=True)
                        quest.assignToCharacter(character)
                        quest.activate()
                        self.addQuest(quest)
                        return
                if step == "clearOutside":
                    for room in terrain.rooms:
                        for otherChar in room.characters:
                            if otherChar.faction == character.faction:
                                continue
                            self.addQuest(src.quests.questMap["SecureTile"](toSecure=room.getPosition(),endWhenCleared=True))
                            return

src.quests.addType(ClearTerrain)

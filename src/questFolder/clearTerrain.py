import random

import src


class ClearTerrain(src.quests.MetaQuestSequence):
    type = "ClearTerrain"

    def __init__(self, description="clear terrain", creator=None, command=None, lifetime=None):
        questList = []
        super().__init__(questList, creator=creator, lifetime=lifetime)
        self.metaDescription = description

    def generateTextDescription(self):
        text = ["""
Clear the whole terrain from enemies.

Just clear the whole terrain tile for tile.
"""]
        return text

    def triggerCompletionCheck(self,character=None):
        if not character:
            return None
        if not character.container:
            return None

        if isinstance(character.container,src.rooms.Room):
            terrain = character.container.container
        else:
            terrain = character.container

        for otherChar in terrain.characters:
            if otherChar.faction == character.faction:
                continue
            return None
        for room in terrain.rooms:
            for otherChar in room.characters:
                if otherChar.faction == character.faction:
                    continue
                return None

        super().triggerCompletionCheck()
        return False


    def getNextStep(self,character=None,ignoreCommands=False, dryRun = True):
        if not character:
            return (None,None)

        if not self.subQuests:
            if not ignoreCommands and character.macroState.get("submenue"):
                return (None,(["esc"],"exit submenu"))

            if character.yPosition%15 == 14:
                return (None,("w","enter tile"))
            if character.yPosition%15 == 0:
                return (None,("s","enter tile"))
            if character.xPosition%15 == 14:
                return (None,("a","enter tile"))
            if character.xPosition%15 == 0:
                return (None,("d","enter tile"))

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
                        return ([quest],None)
                if step == "clearOutside":
                    for room in terrain.rooms:
                        for otherChar in room.characters:
                            if otherChar.faction == character.faction:
                                continue
                            quest = src.quests.questMap["SecureTile"](toSecure=room.getPosition(),endWhenCleared=True)
                            return ([quest],None)
        return (None,None)

src.quests.addType(ClearTerrain)

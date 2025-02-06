import random

import src


class ClearTerrain(src.quests.MetaQuestSequence):
    type = "ClearTerrain"

    def __init__(self, description="clear terrain", creator=None, command=None, lifetime=None,outsideOnly=False,insideOnly=False):
        questList = []
        super().__init__(questList, creator=creator, lifetime=lifetime)
        self.metaDescription = description
        self.outsideOnly = outsideOnly
        self.insideOnly = insideOnly

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

        if self.outsideOnly:
            for otherChar in terrain.characters:
                if otherChar.faction == character.faction:
                    continue
                if terrain.getRoomByPosition(otherChar.getBigPosition()):
                    continue
                return False
        elif self.insideOnly:
            for room in terrain.rooms:
                for otherChar in room.characters:
                    if otherChar.faction == character.faction:
                        continue
                    return False
        else:
            for otherChar in terrain.characters:
                if otherChar.faction == character.faction:
                    continue
                return False
            for room in terrain.rooms:
                for otherChar in room.characters:
                    if otherChar.faction == character.faction:
                        continue
                    return False

        self.postHandler()
        return True


    def getNextStep(self,character=None,ignoreCommands=False, dryRun = True):
        if not character:
            return (None,None)

        if self.subQuests:
            return (None,None)

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

        if self.outsideOnly:
            steps = ["clearOutside"]
        if self.insideOnly:
            steps = ["clearRooms"]

        for step in steps:
            if step == "clearOutside":
                for otherChar in terrain.characters:
                    if otherChar.faction == character.faction:
                        continue
                    if terrain.getRoomByPosition(otherChar.getBigPosition()):
                        continue
                    if otherChar.xPosition//15 in (0,14):
                        continue
                    if otherChar.yPosition//15 in (0,14):
                        continue
                    quest = src.quests.questMap["SecureTile"](toSecure=(otherChar.xPosition//15,otherChar.yPosition//15),endWhenCleared=True)
                    return ([quest],None)
            if step == "clearRooms":
                for room in terrain.rooms:
                    for otherChar in room.characters:
                        if otherChar.faction == character.faction:
                            continue
                        quest = src.quests.questMap["SecureTile"](toSecure=room.getPosition(),endWhenCleared=True)
                        return ([quest],None)

        return (None,None)

src.quests.addType(ClearTerrain)

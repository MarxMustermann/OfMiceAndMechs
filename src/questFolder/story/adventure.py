import src
import random

import src.helpers

class Adventure(src.quests.MetaQuestSequence):
    type = "Adventure"

    def __init__(self, description="adventure", creator=None, lifetime=None, reason=None):
        questList = []
        super().__init__(questList, creator=creator,lifetime=lifetime)
        self.metaDescription = description
        self.reason = reason
        self.visited_terrain = []

    def getNextStep(self,character=None,ignoreCommands=False, dryRun = True):

        if self.subQuests:
            return (None,None)

        if not character:
            return (None,None)

        if character.getBigPosition()[0] == 0:
            return (None, ("d","enter the terrain"))
        if character.getBigPosition()[0] == 14:
            return (None, ("a","enter the terrain"))
        if character.getBigPosition()[1] == 0:
            return (None, ("s","enter the terrain"))
        if character.getBigPosition()[1] == 14:
            return (None, ("w","enter the terrain"))
        
        currentTerrain = character.getTerrain()

        if character.getFreeInventorySpace() < 2:
            if currentTerrain.tag == "shrine":
                quest = src.quests.questMap["GoHome"]()
                return ([quest],None)
        try:
            self.visited_terrain
        except:
            self.visited_terrain = []

        candidates = []
        for x in range(14):
            for y in range(14):
                if (x, y, 0) not in self.visited_terrain:
                    candidates.append((x, y, 0))

        homeCoordinate = (character.registers["HOMETx"], character.registers["HOMETy"], 0)
        candidates.remove(homeCoordinate)

        if len(candidates):
            candidates.sort(key=lambda x: src.helpers.distance_between_points(character.getTerrainPosition(), x))
            targetTerrain = candidates[0]
            if not dryRun:
                self.visited_terrain.append(targetTerrain)
            quest = src.quests.questMap["AdventureOnTerrain"](targetTerrain=targetTerrain)
            return ([quest], None)

        if dryRun:
            self.fail()
        return (None, None)

    def generateTextDescription(self):
        return ["""
Go out and adventure.

"""]

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.wrapedTriggerCompletionCheck, "set faction")
        super().assignToCharacter(character)

    def wrapedTriggerCompletionCheck(self):
        if self.completed:
            1/0
        if not self.active:
            return

        self.triggerCompletionCheck(self.character)

    def triggerCompletionCheck(self,character=None):
        if not character:
            return False

        currentTerrain = character.getTerrain()
        if not currentTerrain.xPosition == character.registers["HOMETx"]:
            return False
        if not currentTerrain.yPosition == character.registers["HOMETy"]:
            return False

        if not character.getFreeInventorySpace() < 2:
            return False

        self.postHandler()
        return True

src.quests.addType(Adventure)

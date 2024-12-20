import src
import random

class Adventure(src.quests.MetaQuestSequence):
    type = "Adventure"

    def __init__(self, description="adventure", creator=None, lifetime=None, reason=None):
        questList = []
        super().__init__(questList, creator=creator,lifetime=lifetime)
        self.metaDescription = description
        self.reason = reason

    def getNextStep(self,character=None,ignoreCommands=False, dryRun = True):

        if self.subQuests:
            return (None,None)

        if not character:
            return (None,None)

        currentTerrain = character.getTerrain()

        candidates = []
        if currentTerrain.xPosition > 1:
            candidates.append((currentTerrain.xPosition-1,currentTerrain.yPosition,0))
        if currentTerrain.xPosition < 13:
            candidates.append((currentTerrain.xPosition+1,currentTerrain.yPosition,0))
        if currentTerrain.yPosition > 1:
            candidates.append((currentTerrain.xPosition,currentTerrain.yPosition-1,0))
        if currentTerrain.yPosition < 13:
            candidates.append((currentTerrain.xPosition,currentTerrain.yPosition+1,0))

        homeCoordinate = (character.registers["HOMETx"],character.registers["HOMETy"],0)
        if homeCoordinate in candidates:
            candidates.remove(homeCoordinate)

        quest = src.quests.questMap["AdventureOnTerrain"](targetTerrain=random.choice(candidates))
        return ([quest],None)

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

        return False

        self.postHandler()

src.quests.addType(Adventure)

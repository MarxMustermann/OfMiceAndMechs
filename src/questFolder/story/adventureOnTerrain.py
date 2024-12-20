import src
import random

class AdventureOnTerrain(src.quests.MetaQuestSequence):
    type = "AdventureOnTerrain"

    def __init__(self, description="adventure on terrain", creator=None, lifetime=None, reason=None, targetTerrain=None):
        questList = []
        super().__init__(questList, creator=creator,lifetime=lifetime)
        self.metaDescription = description
        self.reason = reason
        self.targetTerrain = targetTerrain

    def getNextStep(self,character=None,ignoreCommands=False, dryRun = True):

        if self.subQuests:
            return (None,None)

        if not character:
            return (None,None)

        currentTerrain = character.getTerrain()

        if not (currentTerrain.xPosition == self.targetTerrain[0] and currentTerrain.yPosition == self.targetTerrain[1]):
            quest = src.quests.questMap["GoToTerrain"](targetTerrain=self.targetTerrain)
            return ([quest],None)

        if character.getBigPosition()[0] == 0:
            return (None, ("d","enter the terrain"))
        if character.getBigPosition()[0] == 13:
            return (None, ("a","enter the terrain"))
        if character.getBigPosition()[1] == 0:
            return (None, ("s","enter the terrain"))
        if character.getBigPosition()[1] == 13:
            return (None, ("w","enter the terrain"))
        
        if not character.getBigPosition() == (7,7,0):
            return (None,("gmc","go to terrain center"))

        if not character.container.isRoom:
            if character.getSpacePosition() == (0,7,0):
                return (None, ("d","enter the room"))
            if character.getSpacePosition() == (7,0,0):
                return (None, ("s","enter the room"))
            if character.getSpacePosition() == (14,7,0):
                return (None, ("a","enter the room"))
            if character.getSpacePosition() == (7,14,0):
                return (None, ("w","enter the room"))
            if not dryRun:
                self.postHandler()
            return (None,None)

        for item in character.container.itemsOnFloor:
            if item.bolted or not item.walkable:
                continue

            
        
        1/0
        if not dryRun:
            self.postHandler()
        return (None,None)

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

src.quests.addType(AdventureOnTerrain)

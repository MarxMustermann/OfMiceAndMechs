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
        if character.getBigPosition()[0] == 14:
            return (None, ("a","enter the terrain"))
        if character.getBigPosition()[1] == 0:
            return (None, ("s","enter the terrain"))
        if character.getBigPosition()[1] == 14:
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

        for otherCharacter in character.container.characters:
            if otherCharacter.faction == character.faction:
                continue
            quest = src.quests.questMap["Fight"]()
            return ([quest],None)


        for item in character.container.itemsOnFloor:
            if item.bolted or not item.walkable:
                continue
            if item.xPosition > 12:
                continue
            quest = src.quests.questMap["LootRoom"](targetPosition=character.container.getPosition())
            return ([quest],None)

        return (None,None)

    def generateTextDescription(self):
        return ["""
Go out and adventure.

"""]

    def triggerCompletionCheck(self,character=None):
        if not character:
            return False

        currentTerrain = character.getTerrain()

        if not (currentTerrain.xPosition == self.targetTerrain[0] and currentTerrain.yPosition == self.targetTerrain[1]):
            return False

        if not character.getFreeInventorySpace():
            self.postHandler()
            return True

        if currentTerrain.tag == "ruin":
            if not character.getBigPosition() == (7,7,0):
                return False
            
            if not character.container.isRoom:
                return False

            for otherCharacter in character.container.characters:
                if otherCharacter.faction == character.faction:
                    continue
                return False

            for item in character.container.itemsOnFloor:
                if item.bolted or not item.walkable:
                    continue

                invalidStack = False
                for stackedItem in character.container.getItemByPosition(item.getPosition()):
                    if stackedItem == item:
                        break
                    if not stackedItem.bolted:
                        continue
                    invalidStack = True

                if not invalidStack:
                    return False

        self.postHandler()
        return True

    def wrapedTriggerCompletionCheck(self,test=None):
        pass

src.quests.addType(AdventureOnTerrain)

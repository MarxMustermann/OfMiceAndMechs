import src
import random
import itertools
import logging

logger = logging.getLogger(__name__)

class AdventureOnTerrain(src.quests.MetaQuestSequence):
    type = "AdventureOnTerrain"

    def __init__(self, description="adventure on terrain", creator=None, lifetime=None, reason=None, targetTerrain=None):
        questList = []
        super().__init__(questList, creator=creator,lifetime=lifetime)
        self.metaDescription = description
        self.reason = reason
        self.targetTerrain = targetTerrain
        self.posOfInterest = []
        self.populated_posOfInterest = False
        self.current_target = None

    def getNextStep(self,character=None,ignoreCommands=False, dryRun = True):
        if self.subQuests:
            return (None,None)

        if not character:
            return (None,None)

        if character.macroState["submenue"]:
            return (None, ("esc", "exit menu"))

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
        
        try:
            self.posOfInterest
        except:
            self.posOfInterest = []

        if not len(self.posOfInterest):
            for char in currentTerrain.characters:
                if char == character:
                    continue
                if char.getBigPosition() not in self.posOfInterest:
                    self.posOfInterest.append(char.getBigPosition())
            self.populated_posOfInterest = True

        char_big_pos = character.getBigPosition()
        if not self.posOfInterest:
            if not dryRun:
                self.fail("no POI found to explore")
            return (None,None)

        if not char_big_pos in self.posOfInterest:
            posToGo = random.choice(self.posOfInterest)
            self.current_target = posToGo
            offset = (posToGo[0] - char_big_pos[0] , posToGo[1] - char_big_pos[1])
            moves = "gm"
            if offset[0] > 0:
                moves += "d" * offset[0]
            elif offset[0] < 0:
                moves += "a" * -offset[0]
            if offset[1] > 0:
                moves += "s" * offset[1]
            elif offset[1] < 0:
                moves += "w" * -offset[1]
            return (None,(moves+"j","go to terrain room"))

        if not character.container.isRoom and len(character.terrain.getRoomByPosition(self.current_target)):
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

        if character.container.isRoom:
            itemsOnFloor = character.container.itemsOnFloor
            enemies = character.container.characters
        else:
            itemsOnFloor = character.container.getNearbyItems(character)
            enemies = character.container.getEnemiesOnTile(character)

        for otherCharacter in enemies:
            if otherCharacter.faction == character.faction:
                continue
            quest = src.quests.questMap["Fight"]()
            return ([quest],None)


        for item in itemsOnFloor:
            if item.bolted or not item.walkable:
                continue
            item_pos =item.getSmallPosition()
            if item_pos[0] == None:
                logger.error("found ghost item")
                continue
            if item_pos[0] > 12:
                continue

            if item.name in ("scrap","metal bars"):
                        continue
            quest = src.quests.questMap["LootRoom"](targetPosition=character.getBigPosition())
            return ([quest],None)

        self.posOfInterest.remove(self.current_target)
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
            try:
                self.populated_posOfInterest
            except:
                self.populated_posOfInterest = False
            if self.populated_posOfInterest and not len(self.posOfInterest):
                self.postHandler()
                return True
            return False

        character.terrainInfo[currentTerrain.getPosition()]["looted"] = True
        self.postHandler()
        return True

    def wrapedTriggerCompletionCheck(self,test=None):
        pass

src.quests.addType(AdventureOnTerrain)

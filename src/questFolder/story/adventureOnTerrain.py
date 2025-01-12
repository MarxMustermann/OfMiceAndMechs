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
        self.metaDescription = description+f" {targetTerrain}"
        self.reason = reason
        self.targetTerrain = targetTerrain
        self.donePointsOfInterest = []

    def getRemainingPointsOfInterests(self):
        result = []
        try:
            self.donePointsOfInterest
        except:
            self.donePointsOfInterest = []

        currentTerrain = self.character.getTerrain()

        for char in currentTerrain.characters:
            if char.faction == self.character.faction:
                continue
            if char.getBigPosition() not in result and char.getBigPosition() not in self.donePointsOfInterest:
                result.append(char.getBigPosition())
        for room in currentTerrain.rooms:
            if room.getPosition() not in result and room.getPosition() not in self.donePointsOfInterest:
                result.append(room.getPosition())

        return result

    def getNextStep(self,character=None,ignoreCommands=False, dryRun = True):
        if self.subQuests:
            return (None,None)

        if not character:
            return (None,None)

        if character.macroState["submenue"]:
            return (None, (["esc"], "exit menu"))

        if character.getNearbyEnemies():
            quest = src.quests.questMap["Fight"]()
            return ([quest],None)

        currentTerrain = character.getTerrain()

        if self.targetTerrain[0] == character.registers["HOMETx"] and self.targetTerrain[1] == character.registers["HOMETy"]:
            if not dryRun:
                self.fail("home is target")
            return (None,None)

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
        
        if not character.container.isRoom:
            if character.getSpacePosition() == (0,7,0):
                return (None, ("d","enter the room"))
            if character.getSpacePosition() == (7,0,0):
                return (None, ("s","enter the room"))
            if character.getSpacePosition() == (14,7,0):
                return (None, ("a","enter the room"))
            if character.getSpacePosition() == (7,14,0):
                return (None, ("w","enter the room"))

        pointsOfInterest = self.getRemainingPointsOfInterests()
        if not pointsOfInterest:
            if not dryRun:
                self.fail("no POI found to explore")
            return (None,None)

        char_big_pos = character.getBigPosition()

        if character.container.isRoom:
            itemsOnFloor = character.container.itemsOnFloor
        else:
            itemsOnFloor = character.container.getNearbyItems(character)

        for item in itemsOnFloor:
            if item.bolted or not item.walkable:
                continue
            if item.xPosition == None:
                logger.error("found ghost item")
                continue
            item_pos =item.getSmallPosition()
            if item_pos[0] == None:
                logger.error("found ghost item")
                continue
            if item_pos[0] > 12:
                continue

            if item.type in ("Scrap","MetalBars"):
                continue

            invalidStack = False
            for stackedItem in character.container.getItemByPosition(item.getPosition()):
                if stackedItem == item:
                    break
                if not stackedItem.bolted:
                    continue
                invalidStack = True
            if invalidStack:
                continue

            if character.container.isRoom:
                quest = src.quests.questMap["LootRoom"](targetPosition=character.getBigPosition())
                return ([quest],None)
            else:
                quest = src.quests.questMap["ScavengeTile"](targetPosition=character.getBigPosition())
                return ([quest],None)

        if not dryRun:
            self.donePointsOfInterest.append(character.getBigPosition())

        pointOfInterest = random.choice(pointsOfInterest)
        offset = (pointOfInterest[0] - char_big_pos[0] , pointOfInterest[1] - char_big_pos[1])
        moves = "gm"
        if offset[0] > 0:
            moves += "d" * offset[0]
        elif offset[0] < 0:
            moves += "a" * -offset[0]
        if offset[1] > 0:
            moves += "s" * offset[1]
        elif offset[1] < 0:
            moves += "w" * -offset[1]
        return (None,(moves+"j","go to tile"))

    def generateTextDescription(self):
        return [f"""
Go out and adventure on tile {self.targetTerrain}.

{self.donePointsOfInterest}
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
            if self.getRemainingPointsOfInterests():
                return False

        character.terrainInfo[currentTerrain.getPosition()]["looted"] = True
        self.postHandler()
        return True

    def wrapedTriggerCompletionCheck(self,test=None):
        pass

src.quests.addType(AdventureOnTerrain)

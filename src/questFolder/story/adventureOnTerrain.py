import src
import random
import itertools
import logging

logger = logging.getLogger(__name__)

class AdventureOnTerrain(src.quests.MetaQuestSequence):
    type = "AdventureOnTerrain"

    def __init__(self, description="adventure on terrain", creator=None, lifetime=None, reason=None, targetTerrain=None,terrainsWeight= None):
        questList = []
        super().__init__(questList, creator=creator,lifetime=lifetime)
        self.metaDescription = description+f" {targetTerrain}"
        self.reason = reason
        self.targetTerrain = targetTerrain
        self.donePointsOfInterest = []
        self.terrainsWeight = terrainsWeight

    def getRemainingPointsOfInterests(self):
        result = []

        currentTerrain = self.character.getTerrain()

        for char in currentTerrain.characters:
            if char.faction == self.character.faction:
                continue
            if char.getBigPosition() not in result and char.getBigPosition() not in self.donePointsOfInterest:
                result.append(char.getBigPosition())
        for room in currentTerrain.rooms:
            if room.getPosition() not in result and room.getPosition() not in self.donePointsOfInterest:
                result.append(room.getPosition())

        for donePoi in self.donePointsOfInterest:
            if not donePoi in result:
                continue
            result.remove(donePoi)

        return result

    def getNextStep(self,character=None,ignoreCommands=False, dryRun = True):

        # ensure the quest actually completes
        if self.triggerCompletionCheck(dryRun=dryRun):
            return (None,("+","end quest"))

        # handle weird edge cases
        if self.subQuests:
            return (None,None)
        if not character:
            return (None,None)
        if character.is_low_health():
            return self._solver_trigger_fail(dryRun,"low health")

        # handle menu interaction
        if character.macroState["submenue"]:
            return (None, (["esc"], "exit menu"))

        # defend yourself
        if character.getNearbyEnemies():
            quest = src.quests.questMap["Fight"](reason="eliminate threats")
            return ([quest],None)

        # set up helper variables
        currentTerrain = character.getTerrain()

        # do not adventure at home
        if self.targetTerrain[0] == character.registers["HOMETx"] and self.targetTerrain[1] == character.registers["HOMETy"]:
            return self._solver_trigger_fail(dryRun,"home is target")

        # go to the target terrain
        if not (currentTerrain.xPosition == self.targetTerrain[0] and currentTerrain.yPosition == self.targetTerrain[1]):
            quest = src.quests.questMap["GoToTerrain"](targetTerrain=self.targetTerrain,terrainsWeight= self.terrainsWeight, reason="reach terrain to adventure on")
            return ([quest],None)

        # enter the playing field properly
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

        # mark terrain as completed
        pointsOfInterest = self.getRemainingPointsOfInterests()
        if not pointsOfInterest:
            if currentTerrain.tag == "ruin":
                return (None,("gc","mark terrain as explored"))
            else:
                return self._solver_trigger_fail(dryRun,"no POI")

        # loot current tile
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
            if character.container.isRoom and (item_pos[0] > 11 or item_pos[1] > 11 or item_pos[0] < 1 or item_pos[1] < 1):
                continue

            if item.type in ("Scrap","MetalBars","MoldFeed"):
                continue

            if item.type in ("Bolt",) and character.getFreeInventorySpace() <= 1:
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

            quest = src.quests.questMap["LootRoom"](targetPositionBig=character.getBigPosition(),endWhenFull=True,reason="gain useful items")
            return ([quest],None)

        # mark current tile as explored
        if character.getBigPosition() in self.getRemainingPointsOfInterests():
            if not dryRun:
                self.mark_POI_explored(character.getBigPosition())
            return (None,("+","register room as explored"))

        # loot a different room
        char_big_pos = character.getBigPosition()
        pointOfInterest = random.choice(pointsOfInterest)
        smallest_distance = None
        for check_point in pointsOfInterest:
            if random.random() > 0.8:
                continue
            distance = abs(char_big_pos[0]-check_point[0])+abs(char_big_pos[1]-check_point[1])
            if smallest_distance is None or distance <= smallest_distance:
                smallest_distance = distance
                pointOfInterest = check_point
        quest = src.quests.questMap["LootRoom"](targetPositionBig=pointOfInterest,endWhenFull=True,reason="gather loot")
        return ([quest],None)

    def generateTextDescription(self):
        reasonString = ""
        if self.reason:
            reasonString = ", to "+self.reason
        text = [f"""
Go out and adventure on tile {self.targetTerrain}{reasonString}.

"""]

        text.append(f"""points of interest:\n""")
        rawMap = []
        for y in range(15):
            rawMap.append([])
            for x in range(15):
                if x == 0 or y == 0 or x == 14 or y == 14:
                    rawMap[y].append("~~")
                else:
                    rawMap[y].append("  ")
            rawMap[y].append("\n")
        for pos in self.getRemainingPointsOfInterests():
            rawMap[pos[1]][pos[0]] = "OO"
        for pos in self.donePointsOfInterest:
            rawMap[pos[1]][pos[0]] = "XX"
        text.append("\n")
        text.append(rawMap)
        text.append("\n")
        for pos in self.getRemainingPointsOfInterests()+self.donePointsOfInterest:
            text.append(f"* {pos}")
            if pos in self.donePointsOfInterest:
                text.append(f" visited")
            text.append(f"\n")
        if self.character:
            rawMap[self.character.getBigPosition()[1]][self.character.getBigPosition()[0]] = "@@"

        return text

    def triggerCompletionCheck(self,character=None,dryRun=True):
        if not character:
            return False

        currentTerrain = character.getTerrain()

        if not (currentTerrain.xPosition == self.targetTerrain[0] and currentTerrain.yPosition == self.targetTerrain[1]):
            return False

        if not character.getFreeInventorySpace(ignoreTypes=["Bolt"]):
            if not dryRun:
                self.postHandler()
            return True

        if not currentTerrain.tag == "ruin":
            if not dryRun:
                self.postHandler()
            return True

        if character.terrainInfo[currentTerrain.getPosition()].get("looted"):
            if not dryRun:
                self.postHandler()
            return True

        return False

    def wrapedTriggerCompletionCheck(self,test=None):
        pass

    def handleQuestFailure(self,extraInfo):
        if extraInfo["quest"].type == "LootRoom":
            self.mark_POI_explored(extraInfo["quest"].targetPositionBig)
            return

    def mark_POI_explored(self,pos):
        if pos in self.getRemainingPointsOfInterests() and not pos in self.donePointsOfInterest:
            self.donePointsOfInterest.append(pos)

    def handleChangedTile(self, extraInfo=None):
        self.mark_POI_explored(extraInfo.get("old_pos"))
        self.mark_POI_explored(extraInfo.get("new_pos"))

    def handleEnteredRoom(self, extraInfo=None):
        self.mark_POI_explored(extraInfo[1].getPosition())

        self.clearSubQuests()

    def assignToCharacter(self, character):
        '''
        listen to the character changing the terrain
        '''
        if self.character:
            return

        self.startWatching(character,self.handleChangedTile, "changedTile")
        self.startWatching(character,self.handleEnteredRoom, "entered room")
        super().assignToCharacter(character)

src.quests.addType(AdventureOnTerrain)

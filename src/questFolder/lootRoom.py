import random

import src
import logging

logger = logging.getLogger(__name__)

class LootRoom(src.quests.MetaQuestSequence):
    type = "LootRoom"

    def __init__(self, description="loot room", creator=None, targetPosition=None, reason=None, story=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description+" "+str(targetPosition)
        self.baseDescription = description
        self.reason = reason
        self.story = story

        if targetPosition:
            self.setParameters({"targetPosition":targetPosition})

    def generateTextDescription(self):
        reasonString = ""
        if self.reason:
            reasonString = ", to "+self.reason
        storyString = ""
        if self.story:
            storyString = self.story

        text = f"""{storyString}
Loot the room on tile {self.targetPosition}{reasonString}.

Remove all items that are not bolted down."""
        return text

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.wrapedTriggerCompletionCheck, "itemPickedUp")
        super().assignToCharacter(character)

    def wrapedTriggerCompletionCheck(self,extraInfo=None):
        self.triggerCompletionCheck(extraInfo[0])

    def triggerCompletionCheck(self,character=None):

        if not character:
            return False

        if character.getBigPosition() != (self.targetPosition[0], self.targetPosition[1], 0):
            return False
        
        if not self.getLeftoverItems(character):
            self.postHandler()
            return True

        return False

    def setParameters(self,parameters):
        if "targetPosition" in parameters and "targetPosition" in parameters:
            self.targetPosition = parameters["targetPosition"]
            self.metaDescription = self.baseDescription+" "+str(self.targetPosition)
        return super().setParameters(parameters)

    def getNextStep(self,character=None,ignoreCommands=False, dryRun = True):
        if self.subQuests:
            return (None,None)

        if not character:
            return (None,None)

        if character.getNearbyEnemies():
            quest = src.quests.questMap["Fight"]()
            return ([quest],None)

        if not character.getFreeInventorySpace() > 0:
            quest = src.quests.questMap["ClearInventory"](reason="have inventory space to pick up more items",returnToTile=False)
            return ([quest],None)
        if not isinstance(character.container,src.rooms.Room):
            if character.yPosition%15 == 14:
                return (None,("w","enter tile"))
            if character.yPosition%15 == 0:
                return (None,("s","enter tile"))
            if character.xPosition%15 == 14:
                return (None,("a","enter tile"))
            if character.xPosition%15 == 0:
                return (None,("d","enter tile"))

        if character.getBigPosition() != (self.targetPosition[0], self.targetPosition[1], 0):
            quest = src.quests.questMap["GoToTile"](targetPosition=self.targetPosition)
            return ([quest],None)

        charPos = character.getPosition()

        offsets = [(0,0,0),(1,0,0),(0,1,0),(-1,0,0),(0,-1,0)]
        foundOffset = None
        foundItems = None
        for offset in offsets:
            checkPos = (charPos[0]+offset[0],charPos[1]+offset[1],charPos[2]+offset[2])
            items = character.container.getItemByPosition(checkPos)
            if not items:
                continue

            if items[0].bolted:
                continue

            foundValuableItem = False
            for item in items:
                if item.type in ("Scrap","MetalBars"):
                    continue
                if item.walkable == False:
                    continue
                foundValuableItem = True
            if not foundValuableItem:
                continue

            invalidStack = False
            for stackedItem in character.container.getItemByPosition(checkPos):
                if stackedItem == items[0]:
                    break
                if not stackedItem.bolted:
                    continue
                invalidStack = True
            if invalidStack:
                continue

            foundOffset = offset

            foundItems = []
            for item in items:
                if item.bolted:
                    break
                foundItems.append(item)
            break

        if foundOffset:
            if foundOffset == (0,0,0):
                command = "k"
            elif foundOffset == (1,0,0):
                command = "Kd"
            elif foundOffset == (-1,0,0):
                command = "Ka"
            elif foundOffset == (0,1,0):
                command = "Ks"
            elif foundOffset == (0,-1,0):
                command = "Kw"

            return (None,(command*len(foundItems),"clear spot"))

        items = self.getLeftoverItems(character)
        random.shuffle(items)
        for item in items:
            if item.type in ("Scrap","MetalBars"):
                continue

            item_pos = item.getSmallPosition()
            if item_pos[0] == None:
                logger.error("found ghost item")
                continue
            if item_pos[0] > 12:
                continue
            if item.walkable == False:
                continue

            quest = src.quests.questMap["GoToPosition"](targetPosition=item_pos,ignoreEndBlocked=True)
            return ([quest],None)

        return (None,None)

    def getLeftoverItems(self,character):

        if isinstance(character.container,src.rooms.Room):
            terrain = character.container.container
        else:
            terrain  = character.container

        if character.container.isRoom:
            itemsOnFloor = character.container.itemsOnFloor

            rooms = terrain.getRoomByPosition(self.targetPosition)
            room = None
            if rooms:
                room = rooms[0]

            if room.floorPlan:
                return []
        else:
            itemsOnFloor = character.container.getNearbyItems(character)

        foundItems = []
        for item in itemsOnFloor:
            if item.bolted:
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
            if item.walkable == False:
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

            foundItems.append(item)

        return foundItems
    
    def handleQuestFailure(self,extraInfo):
        if extraInfo["reason"] == "no path found":
            newQuest = src.quests.questMap["ClearPathToPosition"](targetPosition=extraInfo["quest"].targetPosition)
            self.addQuest(newQuest)
            self.startWatching(newQuest,self.handleQuestFailure,"failed")
            return
        self.fail(extraInfo["reason"])

src.quests.addType(LootRoom)

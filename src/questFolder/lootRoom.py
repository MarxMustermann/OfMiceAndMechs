import random

import src
import logging

logger = logging.getLogger(__name__)

class LootRoom(src.quests.MetaQuestSequence):
    type = "LootRoom"

    def __init__(self, description="loot room", creator=None, targetPositionBig=None, reason=None, story=None, endWhenFull=False):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        if targetPositionBig:
            self.metaDescription += " "+str(targetPositionBig)
        self.baseDescription = description
        self.reason = reason
        self.story = story
        self.endWhenFull = endWhenFull

        self.visited_target_tile = False

        self.targetPositionBig = targetPositionBig

    def generateTextDescription(self):
        reasonString = ""
        if self.reason:
            reasonString = ", to "+self.reason
        storyString = ""
        if self.story:
            storyString = self.story

        text = f"""{storyString}
Loot the room on tile {self.targetPositionBig}{reasonString}.

Remove all items that are not bolted down."""
        return text

    def changedTile(self, extraInfo=None):
        if self.targetPositionBig == self.character.getBigPosition():
            self.visited_target_tile = True
        else:
            if self.visited_target_tile:
                self.fail("left target tile")

    def assignToCharacter(self, character):
        if self.character:
            return

        if self.targetPositionBig == character.getBigPosition():
            self.visited_target_tile = True

        self.startWatching(character,self.changedTile, "changedTile")
        self.startWatching(character,self.wrapedTriggerCompletionCheck, "itemPickedUp")
        super().assignToCharacter(character)

    def wrapedTriggerCompletionCheck(self,extraInfo=None):
        self.triggerCompletionCheck(extraInfo[0],dryRun=False)

    def triggerCompletionCheck(self,character=None,dryRun=True):

        if not character:
            return False

        if self.targetPositionBig and character.getBigPosition() != (self.targetPositionBig[0], self.targetPositionBig[1], 0):
            return False

        if self.endWhenFull and character.getFreeInventorySpace(ignoreTypes=["Bolt"]) == 0:
            if not dryRun:
                self.postHandler()
            return True
        
        if not self.getLeftoverItems(character):
            if not dryRun:
                self.postHandler()
            return True

        return False

    def setParameters(self,parameters):
        if "targetPositionBig" in parameters and "targetPositionBig" in parameters:
            self.targetPositionBig = parameters["targetPositionBig"]
            self.metaDescription = self.baseDescription+" "+str(self.targetPositionBig)
        return super().setParameters(parameters)

    def getNextStep(self,character=None,ignoreCommands=False, dryRun = True):

        # handle weird edge cases
        if self.subQuests:
            return (None,None)
        if not character:
            return (None,None)

        # set current position as target
        if not self.targetPositionBig:
            if not dryRun: 
                self.targetPositionBig = character.getBigPosition()
            return (None,("+","set current position as target"))

        # handle submenues
        submenue = character.macroState.get("submenue")
        if submenue and not ignoreCommands:

            # drop item from inventory
            if isinstance(submenue,src.menuFolder.inventoryMenu.InventoryMenu) and character.getFreeInventorySpace() <= 1:
                command = submenue.get_command_to_select_item(item_type="Bolt",selectionCommand="l")
                if command:
                    return (None,(command,"drop the item"))

            # close unknown submenues
            if not submenue.tag in ("advancedPickupSelection",):
                return (None,(["esc"],"exit the menu"))

        # handle direct threats
        if character.getNearbyEnemies():
            quest = src.quests.questMap["Fight"](reason="get rid of threats")
            return ([quest],None)

        # ensure there is inventory space
        if not character.getFreeInventorySpace(ignoreTypes=["Bolt"]) > 0:
            quest = src.quests.questMap["ClearInventory"](reason="have inventory space to pick up more items",returnToTile=False)
            return ([quest],None)

        # actually enter rooms
        if not isinstance(character.container,src.rooms.Room):
            if character.yPosition%15 == 14:
                return (None,("w","enter tile"))
            if character.yPosition%15 == 0:
                return (None,("s","enter tile"))
            if character.xPosition%15 == 14:
                return (None,("a","enter tile"))
            if character.xPosition%15 == 0:
                return (None,("d","enter tile"))

        # go the the location to be looted
        if character.getBigPosition() != (self.targetPositionBig[0], self.targetPositionBig[1], 0):
            quest = src.quests.questMap["GoToTile"](targetPosition=self.targetPositionBig,reason="reach the loot")
            return ([quest],None)

        # find lootable items in reach
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
                if item.type in ("Scrap","MetalBars","MoldFeed",):
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

            foundItems = []
            for item in items:
                if item.type in ("Scrap","MetalBars","MoldFeed",):
                    continue
                if item.bolted:
                    break
                if item.type == "Bolt" and character.getFreeInventorySpace() <= 1:
                    continue
                foundItems.append(item)

            if foundItems:
                foundOffset = offset
                break

        # ensure inventory space
        if not character.getFreeInventorySpace() > 0:
            dropCommand = "l"

            isValidDropSpot = True
            items = character.container.getItemByPosition(character.getPosition())
            if len(items) > 15:
                isValidDropSpot = False
            for item in items:
                if not item.walkable:
                    isValidDropSpot = False
                    break
                if item.type in ("Scrap","MetalBars","MoldFeed",):
                    continue
                if item.type in ["Bolt"]:
                    continue
                isValidDropSpot = False
                break
            if not isValidDropSpot:
                offsets = [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0)]
                random.shuffle(offsets)
                for offset in offsets:
                    isValidDropSpot = True
                    items = character.container.getItemByPosition(character.getPosition())
                    if len(items) > 15:
                        isValidDropSpot = False
                    for item in items:
                        if not item.walkable:
                            isValidDropSpot = False
                            break
                    
                    if isValidDropSpot:
                        dropCommand = "L"
                        match offset:
                            case (1,0,0):
                                dropCommand += "d"
                            case (-1,0,0):
                                dropCommand += "a"
                            case (0,1,0):
                                dropCommand += "s"
                            case (0,-1,0):
                                dropCommand += "w"

            if character.inventory[-1].type == "Bolt":
                return (None,(dropCommand,"drop item"))

            index = 0
            for item in character.inventory:
                if item.type in ["Bolt"]:
                    break
                index += 1
            else:
                abort_reason = "no item type to drop"
                if not dryRun:
                    self.fail(abort_reason)
                return (None,("+","abort quest\n("+abort_reason+")"))
            return (None,("i"+"s"*index+dropCommand,"drop item"))

        # pick up loot
        if foundOffset:
            if foundOffset == (0,0,0):
                command = "k"*len(foundItems)
            elif foundOffset == (1,0,0):
                command = "Kd"
            elif foundOffset == (-1,0,0):
                command = "Ka"
            elif foundOffset == (0,1,0):
                command = "Ks"
            elif foundOffset == (0,-1,0):
                command = "Kw"

            if len(items) > 1 and command[0] == "K":
                hasAvoidItem = False 
                for item in items:
                    if not item.type in ("Scrap","MetalBars","MoldFeed",):
                        continue
                    hasAvoidItem = True
                if not hasAvoidItem:
                    command = command.upper()

            if command[0] == "K":
                if submenue:
                    if submenue.tag == "advancedPickupSelection":
                        command = command[1:]
                    else:
                        return (None,(["esc"],"close menu")

            return (None,(command,"clear spot"))

        # go to loot
        items = self.getLeftoverItems(character)
        random.shuffle(items)
        for item in items:
            if item.type in ("Scrap","MetalBars"):
                continue

            item_pos = item.getSmallPosition()
            if item_pos[0] == None:
                logger.error("found ghost item")
                continue
            if item_pos[0] > 13:
                continue
            if item.walkable == False:
                continue
            if item.type in ["Bolt"] and character.getFreeInventorySpace() <= 1:
                continue

            quest = src.quests.questMap["GoToPosition"](targetPosition=item_pos,ignoreEndBlocked=True,reason="be able to pick up loot")
            return ([quest],None)

        # dummy return
        return self._solver_trigger_fail(dryRun,"unknown reason")

    def getLeftoverItems(self,character):

        if isinstance(character.container,src.rooms.Room):
            terrain = character.container.container
        else:
            terrain  = character.container

        if character.container.isRoom:
            itemsOnFloor = character.container.itemsOnFloor

            targetPositionBig = self.targetPositionBig
            if not targetPositionBig:
                targetPositionBig = character.getBigPosition()
            rooms = terrain.getRoomByPosition(targetPositionBig)
            room = None
            if rooms:
                room = rooms[0]
            else:
                return []

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
            if item_pos[0] > 13:
                continue
            if character.container.isRoom and (item_pos[0] > 11 or item_pos[1] > 11 or item_pos[0] < 1 or item_pos[1] < 1):
                continue
            if item.type in ("Scrap","MetalBars","MoldFeed",):
                continue
            if item.type == "Bolt" and character.getFreeInventorySpace() <= 1:
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

    def getQuestMarkersSmall(self,character,renderForTile=False):
        '''
        return the quest markers for the normal map
        '''
        if isinstance(character.container,src.rooms.Room):
            if renderForTile:
                return []
        else:
            if not renderForTile:
                return []

        result = super().getQuestMarkersSmall(character,renderForTile=renderForTile)
        if not renderForTile:
            if isinstance(character.container,src.rooms.Room):
                if not character.getNearbyEnemies():
                    for item in self.getLeftoverItems(character):
                        result.append((item.getPosition(),"target"))
        return result
    
    def handleQuestFailure(self,extraInfo):
        if extraInfo["reason"] == "no path found":
            newQuest = src.quests.questMap["ClearPathToPosition"](targetPosition=extraInfo["quest"].targetPosition)
            self.addQuest(newQuest)
            self.startWatching(newQuest,self.handleQuestFailure,"failed")
            return
        self.fail(extraInfo["reason"])

src.quests.addType(LootRoom)

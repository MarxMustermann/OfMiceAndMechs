import random

import src
import logging

logger = logging.getLogger(__name__)

class FetchMetalWorkingBench(src.quests.MetaQuestSequence):
    type = "FetchMetalWorkingBench"

    def __init__(self, description="fetch MetalWorkingBench", creator=None, targetPositionBig=None, reason=None, story=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        if targetPositionBig:
            self.metaDescription += " "+str(targetPositionBig)
        self.baseDescription = description
        self.reason = reason
        self.story = story
        self.targetPositionBig = targetPositionBig

    def generateTextDescription(self):
        reasonString = ""
        if self.reason:
            reasonString = ", to "+self.reason
        storyString = ""
        if self.story:
            storyString = self.story

        sample_metalworkingBench = src.items.itemMap["MetalWorkingBench"]()
        character_position = self.character.getBigPosition()
        direction_string = self.character.getTerrain().getDistanceDescription(character_position,self.targetPositionBig)
        direction_string = f"The room with the MetalWorkingBench is {direction_string}."
        if character_position == self.targetPositionBig:
            direction_string = "You are in the room with the MetalWorkingBench"

        text = [f"""{storyString}
""",(src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"""Fetch a MetalWorkingBench"""),f""" from tile {self.targetPositionBig}{reasonString}.

{direction_string}
A MetalWorkingBench looks like this: """,sample_metalworkingBench.metaRender(),"""
""",(src.pseudoUrwid.AttrSpec(src.interaction.ui_hint_color,"black"),"""Use the k or K keys to pick up items.""")]
        return text

    def assignToCharacter(self, character):
        if self.character:
            return

        if self.targetPositionBig == character.getBigPosition():
            self.visited_target_tile = True

        self.startWatching(character,self.wrapedTriggerCompletionCheck, "itemPickedUp")
        super().assignToCharacter(character)

    def wrapedTriggerCompletionCheck(self,extraInfo=None):
        self.triggerCompletionCheck(extraInfo[0],dryRun=False)

    def triggerCompletionCheck(self,character=None,dryRun=True):

        if not character:
            return False

        if character.searchInventory("MetalWorkingBench"):
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

        # handle submenues
        submenue = character.macroState.get("submenue")
        if submenue and not ignoreCommands:

            # close unknown submenues
            if not submenue.tag in ("advancedPickupSelection",):
                return (None,(["esc"],"exit the menu"))

        # handle direct threats
        if character.getNearbyEnemies():
            quest = src.quests.questMap["Fight"](reason="get rid of threats")
            return ([quest],None)

        # ensure there is inventory space
        if not character.getFreeInventorySpace() > 0:
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
            if items[0].type != "MetalWorkingBench":
                continue

            foundOffset = offset
            break

        # pick up loot
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

            if command[0] == "K":
                if submenue:
                    if submenue.tag == "advancedPickupSelection":
                        command = command[1:]
                    else:
                        return (None,(["esc"],"close menu"))

            return (None,(command,"clear spot"))

        # go to loot
        items = self.getMetalWorkingBench(character)
        random.shuffle(items)
        for item in items:
            quest = src.quests.questMap["GoToPosition"](targetPosition=item.getPosition(),ignoreEndBlocked=True,reason="be able to pick up the MetalWorkingBench")
            return ([quest],None)

        # dummy return
        return self._solver_trigger_fail(dryRun,"unknown reason")

    def getMetalWorkingBench(self,character):

        if isinstance(character.container,src.rooms.Room):
            terrain = character.container.container
        else:
            terrain  = character.container

        # get the list of items on the floor
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
            if item.type != "MetalWorkingBench":
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
                    for item in self.getMetalWorkingBench(character):
                        result.append((item.getPosition(),"target"))
        return result
    
    def handleQuestFailure(self,extraInfo):
        if extraInfo["reason"] == "no path found":
            newQuest = src.quests.questMap["ClearPathToPosition"](targetPosition=extraInfo["quest"].targetPosition)
            self.addQuest(newQuest)
            self.startWatching(newQuest,self.handleQuestFailure,"failed")
            return
        self.fail(extraInfo["reason"])

src.quests.addType(FetchMetalWorkingBench)

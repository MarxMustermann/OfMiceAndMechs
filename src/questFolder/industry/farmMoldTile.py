import random

import src

class FarmMoldTile(src.quests.MetaQuestSequence):
    '''
    quest to farm mold on a specific tile
    '''
    type = "FarmMoldTile"
    def __init__(self, description="farm mold tile", creator=None, targetPosition=None, reason=None, endOnFullInventory=False, stimulateMoldGrowth=True,tryHard=False):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description+" "+str(targetPosition)
        self.baseDescription = description
        self.reason = reason
        self.endOnFullInventory = endOnFullInventory
        self.stimulateMoldGrowth = stimulateMoldGrowth
        self.tryHard = tryHard

        self.targetPosition = targetPosition

    def generateTextDescription(self):
        '''
        generate a textual description to show on the UI
        Returns:
            the textual description
        '''

        out = []
        reason = ""
        if self.reason:
            reason = f", to {self.reason}"
        text = f"""
farm mold on the tile {self.targetPosition}{reason}."""
        out.append(text)
        if self.stimulateMoldGrowth:
            out.append("\n\nStimulate the mold growth by picking sprouts")
        return out

    def triggerCompletionCheck(self,character=None,dryRun=True):
        '''
        check if the quest completed and end it
        Parameters:
            character:  the character doing the quest
            dryRun:     flag to be stateless or not
        Returns:
            whether the quest ended or not
        '''

        if not character:
            return False

        if self.endOnFullInventory and not character.getFreeInventorySpace() > 0:
            if not dryRun:
                self.postHandler()
            return True

        if not self.getLeftoverItems(character):
            if not dryRun:
                self.postHandler()
            return True

        return False

    def getNextStep(self,character,ignoreCommands=False, dryRun = True):
        '''
        generate the next step to solve the quest
        Parameters:
            character:       the character doing the quest
            ignoreCommands:  whether to generate commands or not
            dryRun:          flag to be stateless or not
        Returns:
            the activity to run as next step
        '''

        # handle weird edge cases
        if not character:
            return (None,None)
        if self.subQuests:
            return (None,None)
        if character.getTerrain().alarm and not self.tryHard:
            return self._solver_trigger_fail(dryRun,"alarm")
        if character.getTerrain().getRoomByPosition(self.targetPosition):
            return self._solver_trigger_fail(dryRun,"blocked by room")

        # ensure minumum health
        if character.health < 50:
            return self._solver_trigger_fail(dryRun,"low health")

        # go to plot to work on
        if character.getBigPosition() != (self.targetPosition[0], self.targetPosition[1], 0):
            quest = src.quests.questMap["GoToTile"](targetPosition=self.targetPosition,reason="go to target tile")
            return ([quest],None)

        # process each plant
        items = self.getLeftoverItems(character)
        for item in items:
            if item.type == "Bloom":
                path = character.getTerrain().getPathTile(character.getTilePosition(),character.getSpacePosition() ,item.getSmallPosition(),character=character,ignoreEndBlocked =True)
                if len(path):
                    quest = src.quests.questMap["CleanSpace"](targetPosition=item.getSmallPosition(),targetPositionBig=self.targetPosition,reason="pick up the items",pickUpBolted=True)
                    return ([quest],None)

        # soft hang up on weird state
        if not self.stimulateMoldGrowth:
            return (None,(".","stand around confused"))

        # find nearby sprouts
        offsets = [(0,0,0),(1,0,0),(0,1,0),(-1,0,0),(0,-1,0)]
        foundOffset = None
        charPos = character.getPosition()
        for offset in offsets:
            checkPos = (charPos[0]+offset[0],charPos[1]+offset[1],charPos[2]+offset[2])
            items = character.container.getItemByPosition(checkPos)
            if not items:
                continue
            if not items[0].type == "Sprout":
                continue
            foundOffset = offset
            break

        # activate nearby sprouts
        if foundOffset:
            if foundOffset == (0,0,0):
                command = "j"
            elif foundOffset == (1,0,0):
                command = "Jd"
            elif foundOffset == (-1,0,0):
                command = "Ja"
            elif foundOffset == (0,1,0):
                command = "Js"
            elif foundOffset == (0,-1,0):
                command = "Jw"
            if command[0] == "J" and "advancedInteraction" in character.interactionState:
                command = command[1:]
            return (None,(command,"stimulate mold growth"))

        # soft hang up of weird state
        items = self.getLeftoverItems(character)
        if not items:
            return (None,(".","stand around confused"))

        # go to sprout
        item = random.choice(items)
        quest = src.quests.questMap["GoToPosition"](targetPosition=item.getSmallPosition(),ignoreEndBlocked=True)
        return ([quest],None)

    def getLeftoverItems(self,character):
        '''
        get what items still have to be processed
        Parameters:
            character:  the character doing the quest
        Returns:
            the list of items
        '''
        terrain = character.getTerrain()
        if not terrain:
            return []
        leftOverItems = []
        numSprouts = 0
        tile_items = terrain.itemsByBigCoordinate.get(self.targetPosition,[])
        for item in tile_items:
            if item.type == "Bloom":
                leftOverItems.append(item)
            if self.stimulateMoldGrowth:
                if item.type != "Sprout":
                    continue
                items = terrain.getItemByPosition(item.getPosition())
                if len(items) != 1:
                    continue
                if not items[0].type == "Sprout":
                    continue
                numSprouts += 1
                if numSprouts > 4:
                    leftOverItems.append(item)
        random.shuffle(leftOverItems)
        return leftOverItems

    def pickedUpItem(self,extraInfo):
        '''
        react to an item being picked up
        Parameters:
            extraInfo:  context information
        '''
        self.triggerCompletionCheck(extraInfo[0],dryRun=False)

    def handleHurt(self,extraInfo=None):
        '''
        react to being hurt
        Parameters:
            extraInfo:  context information
        '''
        if not self.character:
            return

        if self.character.health < 50:
            self.fail("low health")

    def assignToCharacter(self, character):
        '''
        assign quest to a character
        Parameters:
            character:  the character to assign quest to
        '''

        if self.character:
            return None

        self.startWatching(character,self.handleHurt, "hurt")
        self.startWatching(character,self.pickedUpItem, "itemPickedUp")
        return super().assignToCharacter(character)

    def getQuestMarkersTile(self,character):
        '''
        return the quest markers for the mini map
        Parameters:
            character:      the character doing the quest
        Returns:
            the quest markers to show
        '''
        result = super().getQuestMarkersTile(character)
        result.append(((self.targetPosition[0],self.targetPosition[1]),"target"))
        return result

# register the quest type
src.quests.addType(FarmMoldTile)

import src

import random

class FarmMold(src.quests.MetaQuestSequence):
    '''
    quest to farm mold
    '''
    type = "FarmMold"
    lowLevel = True
    def __init__(self, description="farm mold", creator=None, toCollect=None, lifetime=None, reason=None, tryHard=False, waitForGrowth=False):
        self.lastMoveDirection = None
        questList = []
        super().__init__(questList, creator=creator,lifetime=lifetime)
        self.metaDescription = description
        self.reason = reason
        if toCollect:
            self.metaDescription += " for "+toCollect
        self.toCollect = toCollect
        self.tryHard = tryHard
        self.waitForGrowth = waitForGrowth

    def generateTextDescription(self):
        '''
        get textual description of the quest
        Returns:
            the textual description
        '''
        out = []

        reason = ""
        if self.reason:
            reason = f", to {self.reason}"
        text = f"""
farm mold{reason}."""

        out.append(text)
        return out

    def triggerCompletionCheck(self,character=None, dryRun=True):
        '''
        check if the quest is completed
        Parameters:
            character:  the character doing the quest
            dryRun:     flag to be stateless or not
        Returns:
            whether the quest ended or not
        '''
        if not character:
            return False
        if not character.getFreeInventorySpace():
            if not dryRun:
                self.postHandler()
            return True
        if character.getTerrain().alarm and not self.tryHard:
            if not dryRun:
                self.postHandler()
            return True
        return False

    def getNextStep(self,character,ignoreCommands=False, dryRun = True):
        '''
        generate the next step towards solving the quest
        Parameters:
            character:       the character doing the quest
            ignoreCommands:  whether to generate commands or not
            dryRun:          flag to be stateless or not
        Returns:
            the activity to run as next step
        '''

        # skip weird states
        if self.subQuests:
            return (None,None)
        if not character:
            return (None,None)

        # ensure minumum health
        if character.health < 50:
            return self._solver_trigger_fail(dryRun,"low health")

        # search for blooms to pick
        terrain = character.getTerrain()
        candidates = []
        for (coord,itemList) in terrain.itemsByBigCoordinate.items():
            if character.getTerrain().getRoomByPosition(coord):
                continue
            for item in itemList:
                if not item.type == "Bloom":
                    continue
                candidates.append(coord)

        # pick bloom
        if candidates:
            coord = random.choice(candidates)
            quest = src.quests.questMap["FarmMoldTile"](targetPosition=coord,stimulateMoldGrowth=False,tryHard=self.tryHard,reason="harvest one field")
            return ([quest],None)

        # search for sprouts to pick
        candidates = []
        for (coord,itemList) in terrain.itemsByBigCoordinate.items():
            if character.getTerrain().getRoomByPosition(coord):
                continue
            numSprouts = 0
            for item in itemList:
                if not item.type == "Sprout":
                    continue
                items = terrain.getItemByPosition(item.getPosition())
                if len(items) != 1:
                    continue
                if not items[0].type == "Sprout":
                    continue
                numSprouts += 1
            if numSprouts > 4:
                candidates.append(coord)

        # pick sprouts
        if candidates:
            coord = random.choice(candidates)
            quest = src.quests.questMap["FarmMoldTile"](targetPosition=coord,tryHard=self.tryHard,reason="encourage growth")
            return ([quest],None)

        # abort when nothing to do
        if self.waitForGrowth:
            return (None,(";","wait for the plants to grow"))
        return self._solver_trigger_fail(dryRun,"no field")

    def pickedUpItem(self,test=None):
        '''
        (obsolete)
        handle the character picking up an item
        '''
        pass

    @staticmethod
    def generateDutyQuest(beUsefull,character,currentRoom, dryRun):
        '''
        generate the quests for doing a duty
        Parameters:
            beUsefull:   the quest to generate the duty for
            character:   the character to generate the quest for
            currentRoom: the room the character is currently in
            dryRun:      flag for statelessness
        Returns:
            the generated quests ( (None,None) for no quest to do )
        '''
        terrain = character.getTerrain()
        try:
            terrain.alarm
        except:
            terrain.alarm = False
        if terrain.alarm:
            return (None,None)

        if not character.getFreeInventorySpace():
            quest = src.quests.questMap["ClearInventory"](reason="make space for blooms")
            if not dryRun:
                beUsefull.idleCounter = 0
            return ([quest],None)

        quest = src.quests.questMap["FarmMold"](lifetime=1000,reason="keep the fields going")
        if not dryRun:
            beUsefull.idleCounter = 0
        return ([quest],None)

    def handleHurt(self,extraInfo=None):
        '''
        react to getting hurt
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
        return super().assignToCharacter(character)

# register the quest type
src.quests.addType(FarmMold)

import src

import random

class FarmMold(src.quests.MetaQuestSequence):
    '''
    quest to farm mold
    '''
    type = "FarmMold"
    lowLevel = True
    def __init__(self, description="farm mold", creator=None, toCollect=None, lifetime=None, reason=None, tryHard=False):
        self.lastMoveDirection = None
        questList = []
        super().__init__(questList, creator=creator,lifetime=lifetime)
        self.metaDescription = description
        self.reason = reason
        if toCollect:
            self.metaDescription += " for "+toCollect
        self.toCollect = toCollect
        self.tryHard = tryHard

    def generateTextDescription(self):
        '''
        get textual description of the quest
        '''
        out = []

        reason = ""
        if self.reason:
            reason = f", to {self.reason}"
        text = """
farm mold"""

        out.append(text)
        return out

    def triggerCompletionCheck(self,character=None, dryRun=True):
        '''
        check if the quest is completed
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
        '''

        # skip weird states
        if self.subQuests:
            return (None,None)
        if not character:
            return (None,None)

        # ensure minumum health
        if character.health < 30:
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
            quest = src.quests.questMap["FarmMoldTile"](targetPosition=coord,stimulateMoldGrowth=False,tryHard=self.tryHard)
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
                if len(character.container.getItemByPosition(item.getPosition())) > 1:
                    continue
                numSprouts += 1
            if numSprouts > 4:
                candidates.append(coord)

        # pick sprouts
        if candidates:
            coord = random.choice(candidates)
            quest = src.quests.questMap["FarmMoldTile"](targetPosition=coord,tryHard=self.tryHard)
            return ([quest],None)

        # abort when nothing to do
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
        '''
        terrain = character.getTerrain()
        try:
            terrain.alarm
        except:
            terrain.alarm = False
        if terrain.alarm:
            return (None,None)

        if not character.getFreeInventorySpace():
            quest = src.quests.questMap["ClearInventory"]()
            if not dryRun:
                beUsefull.idleCounter = 0
            return ([quest],None)

        quest = src.quests.questMap["FarmMold"](lifetime=1000)
        if not dryRun:
            beUsefull.idleCounter = 0
        return ([quest],None)

# register the quest type
src.quests.addType(FarmMold)

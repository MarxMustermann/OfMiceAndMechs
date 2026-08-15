import random

import src

class FreeUpStorage(src.quests.MetaQuestSequence):
    '''
    A quest to free uo some storage in the base
    '''
    type = "FreeUpStorage"
    def __init__(self, description="free up storage", creator=None, lifetime=None, reason=None, amount=5):
        self.lastMoveDirection = None
        questList = []
        super().__init__(questList, creator=creator,lifetime=lifetime)
        self.metaDescription = description
        self.reason = reason
        self.amount = amount

    def generateTextDescription(self):
        '''
        returns a text desrcibing the quest
        '''

        # create the description for why the quest was created
        reasonText = (src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),".")
        if self.reason:
            reasonText = [(src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),","),f" to {self.reason}."]

        # generate the text description
        num_free_storage = self.getNumFreeStorageSlots()
        text = [f"""
""",(src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"""Free up general storage slots"""),reasonText,"""
"""]
        text.append(f"""

This quest will end when {self.amount} general storage slots are free.
Currently {num_free_storage} storage slots are free.""")

        # return the description
        return text

    def triggerCompletionCheck(self,character=None,dryRun=True):
        '''
        chcek if the quest has been completed
        '''
        if not character:
            return False
        if self.getNumFreeStorageSlots() >= self.amount:
            if not dryRun:
                self.postHandler()
            return True
        return False

    def getNumFreeStorageSlots(self):
        '''
        get the number of empty storage slots
        '''
        num_empty_storage = 0
        for room in self.character.getTerrain().rooms:
            for storageSlot in room.storageSlots:
                if storageSlot[1]:
                    continue
                if room.getItemByPosition(storageSlot[0]):
                    continue
                num_empty_storage += 1
        return num_empty_storage

    def getNextStep(self,character,ignoreCommands=False, dryRun = True):
        '''
        calculate the next step toward solving the quest
        '''

        # handle weird edge cases
        if not character:
            return (None,None)
        if self.subQuests:
            return (None,None)

        # set up helper variables
        terrain = character.getTerrain()

        if character.getFreeInventorySpace() <= 0:
            quest = src.quests.questMap["DiscardItemsInside"]()
            return ([quest],None)

        # get storage stockpiles that can be consolidated
        to_consolidate = self.getConsolidatableStockpiles()
        for (item_type,stockpiles) in to_consolidate.items():
            stockpile_to_remove = stockpiles[0]
            stockpile_to_fill = stockpiles[-1]
            quests = []
            quests.append(src.quests.questMap["CleanSpace"](targetPositionBig=stockpile_to_remove[0].getPosition(),targetPosition=stockpile_to_remove[1][0]))
            quests.append(src.quests.questMap["RestockRoom"](targetPositionBig=stockpile_to_fill[0].getPosition(),targetPosition=stockpile_to_fill[1][0],toRestock=item_type,allowAny=True))
            return (reversed(quests),None)

        # collect storage information
        inventory = self.getStored()

        # choose random items as base logic
        total_items = []
        for (item_type,item_list) in inventory.items():
            total_items.extend(item_list)
        item = random.choice(total_items)

        # choose metal bars with priority
        metalBars = inventory.get("MetalBars",[])
        if metalBars:
            item = metalBars[0]

        # choose scrap if possible
        scrap = inventory.get("Scrap",[])
        if scrap:
            item = scrap[0]

        # pick up chosen item
        quest = src.quests.questMap["CleanSpace"](targetPositionBig=item.getBigPosition(),targetPosition=item.getPosition())
        return ([quest],None)

    def getConsolidatableStockpiles(self):
        '''
        get stockpiles that can be consolidated
        '''

        # set up helper variables
        terrain = self.character.getTerrain()
        result = {}

        # fetch half filles storage stockpiles
        for room in terrain.rooms:
            for storageSlot in room.storageSlots:
                if storageSlot[1]:
                    continue
                items = room.getItemByPosition(storageSlot[0])
                if not items:
                    continue
                if items[0].walkable == False:
                    continue
                if len(items) > 25:
                    continue
                if items[0].type not in result:
                    result[items[0].type] = []
                result[items[0].type].append((room,storageSlot))

        # filters item types blocking only one stockpile
        for (item_type, stockpiles) in list(result.items()):
            if len(stockpiles) > 1:
                continue
            del result[item_type]

        # return result
        return result

    def getStored(self):
        '''
        get the items stored on the base
        '''
        terrain = self.character.getTerrain()

        stored = {}
        for room in terrain.rooms:
            for storageSlot in room.storageSlots:
                if storageSlot[1]:
                    continue
                items = room.getItemByPosition(storageSlot[0])
                if not items:
                    continue
                for item in items:
                    if not item.type in stored:
                        stored[item.type] = []
                    stored[item.type].append(item)
        return stored

    def pickedUpItem(self,extraInfo):
        '''
        handle the character having picked up an item
        '''
        self.triggerCompletionCheck(extraInfo[0],dryRun=False)

    def assignToCharacter(self, character):
        '''
        make the quest listen to character events
        '''
        if self.character:
            return None

        self.startWatching(character,self.pickedUpItem, "itemPickedUp")
        return super().assignToCharacter(character)

    @staticmethod
    def generateDutyQuest(beUsefull,character,room, dryRun):
        '''
        generate the quests for the storage management duty
        '''

        # set up helper variables
        terrain = character.getTerrain()

        # enforce storage limits
        stockplaner = None
        for room in terrain.rooms:
            stockplaner = room.getItemByType("StockPlaner",needsBolted=True)
            if stockplaner:
                break
        if stockplaner:
            limit_violations = stockplaner.getStockLimitViolations()
            if limit_violations:
                random.shuffle(limit_violations)
                violation = limit_violations[0]
                quests = []
                quests.append(src.quests.questMap["ClearInventory"]())
                quests.append(src.quests.questMap["FetchItems"](toCollect=violation[0],amount=min(violation[1],10)))
                quests.append(src.quests.questMap["DiscardItemsInside"]())
                return (list(reversed(quests)),None)

        # free up storage
        num_empty_storage = 0
        num_storage = 0
        for room in terrain.rooms:
            storageSlots = room.storageSlots
            for storageSlot in storageSlots:
                if storageSlot[1]:
                    continue
                num_storage += 1
                if room.getItemByPosition(storageSlot[0]):
                    continue
                num_empty_storage += 1
        if num_empty_storage <= 0 and num_storage:
            quest = src.quests.questMap["FreeUpStorage"](amount=5)
            if not dryRun:
                beUsefull.idleCounter = 0
            return ([quest],None)
        return (None,None)

# register the quest
src.quests.addType(FreeUpStorage)

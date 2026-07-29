import random

import src

class FreeUpStorage(src.quests.MetaQuestSequence):
    type = "FreeUpStorage"
    lowLevel = True

    def __init__(self, description="free up storage", creator=None, lifetime=None, reason=None, amount=1):
        self.lastMoveDirection = None
        questList = []
        super().__init__(questList, creator=creator,lifetime=lifetime)
        self.metaDescription = description
        self.reason = reason
        self.amount = amount

    def generateTextDescription(self):
        out = []

        reasonText = (src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),".")
        if self.reason:
            reasonText = [(src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),","),f" to {self.reason}."]

        num_free_storage = self.getNumFreeStorageSlots()
        text = [f"""
""",(src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"""Free up general storage slots"""),reasonText,"""
"""]
        text.append(f"""

This quest will end when {self.amount} general storage slots are free.
Currently {num_free_storage} storage slots are free.""")

        out.append(text)
        return out

    def triggerCompletionCheck(self,character=None,dryRun=True):
        if not character:
            return False
        if self.getNumFreeStorageSlots() >= self.amount:
            if not dryRun:
                self.postHandler()
            return True
        return False

    def getNumFreeStorageSlots(self):
        num_empty_storage = 0
        for room in self.character.getTerrain().rooms:
            for storageSlot in room.storageSlots:
                print(storageSlot)
                if storageSlot[1]:
                    continue
                print("1")
                if room.getItemByPosition(storageSlot[0]):
                    continue
                print("2")
                num_empty_storage += 1
        return num_empty_storage

    def getNextStep(self,character,ignoreCommands=False, dryRun = True):

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

    def getStored(self):
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
        self.triggerCompletionCheck(extraInfo[0],dryRun=False)

    def assignToCharacter(self, character):
        if self.character:
            return None

        self.startWatching(character,self.pickedUpItem, "itemPickedUp")
        return super().assignToCharacter(character)

    @staticmethod
    def generateDutyQuest(beUsefull,character,room, dryRun):
        '''
        generate the quests for the storage management duty
        '''
        terrain = character.getTerrain()
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

src.quests.addType(FreeUpStorage)

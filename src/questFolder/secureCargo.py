import src

class SecureCargo(src.quests.MetaQuestSequence):
    type = "SecureCargo"

    def __init__(self, description="secure cargo"):
        super().__init__()
        self.metaDescription = description

    def generateTextDescription(self):
        return """
The last delivery was ambushed.
Weapons and armor were left.

Go there and fetch those items.
Clear your inventory afterwards to complete this quest.
"""

    def wrapedTriggerCompletionCheck(self, extraInfo):
        self.triggerCompletionCheck(self.character)

    def droppedItem(self,extraInfo):
        self.triggerCompletionCheck(extraInfo[0])

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.wrapedTriggerCompletionCheck, "removed item")
        self.startWatching(character,self.droppedItem, "dropped")

        super().assignToCharacter(character)

    def triggerCompletionCheck(self,character=None):
        if not character:
            return False

        if len(character.inventory) > 0:
            return False

        if not self.getLoot(character):
            character.awardReputation(amount=400, reason="secured the cargo")
            self.postHandler()
            return True

        return False

    def solver(self,character):
        self.triggerCompletionCheck(character)

        if not self.subQuests:
            if not character.getFreeInventorySpace() > 0:
                quest = src.quests.questMap["ClearInventory"](returnToTile=False)
                self.addQuest(quest)
                quest.assignToCharacter(character)
                quest.activate()
                return
            currentTerrain = character.getTerrain()
            targetRooms = currentTerrain.getRoomsByTag("cargo")
            if not targetRooms:
                return
            targetRoom = targetRooms[0]
            if character.container != targetRoom:
                quest = src.quests.questMap["SecureTile"](toSecure=targetRoom.getPosition(),endWhenCleared=True)
                self.addQuest(quest)
                quest.assignToCharacter(character)
                quest.activate()
                return
            item = self.getLoot(character)
            if not item and len(character.inventory) > 0:
                quest = src.quests.questMap["ClearInventory"](returnToTile=False)
                self.addQuest(quest)
                quest.assignToCharacter(character)
                quest.activate()
                return

            self.addQuest(src.quests.questMap["RunCommand"](command="k", description="pick up loot"))
            quest = src.quests.questMap["GoToPosition"](targetPosition=item.getPosition(),description="go to loot")
            self.addQuest(quest)
            quest.assignToCharacter(character)
            quest.activate()
            return

        super().solver(character)

    def getLoot(self,character):
        currentTerrain = character.getTerrain()
        targetRooms = currentTerrain.getRoomsByTag("cargo")
        if not targetRooms:
            self.postHandler()
            return None
        targetRoom = targetRooms[0]

        for item in targetRoom.itemsOnFloor:
            if item.type in ("Sword","Armor"):
                return item

        return None

src.quests.addType(SecureCargo)

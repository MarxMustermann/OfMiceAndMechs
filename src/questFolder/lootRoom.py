import src


class LootRoom(src.quests.MetaQuestSequence):
    type = "LootRoom"

    def __init__(self, description="loot room", roomPos = None):
        super().__init__()
        self.baseDescription = description
        self.metaDescription = self.baseDescription+f" {roomPos}"
        self.roomPos = roomPos

    def generateTextDescription(self):
        return f"""
Loot a room. Take everything that is valuable and bring it home.


Go to the room on tile {self.roomPos} and take everything not bolted and valuable.
Clear your inventory afterwards to complete the quest."""

    def triggerCompletionCheck(self,character=None):
        if not character:
            return False

        if len(character.inventory) > 0:
            return False

        if not self.getLoot(character):
            character.awardReputation(amount=200, reason="looted a room")
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
            if character.getBigPosition() != self.roomPos:
                if len(character.inventory) > 0:
                    quest = src.quests.questMap["ClearInventory"](returnToTile=False)
                    self.addQuest(quest)
                    quest.assignToCharacter(character)
                    quest.activate()
                    return
                quest = src.quests.questMap["SecureTile"](toSecure=self.roomPos,endWhenCleared=True)
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
            self.addQuest(src.quests.questMap["GoToPosition"](targetPosition=item.getPosition(),description="go to loot"))
            return

        super().solver(character)

    def getLoot(self,character):
        currentTerrain = character.getTerrain()
        rooms = currentTerrain.getRoomByPosition(self.roomPos)
        if not rooms:
            return None

        for item in rooms[0].itemsOnFloor:
            if item.type in ("Scrap",):
                continue
            if not item.bolted:
                return item

        return None

    def droppedItem(self,extraInfo):
        self.triggerCompletionCheck(extraInfo[0])

    def assignToCharacter(self, character):
        if self.character:
            return None

        self.startWatching(character,self.droppedItem, "dropped")

        return super().assignToCharacter(character)

src.quests.addType(LootRoom)

import src

class ClearInventory(src.quests.MetaQuestSequence):
    type = "ClearInventory"

    def __init__(self, description="clear inventory", creator=None, targetPosition=None, returnToTile=True):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        self.returnToTile = False
        if returnToTile:
            self.setParameters({"returnToTile":returnToTile})

        self.tileToReturnTo = None

    def generateTextDescription(self):
        return """
You should clear your inventory.

The storage room is a good place to put your items.
Put the items into the stockpiles to make then accessible to the base.



To see your items open the your inventory by pressing i."""

    def droppedItem(self,extraInfo):
        self.triggerCompletionCheck(extraInfo[0])

    def handleTileChange(self):
        self.triggerCompletionCheck(self.character)

    def activate(self):
        if self.character:
            if self.returnToTile and not self.tileToReturnTo:
                self.tileToReturnTo = self.character.getBigPosition()
            self.triggerCompletionCheck(self.character)
        super().activate()

    def assignToCharacter(self, character):
        if self.character:
            return
        
        self.startWatching(character,self.droppedItem, "dropped")
        self.startWatching(character,self.handleTileChange, "changedTile")

        if self.active:
            if self.returnToTile and not self.tileToReturnTo:
                self.tileToReturnTo = character.getBigPosition()
            self.triggerCompletionCheck(character)
        return super().assignToCharacter(character)

    def triggerCompletionCheck(self,character=None):
        if not character:
            return

        if not character.inventory:
            if self.returnToTile and not character.getBigPosition() == self.tileToReturnTo:
                return
            self.postHandler()
            return
        return

    def solver(self, character):
        self.triggerCompletionCheck(character)

        if self.returnToTile and not self.tileToReturnTo:
            self.tileToReturnTo = character.getBigPosition()

        if not self.subQuests:
            if not isinstance(character.container,src.rooms.Room):
                if character.yPosition%15 == 14:
                    character.runCommandString("w")
                    return
                if character.yPosition%15 == 0:
                    character.runCommandString("s")
                    return
                if character.xPosition%15 == 14:
                    character.runCommandString("a")
                    return
                if character.xPosition%15 == 0:
                    character.runCommandString("d")
                    return


            # clear inventory local
            room = character.getRoom()
            if len(character.inventory) and room:
                emptyInputSlots = room.getEmptyInputslots(character.inventory[-1].type, allowAny=True)
                print(emptyInputSlots)
                if emptyInputSlots:
                    quest = src.quests.questMap["RestockRoom"](toRestock=character.inventory[-1].type, allowAny=True)
                    self.addQuest(quest)
                    quest.assignToCharacter(character)
                    quest.activate()
                    return True

            if not "HOMEx" in character.registers:
                return True

            if character.inventory:
                homeRoom = character.getHomeRoom()

                if not hasattr(homeRoom,"storageRooms") or not homeRoom.storageRooms:
                    return True
                quest = src.quests.questMap["GoToTile"](targetPosition=(homeRoom.storageRooms[0].xPosition,homeRoom.storageRooms[0].yPosition,0))
                self.addQuest(quest)
                quest.assignToCharacter(character)
                quest.activate()
                return True

            if self.returnToTile and not character.getBigPosition() == self.returnToTile:
                quest = src.quests.questMap["GoToTile"](targetPosition=self.tileToReturnTo)
                self.addQuest(quest)
                quest.assignToCharacter(character)
                quest.activate()
                return True

            return False

        super().solver(character)

    def setParameters(self,parameters):
        if "returnToTile" in parameters and "returnToTile" in parameters:
            self.returnToTile = parameters["returnToTile"]
        return super().setParameters(parameters)

src.quests.addType(ClearInventory)

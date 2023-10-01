import src

class ClearInventory(src.quests.MetaQuestSequence):
    type = "ClearInventory"

    def __init__(self, description="clear inventory", creator=None, targetPosition=None, returnToTile=True,tryHard=False,reason=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        self.returnToTile = False
        self.tryHard = tryHard
        self.reason = reason
        if returnToTile:
            self.setParameters({"returnToTile":returnToTile})

        self.tileToReturnTo = None

    def generateTextDescription(self):
        reason = ""
        if self.reason:
            reason += f", to {self.reason}"
        text = f"""
Clear your inventory{reason}.

The storage room is a good place to put your items.
Put the items into the stockpiles to make then accessible to the base.

To see your items open the your inventory by pressing i."""
        return text

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
            if self.returnToTile and character.getBigPosition() != self.tileToReturnTo:
                return
            self.postHandler()
            return
        return

    def getSolvingCommandString(self, character, dryRun=True):
        nextStep = self.getNextStep(character)
        if nextStep == (None,None):
            return super().getSolvingCommandString(character)
        return self.getNextStep(character)[1]

    def solver(self, character):
        (nextQuests,nextCommand) = self.getNextStep(character,dryRun=False)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
            return

        if nextCommand:
            character.runCommandString(nextCommand)
            return
        super().solver(character)

    def getNextStep(self,character=None,ignoreCommands=False,dryRun=True):
        if self.returnToTile and not self.tileToReturnTo:
            self.tileToReturnTo = character.getBigPosition()

        if not self.subQuests:
            if not isinstance(character.container,src.rooms.Room):
                if character.yPosition%15 == 14:
                    return (None,("w","enter tile"))
                if character.yPosition%15 == 0:
                    return (None,("s","enter tile"))
                if character.xPosition%15 == 14:
                    return (None,("a","enter tile"))
                if character.xPosition%15 == 0:
                    return (None,("d","enter tile"))

                if "HOMEx" in character.registers:
                    quest = src.quests.questMap["GoHome"]()
                    return ([quest],None)

                return (None,("l","drop item"))

            # clear inventory local
            room = character.getRoom()
            if len(character.inventory) and room:
                emptyInputSlots = room.getEmptyInputslots(character.inventory[-1].type, allowAny=True)
                if emptyInputSlots:
                    quest = src.quests.questMap["RestockRoom"](toRestock=character.inventory[-1].type, allowAny=True, reason="remove items from your inventory")
                    return ([quest],None)

            if not "HOMEx" in character.registers:
                self.fail(reason="no home")
                return (None,None)

            if character.inventory:
                homeRoom = character.getHomeRoom()

                if hasattr(homeRoom,"storageRooms") and homeRoom.storageRooms:
                    quest = src.quests.questMap["GoToTile"](targetPosition=(homeRoom.storageRooms[0].xPosition,homeRoom.storageRooms[0].yPosition,0),reason="go to a storage room")
                    return ([quest],None)

                for checkRoom in character.getTerrain().rooms:
                    emptyInputSlots = checkRoom.getEmptyInputslots(character.inventory[-1].type, allowAny=True)
                    if emptyInputSlots:
                        quest1 = src.quests.questMap["GoToTile"](targetPosition=checkRoom.getPosition(),reason="go to a room with empty stockpiles")
                        quest2 = src.quests.questMap["RestockRoom"](toRestock=character.inventory[-1].type, allowAny=True, reason="to remove items from your inventory")
                        return ([quest2,quest1],None)

                if not "HOMEx" in character.registers:
                    self.fail(reason="no home")
                    return (None,None)

                if not dryRun:
                    character.timeTaken += 1
                    self.fail(reason="no storage available")
                return (None,None)

            if self.returnToTile and character.getBigPosition() != self.returnToTile:
                quest = src.quests.questMap["GoToTile"](description="return to tile",targetPosition=self.tileToReturnTo,reason="get back where your inventory was filled up")
                return ([quest],None)

        return (None,None)

    def setParameters(self,parameters):
        if "returnToTile" in parameters and "returnToTile" in parameters:
            self.returnToTile = parameters["returnToTile"]
        return super().setParameters(parameters)

src.quests.addType(ClearInventory)

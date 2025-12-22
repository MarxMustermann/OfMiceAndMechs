import src


class ClearInventory(src.quests.MetaQuestSequence):
    '''
    quest to clear a characters inventory
    '''
    type = "ClearInventory"
    lowLevel = True
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
        '''
        generates a textual description
        '''
        reason = ""
        if self.reason:
            reason += f", to {self.reason}"
        text = f"""
Clear your inventory{reason}.

The storage room is a good place to put your items.
Put the items into the stockpiles to make then accessible to the base.

To see your items open the your inventory by pressing i."""

        if self.returnToTile:
            if not self.tileToReturnTo:
                text += "\n\nReturn to your current position afterwards."
            else:
                text += f"\n\nReturn to the tile {self.tileToReturnTo} afterwards."
            
        return text

    def droppedItem(self,extraInfo):
        '''
        handle the character having dropped an item
        '''
        self.triggerCompletionCheck(extraInfo[0],dryRun=False)

    def handleTileChange(self,extraInfo=None):
        '''
        hande the character having moved
        '''
        self.triggerCompletionCheck(self.character,dryRun=False)

    def activate(self):
        '''
        start to actually be active
        '''
        if self.character:
            if self.returnToTile and not self.tileToReturnTo:
                self.tileToReturnTo = self.character.getBigPosition()
            self.triggerCompletionCheck(self.character,dryRun=False)
        super().activate()

    def assignToCharacter(self, character):
        '''
        assign this quest to a character
        '''
        if self.character:
            return None

        self.startWatching(character,self.droppedItem, "dropped")
        self.startWatching(character,self.handleTileChange, "changedTile")

        if self.active:
            if self.returnToTile and not self.tileToReturnTo:
                self.tileToReturnTo = character.getBigPosition()
            self.triggerCompletionCheck(character,dryRun=False)
        return super().assignToCharacter(character)

    def triggerCompletionCheck(self,character=None,dryRun=True):
        '''
        check if this quest is completed
        '''
        if not character:
            return False

        if not character.inventory:
            if self.returnToTile and character.getBigPosition() != self.tileToReturnTo:
                return False
            self.postHandler()
            return True
        return False

    def getNextStep(self,character=None,ignoreCommands=False,dryRun=True):
        '''
        calculate the next step towards solving the quest
        '''

        # remember current position as place to return to
        if self.returnToTile and not self.tileToReturnTo:
            self.tileToReturnTo = character.getBigPosition()

        # handle weird edge cases
        if self.subQuests:
            return (None,None)

        # fail on danger
        if character.getNearbyEnemies():
            return self._solver_trigger_fail(dryRun, "nearby enemies")

        # close other menus
        if not ignoreCommands and character.macroState.get("submenue"):
            return (None,(["esc"],"exit submenu"))

        # handle weird edge cases
        if not isinstance(character.container,src.rooms.Room):

            # enter rooms properly
            if character.yPosition%15 == 14:
                return (None,("w","enter tile"))
            if character.yPosition%15 == 0:
                return (None,("s","enter tile"))
            if character.xPosition%15 == 14:
                return (None,("a","enter tile"))
            if character.xPosition%15 == 0:
                return (None,("d","enter tile"))

            # just drop items somewhere
            if not "HOMEx" in character.registers:
                return (None,("l","drop item"))

        # clear inventory in local room
        room = character.getRoom()
        if len(character.inventory) and room:
            emptyInputSlots = room.getEmptyInputslots(character.inventory[-1].type, allowAny=True)
            if emptyInputSlots:
                quest = src.quests.questMap["RestockRoom"](toRestock=character.inventory[-1].type, allowAny=True, reason="reduce the number of items in your inventory")
                return ([quest],None)

        # fail if there is no home
        if "HOMEx" not in character.registers:
            return self._solver_trigger_fail(dryRun,"no home")

        # get rid of the items
        if character.inventory:

            homeRoom = character.getHomeRoom()
            if not homeRoom:
                return self._solver_trigger_fail(dryRun,"no home")
            if hasattr(homeRoom,"storageRooms") and homeRoom.storageRooms:
                quest = src.quests.questMap["GoToTile"](targetPosition=(homeRoom.storageRooms[0].xPosition,homeRoom.storageRooms[0].yPosition,0),reason="go to a storage room")
                return ([quest],None)

            # restock rooms if possible
            for checkRoom in character.getTerrain().rooms:
                emptyInputSlots = checkRoom.getEmptyInputslots(character.inventory[-1].type, allowAny=True)
                if emptyInputSlots:
                    quest1 = src.quests.questMap["GoToTile"](targetPosition=checkRoom.getPosition(),reason="go to a room with empty stockpiles")
                    quest2 = src.quests.questMap["RestockRoom"](toRestock=character.inventory[-1].type, allowAny=True, reason="reduce the number of item in your inventory")
                    return ([quest2,quest1],None)

            # just get rid of items
            if not character.getTerrain().alarm:
                quest = src.quests.questMap["DropItemsOutside"]()
                return ([quest],None)
            else:
                quest = src.quests.questMap["DiscardItemsInside"]()
                return ([quest],None)
            return self._solver_trigger_fail(dryRun,"no storage available")

        # return back to original position
        if self.returnToTile and character.getBigPosition() != self.returnToTile:
            quest = src.quests.questMap["GoToTile"](description="return to tile",targetPosition=self.tileToReturnTo,reason="get back where your inventory was filled up")
            return ([quest],None)

        # end quest
        if not dryRun:
            self.postHandler()
        return (None,("+","end quest"))

    def setParameters(self,parameters):
        '''
        set dict based parameters (obsolete?)
        '''
        if "returnToTile" in parameters and "returnToTile" in parameters:
            self.returnToTile = parameters["returnToTile"]
        return super().setParameters(parameters)

    @staticmethod
    def generateDutyQuest(beUsefull,character,room, dryRun):
        '''
        generate the tasks for cleaning duty
        '''
        if len(character.inventory) > 9:
            quest = src.quests.questMap["ClearInventory"]()
            if not dryRun:
                beUsefull.idleCounter = 0
            return ([quest],None)

        # clear inventory local
        if len(character.inventory) > 1 and character.container.isRoom:
            emptyInputSlots = character.container.getEmptyInputslots(character.inventory[-1].type, allowAny=True)
            if emptyInputSlots:
                quest = src.quests.questMap["RestockRoom"](toRestock=character.inventory[-1].type, allowAny=True,reason="clear your inventory")
                if not dryRun:
                    beUsefull.idleCounter = 0
                return ([quest],None)

        # go to garbage stockpile and unload
        if len(character.inventory) > 6:
            if "HOMEx" not in character.registers:
                if not dryRun:
                    beUsefull.idleCounter = 0
                return (None,None)
            homeRoom = character.getHomeRoom()
            if not hasattr(homeRoom,"storageRooms") or not homeRoom.storageRooms:
                return (None,None)

            quest = src.quests.questMap["GoToTile"](targetPosition=(homeRoom.storageRooms[0].xPosition,homeRoom.storageRooms[0].yPosition,0))
            if not dryRun:
                beUsefull.idleCounter = 0
            return ([quest],None)
        if len(character.inventory) > 9:
            quest = src.quests.questMap["ClearInventory"]()
            if not dryRun:
                beUsefull.idleCounter = 0
            return ([quest],None)
        return (None,None)

# register item type
src.quests.addType(ClearInventory)

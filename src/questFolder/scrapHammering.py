import src


class ScrapHammering(src.quests.MetaQuestSequence):
    type = "ScrapHammering"

    def __init__(self, description="scrap hammering", creator=None, reason=None, amount=None,produceToInventory=False, tryHard=False):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        self.reason = reason
        self.amount = amount
        self.amountDone = 0
        self.produceToInventory = produceToInventory
        self.tryHard = tryHard

    def generateTextDescription(self):
        reason = ""
        if self.reason:
            reason = f", to {self.reason}"
        return f"""
Do some scrap hammering{reason}.

Hammer {self.amount} Scrap to MetalBars. {self.amountDone} done.
"""

    def triggerCompletionCheck(self,character=None, dryRun=True):
        if not character:
            return False

        return False

    def getNextStep(self,character,ignoreCommands=False, dryRun = True):
        '''
        get the next step towards solving the quest
        '''

        # let subquests complete first
        if self.subQuests:
            return (None,None)

        # enter tile properly
        if not character.container.isRoom:
            pos = character.getSpacePosition()
            if pos == (14,7,0):
                return (None,("a","enter room"))
            if pos == (0,7,0):
                return (None,("d","enter room"))
            if pos == (7,14,0):
                return (None,("w","enter room"))
            if pos == (7,0,0):
                return (None,("s","enter room"))

        # navigate menues
        submenue = character.macroState.get("submenue")
        if submenue and not ignoreCommands:

            # use menu to set how much scrap to produce
            if submenue.tag == "anvilAmountInput":
                targetAmount = str(self.amount - self.amountDone)
                command = submenue.get_command_to_input(str(targetAmount))
                return (None,(command,"enter how much to produce"))

            # select to produce scrap on the anvil
            if submenue.tag == "applyOptionSelection" and submenue.extraInfo.get("item").type == "Anvil":
                activation_command = "k"
                if self.produceToInventory:
                    activation_command = "j"
                if self.amount-self.amountDone > 1:
                    activation_command = activation_command.upper()
                command = submenue.get_command_to_select_option("produce item",selectionCommand=activation_command)
                if command:
                    return (None,(command,"hammer scrap"))

            # exit othe menues
            return (None,(["esc"],"exit submenu"))

        # handle bump item activation
        action = self.generate_confirm_interaction_command(allowedItems=["Anvil"])
        if action:
            return action

        # get local anvils
        anvils = []
        if character.container.isRoom:
            anvils.extend(character.container.getItemsByType("Anvil"))

        # go to room with anvils
        if not anvils:
            for room in character.getTerrain().rooms:
                for item in room.getItemsByType("Anvil"):
                    if not item.bolted:
                        continue
                    quest = src.quests.questMap["GoToTile"](targetPosition=room.getPosition(),reason="go to a room with a Anvil")
                    return ([quest],None)

            return self._solver_trigger_fail(dryRun,"no anvil available")

        # get anvils right next to the character
        anvilNearBy = None
        for anvil in anvils:
            if not character.getDistance(anvil.getPosition()) > 1:
                anvilNearBy = anvil
                break

        # go to an anvil
        if not anvilNearBy:
            quest = src.quests.questMap["GoToPosition"](targetPosition=anvils[0].getPosition(),ignoreEndBlocked=True,reason="go to an anvil")
            return ([quest],None)

        # activate anvil
        pos = character.getPosition()
        anvilPos = anvilNearBy.getPosition()
        if (pos[0],pos[1],pos[2]) == anvilPos:
            return (None,("j","hammer some scrap"))
        if (pos[0]-1,pos[1],pos[2]) == anvilPos:
            return (None,("aj","hammer some scrap"))
        if (pos[0]+1,pos[1],pos[2]) == anvilPos:
            return (None,("dj","hammer some scrap"))
        if (pos[0],pos[1]-1,pos[2]) == anvilPos:
            return (None,("wj","hammer some scrap"))
        if (pos[0],pos[1]+1,pos[2]) == anvilPos:
            return (None,("sj","hammer some scrap"))

        # fail
        return self._solver_trigger_fail(dryRun,"impossible state")

    def handleQuestFailure(self,extraParam):

        # handle weird edge cases
        if extraParam["quest"] not in self.subQuests:
            return

        # remove completed quests
        self.subQuests.remove(extraParam["quest"])

        # set up helper variables
        quest = extraParam["quest"]
        reason = extraParam.get("reason")

        # collect missing scrap
        if (reason and reason.startswith("no source for item Scrap") and 
                (self.tryHard or "resource gathering" in self.character.duties) and 
                (not self.character.getTerrain().alarm or self.tryHard) ):
            newQuest = src.quests.questMap["GatherScrap"](reason="have some scrap to hammer",tryHard=self.tryHard)
            self.addQuest(newQuest)
            self.startWatching(quest,self.handleQuestFailure,"failed")
            return

        # fail recursively
        self.fail(reason)

    def handleHammeredScrap(self, extraInfo):

        # handle weird edge cases
        if self.completed:
            1/0
        if not self.active:
            return

        # register that a metal bar was completed
        self.amountDone += 1
        if self.amount is not None and self.amountDone >= self.amount:
            self.postHandler()

    def handleInventoryFull(self, extraInfo):

        # handle weird edge cases
        if self.completed:
            1/0
        if not self.active:
            return

        # clear inventory if needed
        quest = src.quests.questMap["ClearInventory"](reason="be able to carry more metal bars")
        self.startWatching(quest,self.handleQuestFailure,"failed")
        self.addQuest(quest)

    def handleNoScrap(self, extraInfo):

        # handle weird edge cases
        if self.completed:
            1/0
        if not self.active:
            return

        # fetch scrap if needed
        quest = src.quests.questMap["FetchItems"](toCollect="Scrap",amount=1,reason="have some scrap to hammer")
        self.startWatching(quest,self.handleQuestFailure,"failed")
        self.addQuest(quest)

    def assignToCharacter(self, character):

        # handle weird edge cases
        if self.character:
            return None

        # register to listen for events
        self.startWatching(character,self.handleHammeredScrap, "hammered scrap")
        self.startWatching(character,self.handleInventoryFull, "inventory full error")
        self.startWatching(character,self.handleNoScrap, "no scrap error")

        # do super class stuff
        return super().assignToCharacter(character)

    def getQuestMarkersSmall(self,character,renderForTile=False):
        '''
        return the quest markers for the normal map
        '''

        # do nothing if wrong scale is requested
        if isinstance(character.container,src.rooms.Room):
            if renderForTile:
                return []
        else:
            if not renderForTile:
                return []

        # highlight anvils
        result = super().getQuestMarkersSmall(character,renderForTile=renderForTile)
        if not renderForTile:
            if isinstance(character.container,src.rooms.Room):
                for item in character.container.itemsOnFloor:
                    if not item.type == "Anvil":
                        continue
                    if not item.bolted:
                        continue
                    result.append((item.getPosition(),"target"))
        return result

    @staticmethod
    def generateDutyQuest(beUsefull,character,currentRoom, dryRun):

        # do planned production
        hasReadyAnvil = False
        for room in beUsefull.getRandomPriotisedRooms(character,currentRoom):
            for anvil in room.getItemsByType("Anvil"):
                if not anvil.checkForInputScrap(character):
                    continue
                hasReadyAnvil = True
                if anvil.scheduledAmount:
                    quest = src.quests.questMap["ScrapHammering"](amount=min(10,anvil.scheduledAmount,reason="do planned production"))
                    if not dryRun:
                        beUsefull.idleCounter = 0
                    return ([quest],None)

        # do nothing in case of no anvil
        if not hasReadyAnvil:
            return (None,None)

        # ensure some stock of metal bars
        itemsInStorage = {}
        freeStorage = 0
        for room in character.getTerrain().rooms:
            for storageSlot in room.storageSlots:
                items = room.getItemByPosition(storageSlot[0])
                if not items:
                    freeStorage += 1
                for item in items:
                    itemsInStorage[item.type] = itemsInStorage.get(item.type,0)+1
        if freeStorage and itemsInStorage.get("MetalBars",0) < 40:
            quest = src.quests.questMap["ScrapHammering"](amount=10,reason="ensure minimal stock of MetalBars")
            if not dryRun:
                beUsefull.idleCounter = 0
            return ([quest],None)

        # do nothing
        return (None,None)

# register quest type
src.quests.addType(ScrapHammering)

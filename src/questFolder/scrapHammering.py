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

    def triggerCompletionCheck(self,character=None):
        if not character:
            return False

        return False

    def getNextStep(self,character,ignoreCommands=False, dryRun = True):
        if self.subQuests:
            return (None,None)

        if character.macroState["submenue"] and isinstance(character.macroState["submenue"],src.menuFolder.selectionMenu.SelectionMenu) and not ignoreCommands:
            submenue = character.macroState["submenue"]
        
            index = None
            counter = 1
            for option in submenue.options.items():
                if option[1] == "produce item":
                    index = counter
                    break
                counter += 1

            if index is None:
                index = counter-1

            if self.produceToInventory:
                activationCommand = "j"
            else:
                activationCommand = "k"

            offset = index-submenue.selectionIndex
            command = ""
            if offset > 0:
                command += "s"*offset
            else:
                command += "w"*(-offset)
            command += activationCommand
            return (None,(command,"hammer scrap"))

        if character.macroState["submenue"] and not ignoreCommands:
            return (None,(["esc"],"exit submenu"))

        if character.macroState.get("itemMarkedLast"):
            if character.macroState["itemMarkedLast"].type == "Anvil":
                return (None,("j","activate anvil"))
            else:
                return (None,(".","undo selection"))

        if character.getBigPosition() != (7, 7, 0):
            quest = src.quests.questMap["GoToTile"](targetPosition=(7,7,0),reason="go to anvil")
            return ([quest],None)

        anvils = []
        if character.container.isRoom:
            anvils.extend(character.container.getItemsByType("Anvil"))
        if not character.container.isRoom:
            return ([src.quests.questMap["EnterRoom"]],None)

        anvilNearBy = None
        for anvil in anvils:
            if not character.getDistance(anvil.getPosition()) > 1:
                anvilNearBy = anvil
                break

        if not anvilNearBy:
            quest = src.quests.questMap["GoToPosition"](targetPosition=anvils[0].getPosition(),ignoreEndBlocked=True,reason="go to an anvil")
            return ([quest],None)

        pos = character.getPosition()
        anvilPos = anvilNearBy.getPosition()
        if self.produceToInventory:
            activationCommand = "j"
        else:
            activationCommand = "k"
        if (pos[0],pos[1],pos[2]) == anvilPos:
            return (None,("j"+activationCommand,"hammer some scrap"))
        if (pos[0]-1,pos[1],pos[2]) == anvilPos:
            return (None,("aj"+activationCommand,"hammer some scrap"))
        if (pos[0]+1,pos[1],pos[2]) == anvilPos:
            return (None,("dj"+activationCommand,"hammer some scrap"))
        if (pos[0],pos[1]-1,pos[2]) == anvilPos:
            return (None,("wj"+activationCommand,"hammer some scrap"))
        if (pos[0],pos[1]+1,pos[2]) == anvilPos:
            return (None,("sj"+activationCommand,"hammer some scrap"))

        return (None,None)


    def handleQuestFailure(self,extraParam):
        if extraParam["quest"] not in self.subQuests:
            return

        self.subQuests.remove(extraParam["quest"])

        quest = extraParam["quest"]

        try:
            self.tryHard
        except:
            self.tryHard = False

        reason = extraParam.get("reason")
        if (reason and reason.startswith("no source for item Scrap") and 
                (self.tryHard or "resource gathering" in self.character.duties) and 
                (not self.character.getTerrain().alarm or self.tryHard) ):
            newQuest = src.quests.questMap["GatherScrap"](reason="have some scrap to hammer",tryHard=self.tryHard)
            self.addQuest(newQuest)
            self.startWatching(quest,self.handleQuestFailure,"failed")
            return

        self.fail(reason)

    def handleHammeredScrap(self, extraInfo):
        if self.completed:
            1/0
        if not self.active:
            return

        self.amountDone += 1
        if self.amount is not None and self.amountDone >= self.amount:
            self.postHandler()

    def handleInventoryFull(self, extraInfo):
        if self.completed:
            1/0
        if not self.active:
            return

        quest = src.quests.questMap["ClearInventory"]()
        self.startWatching(quest,self.handleQuestFailure,"failed")
        self.addQuest(quest)

    def handleNoScrap(self, extraInfo):
        if self.completed:
            1/0
        if not self.active:
            return

        quest = src.quests.questMap["FetchItems"](toCollect="Scrap",amount=1,reason="have some scrap to hammer")
        self.startWatching(quest,self.handleQuestFailure,"failed")
        self.addQuest(quest)

    def assignToCharacter(self, character):
        if self.character:
            return None

        self.startWatching(character,self.handleHammeredScrap, "hammered scrap")
        self.startWatching(character,self.handleInventoryFull, "inventory full error")
        self.startWatching(character,self.handleNoScrap, "no scrap error")

        return super().assignToCharacter(character)

    @staticmethod
    def generateDutyQuest(beUsefull,character,currentRoom, dryRun):
        hasReadyAnvil = False
        for room in beUsefull.getRandomPriotisedRooms(character,currentRoom):
            for anvil in room.getItemsByType("Anvil"):
                if not anvil.checkForInputScrap():
                    continue

                hasReadyAnvil = True
                if anvil.scheduledItems:
                    quest = src.quests.questMap["ScrapHammering"](amount=min(10,len(anvil.scheduledItems)))
                    if not dryRun:
                        beUsefull.idleCounter = 0
                    return ([quest],None)

        if not hasReadyAnvil:
            return (None,None)

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
            quest = src.quests.questMap["ScrapHammering"](amount=10)
            if not dryRun:
                beUsefull.idleCounter = 0
            return ([quest],None)
        return (None,None)

src.quests.addType(ScrapHammering)

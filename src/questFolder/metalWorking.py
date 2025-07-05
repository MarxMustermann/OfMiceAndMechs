import src
import random

class MetalWorking(src.quests.MetaQuestSequence):
    '''
    quest to produce ingame item using metal working

    Parameters:
        description: the description of the quest to show in the UI
        creator: the entity creating the object (obsolete?)
        reason: the reason for assigning the quest to be shown in the UI
        toProduce: the item type to produce
        amount: the amount of items to produce
        produceToInventory: prefer to put the produced Item into your inventory
        tryHard: try eveerythin possible to complete this quest
    '''
    type = "MetalWorking"
    def __init__(self, description="metal working", creator=None, reason=None, toProduce=None, amount=None, produceToInventory=False,tryHard=False):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description + " " + str(toProduce)
        self.reason = reason
        self.toProduce = toProduce
        self.amount = amount
        self.amountDone = 0
        self.produceToInventory = produceToInventory
        self.tryHard = tryHard

    def generateTextDescription(self):
        reason = ""
        if self.reason:
            reason = f", to {self.reason}"
        out = f"""
Do some metal working{reason}.

Produce {self.amount} {self.toProduce}. {self.amountDone} done.

"""

        out = [out]
        if not self.subQuests:
            out.append((src.interaction.urwid.AttrSpec("#f00", "black"),"""
This quest has no subquests. Press r to generate subquests for this quest."""))
        else:
            out.append((src.interaction.urwid.AttrSpec("#080", "black"),"""
This quests has subquests.
Press d to move the cursor and show the subquests description.
"""))
        return out

    def triggerCompletionCheck(self,character=None):
        if not character:
            return False

        if character.getNearbyEnemies():
            self.fail("enemies nearby")
            return True

        return False

    def getNextStep(self,character,ignoreCommands=False,dryRun=True):
        if self.subQuests:
            return (None,None)

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

        if character.macroState["submenue"] and character.macroState["submenue"].tag == "metalWorkingProductInput":
            submenue = character.macroState["submenue"]
            if self.toProduce == submenue.text:
                return (None,(["enter"],"set the name of the item to produce"))

            correctIndex = 0
            while correctIndex < len(self.toProduce) and correctIndex < len(submenue.text):
                if self.toProduce[correctIndex] != submenue.text[correctIndex]:
                    break
                correctIndex += 1

            if correctIndex < len(submenue.text):
                return (None,(["backspace"],"delete input"))

            return (None,(self.toProduce[correctIndex:],"enter name of the tem to produce"))

        if character.macroState["submenue"] and character.macroState["submenue"].tag == "metalWorkingAmountInput":
            submenue = character.macroState["submenue"]
            targetAmount = str(self.amount - self.amountDone)
            if submenue.text == targetAmount:
                return (None,(["enter"],"set how many of the item to produce"))

            correctIndex = 0
            while correctIndex < len(targetAmount) and correctIndex < len(submenue.text):
                if targetAmount[correctIndex] != submenue.text[correctIndex]:
                    break
                correctIndex += 1

            if correctIndex < len(submenue.text):
                return (None,(["backspace"],"delete input"))

            return (None,(targetAmount[correctIndex:],"enter name of the tem to produce"))

        if character.macroState["submenue"] and isinstance(character.macroState["submenue"],src.menuFolder.selectionMenu.SelectionMenu) and not ignoreCommands:
            submenue = character.macroState["submenue"]
            if submenue.tag == "metalWorkingProductSelection":
                index = None
                counter = 1
                for option in submenue.options.items():
                    if option[1] == self.toProduce:
                        index = counter
                        break
                    counter += 1

                if index is None:
                    index = counter-1

                if self.produceToInventory:
                    activationCommand = "j"
                else:
                    activationCommand = "k"

                if self.amount - self.amountDone > 1:
                    activationCommand = activationCommand.upper()

                offset = index-submenue.selectionIndex
                command = ""
                if offset > 0:
                    command += "s"*offset
                else:
                    command += "w"*(-offset)
                command += activationCommand
                return (None,(command,"produce item"))
            else:
                submenue = character.macroState["submenue"]

                if not submenue.extraInfo.get("item"):
                    return (None,(["esc"],"exit submenu"))

                menuEntry = "produce item"
                if submenue.extraInfo.get("item").lastProduction == self.toProduce:
                    menuEntry = "repeat"
                counter = 1
                for option in submenue.options.values():
                    if option == menuEntry:
                        index = counter
                        break
                    counter += 1
                command = ""
                if submenue.selectionIndex > counter:
                    command += "w"*(submenue.selectionIndex-counter)
                if submenue.selectionIndex < counter:
                    command += "s"*(counter-submenue.selectionIndex)

                if submenue.extraInfo.get("item").lastProduction == self.toProduce and (self.amount-self.amountDone > 1):
                    command += "J"
                else:
                    command += "j"
                return (None,(command,"start producing items"))

        if character.macroState["submenue"] and not ignoreCommands:
            return (None,(["esc"],"exit submenu"))

        if character.macroState.get("itemMarkedLast"):
            if character.macroState["itemMarkedLast"].type == "MetalWorkingBench":
                return (None,("j","activate metal working bench"))
            else:
                return (None,(".","undo selection"))

        if character.getBigPosition() != character.getHomeRoomCord():
            quest = src.quests.questMap["GoToTile"](targetPosition=character.getHomeRoomCord(),reason="go to anvil")
            return ([quest],None)

        benches = []
        if character.container.isRoom:
            benches.extend(character.container.getItemsByType("MetalWorkingBench"))

        benchNearBy = None
        for bench in benches:
            if not character.getDistance(bench.getPosition()) > 1:
                benchNearBy = bench
                break

        if not benchNearBy:
            if not benches:
                if not dryRun:
                    self.fail("no metal bench available")
                return (None,None)
            quest = src.quests.questMap["GoToPosition"](targetPosition=benches[0].getPosition(),ignoreEndBlocked=True,reason="go to a MetalWorkingBench")
            return ([quest],None)

        pos = character.getPosition()
        benchPos = benchNearBy.getPosition()

        if (pos[0],pos[1],pos[2]) == benchPos:
            return (None,("j","start metal working"))
        if (pos[0]-1,pos[1],pos[2]) == benchPos:
            return (None,("aj","start metal working"))
        if (pos[0]+1,pos[1],pos[2]) == benchPos:
            return (None,("dj","start metal working"))
        if (pos[0],pos[1]-1,pos[2]) == benchPos:
            return (None,("wj","start metal working"))
        if (pos[0],pos[1]+1,pos[2]) == benchPos:
            return (None,("sj","start metal working"))

        return (None,None)

    def handleQuestFailure(self,extraParam):
        if extraParam["quest"] not in self.subQuests:
            return

        self.subQuests.remove(extraParam["quest"])

        quest = extraParam["quest"]

        reason = extraParam.get("reason")
        if reason and reason.startswith("no source for item MetalBars") and (self.tryHard or "scrap hammering" in self.character.duties):
            newQuest = src.quests.questMap["ScrapHammering"](amount=self.amount,produceToInventory=True,tryHard=self.tryHard)
            self.addQuest(newQuest)
            self.startWatching(newQuest,self.handleQuestFailure,"failed")
            return

        self.fail(reason)

    def handleWorkedMetal(self, extraInfo):
        if self.completed:
            1/0
        if not self.active:
            return

        if self.toProduce != extraInfo["item"].type:
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

    def handleNoMetalBars(self, extraInfo):
        if self.completed:
            1/0
        if not self.active:
            return

        quest = src.quests.questMap["FetchItems"](toCollect="MetalBars",amount=1,reason="have MetalBars to work with")
        self.startWatching(quest,self.handleQuestFailure,"failed")
        self.addQuest(quest)

    def assignToCharacter(self, character):
        if self.character:
            return None

        self.startWatching(character,self.handleWorkedMetal, "worked metal")
        self.startWatching(character,self.handleInventoryFull, "inventory full error")
        self.startWatching(character,self.handleNoMetalBars, "no metalBars error")

        return super().assignToCharacter(character)

    @staticmethod
    def generateDutyQuest(beUsefull,character,currentRoom, dryRun):
        freeMetalWorkingBenches = []

        for room in beUsefull.getRandomPriotisedRooms(character,currentRoom):
            for metalWorkingBench in room.getItemsByType("MetalWorkingBench"):
                if not metalWorkingBench.readyToUse():
                    continue

                freeMetalWorkingBenches.append(metalWorkingBench)

        random.shuffle(freeMetalWorkingBenches)
        for metalWorkingBench in freeMetalWorkingBenches:
            if metalWorkingBench.scheduledItems:
                quests = [src.quests.questMap["ClearInventory"](),
                          src.quests.questMap["MetalWorking"](amount=1,toProduce=metalWorkingBench.scheduledItems[0])]
                if not dryRun:
                    beUsefull.idleCounter = 0
                return (quests,None)

        if not freeMetalWorkingBenches:
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
            for outputSlot in room.outputSlots:
                items = room.getItemByPosition(outputSlot[0])
                for item in items:
                    itemsInStorage[item.type] = itemsInStorage.get(item.type,0)+1

        if freeStorage:

            for room in character.getTerrain().rooms:
                for buildSite in room.buildSites:
                    if buildSite[1] == "Machine":
                        continue
                    if buildSite[1] in itemsInStorage:
                        continue
                    quests = [src.quests.questMap["ClearInventory"](returnToTile=False),
                              src.quests.questMap["MetalWorking"](toProduce=buildSite[1],amount=1,produceToInventory=False)]
                    return (quests,None)

            checkItems = [("RoomBuilder",1,1),("Door",1,1),("Wall",1,1),("Painter",1,1),("ScrapCompactor",1,1),("Case",1,1),("Frame",1,1),("Rod",1,1),("MaggotFermenter",1,1),("Sword",1,1),("Armor",1,1),("Bolt",10,5),("Vial",1,1),("CoalBurner",1,1),("BioPress",1,1),("GooProducer",1,1),("GooDispenser",1,1),("VialFiller",1,1),("Door",4,1),("Painter",2,1),("Wall",10,3),("ScrapCompactor",2,1)]
            for checkItem in checkItems:
                if itemsInStorage.get(checkItem[0],0) < checkItem[1]:
                    quests = [src.quests.questMap["ClearInventory"](returnToTile=False),
                            src.quests.questMap["MetalWorking"](amount=checkItem[2],toProduce=checkItem[0])]
                    if not dryRun:
                        beUsefull.idleCounter = 0
                    return (quests,None)
            return (None,None)
        return (None,None)

src.quests.addType(MetalWorking)

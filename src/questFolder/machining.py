import src
import random

class Machining(src.quests.MetaQuestSequence):
    type = "Machining"

    def __init__(self, description="machining", creator=None, reason=None, toProduce=None, amount=None, produceToInventory=False):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description + " " + str(toProduce)
        self.reason = reason
        self.toProduce = toProduce
        self.amount = amount
        self.amountDone = 0
        self.produceToInventory = produceToInventory

    def generateTextDescription(self):
        reason = ""
        if self.reason:
            reason = f", to {self.reason}"
        out = f"""
Do some machining and produce a machine{reason}.

Produce {self.amount} Machine for {self.toProduce}. {self.amountDone} done.

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

        return False

    def getNextStep(self,character,ignoreCommands=False, dryRun = True):
        if self.subQuests:
            return (None,None)

        if character.macroState["submenue"] and isinstance(character.macroState["submenue"],src.menuFolder.InputMenu.InputMenu) and not ignoreCommands:
            submenue = character.macroState["submenue"]
            if self.toProduce == submenue.text:
                return (None,(["enter"],"set the name of the machine should produce"))

            correctIndex = 0
            while correctIndex < len(self.toProduce) and correctIndex < len(submenue.text):
                if self.toProduce[correctIndex] != submenue.text[correctIndex]:
                    break
                correctIndex += 1

            if correctIndex < len(submenue.text):
                return (None,(["backspace"],"delete input"))

            return (None,(self.toProduce[correctIndex:],"enter name of the machine should produce"))

        if character.macroState["submenue"] and isinstance(character.macroState["submenue"],src.menuFolder.SelectionMenu.SelectionMenu) and not ignoreCommands:
            submenue = character.macroState["submenue"]
            if submenue.tag == "machiningProductSelection":
                index = None
                counter = 1
                for option in submenue.options.items():
                    if option[1] == self.toProduce:
                        index = counter
                        break
                    counter += 1

                if index is None:
                    index = counter-1

                offset = index-submenue.selectionIndex
                if self.produceToInventory:
                    activationCommand = "j"
                else:
                    activationCommand = "k"

                command = ""
                if offset > 0:
                    command += "s"*offset
                else:
                    command += "w"*(-offset)
                command += activationCommand
                return (None,(command,"produce item"))
            else:
                submenue = character.macroState["submenue"]
                counter = 1
                command = ""
                if submenue.selectionIndex > counter:
                    command += "w"*(submenue.selectionIndex-counter)
                if submenue.selectionIndex < counter:
                    command += "s"*(counter-submenue.selectionIndex)
                command += "j"
                return (None,(command,"get your reward"))

        if character.macroState["submenue"] and not ignoreCommands:
            return (None,(["esc"],"exit submenu"))

        if character.getBigPosition() != (7, 7, 0):
            quest = src.quests.questMap["GoToTile"](targetPosition=(7,7,0),reason="go to anvil")
            return ([quest],None)

        benches = []
        if character.container.isRoom:
            benches.extend(character.container.getItemsByType("MachiningTable"))

        benchNearBy = None
        for bench in benches:
            if not character.getDistance(bench.getPosition()) > 1:
                benchNearBy = bench
                break

        if not benchNearBy:
            if not benches:
                self.fail("no bench found")
                return (None,None)
            quest = src.quests.questMap["GoToPosition"](targetPosition=benches[0].getPosition(),ignoreEndBlocked=True,reason="go to a MetalWorkingBench")
            return ([quest],None)

        pos = character.getPosition()
        benchPos = benchNearBy.getPosition()
        if (pos[0],pos[1],pos[2]) == benchPos:
            return (None,("jj","start producing machine"))
        if (pos[0]-1,pos[1],pos[2]) == benchPos:
            return (None,("ajj","start producing machine"))
        if (pos[0]+1,pos[1],pos[2]) == benchPos:
            return (None,("djj","start producing machine"))
        if (pos[0],pos[1]-1,pos[2]) == benchPos:
            return (None,("wjj","start producing machine"))
        if (pos[0],pos[1]+1,pos[2]) == benchPos:
            return (None,("sjj","start producing machine"))

        return (None,None)

    def handleQuestFailure(self,extraParam):
        if extraParam["quest"] not in self.subQuests:
            return

        self.subQuests.remove(extraParam["quest"])

        quest = extraParam["quest"]

        reason = extraParam.get("reason")
        if reason and reason.startswith("no source for item ") and "scrap hammering" in self.character.duties:
            newQuest = src.quests.questMap["ScrapHammering"](amount=1,produceToInventory=True)
            self.addQuest(newQuest)
            self.startWatching(newQuest,self.handleQuestFailure,"failed")
            return
        self.fail(reason)

    def handleConstructedMachine(self, extraInfo):
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

        self.startWatching(character,self.handleConstructedMachine, "constructed machine")
        self.startWatching(character,self.handleInventoryFull, "inventory full error")
        self.startWatching(character,self.handleNoMetalBars, "no metalBars error")

        return super().assignToCharacter(character)
    @staticmethod
    def generateDutyQuest(beUsefull,character,currentRoom, dryRun):
        for room in beUsefull.getRandomPriotisedRooms(character,currentRoom):
            for machiningTable in room.getItemsByType("MachiningTable"):
                if machiningTable.scheduledItems:
                    quests = [src.quests.questMap["ClearInventory"](),
                              src.quests.questMap["Machining"](amount=1,toProduce=machiningTable.scheduledItems[0])]
                    if not dryRun:
                        beUsefull.idleCounter = 0
                    return (quests,None)

        machinesInStorage = {}
        for room in beUsefull.getRandomPriotisedRooms(character,currentRoom):
            for storageSlot in room.storageSlots:
                items = room.getItemByPosition(storageSlot[0])
                for item in items:
                    if item.type != "Machine":
                        continue
                    machinesInStorage[item.toProduce] = machinesInStorage.get(item.toProduce,0)+1
            for outputSlot in room.outputSlots:
                items = room.getItemByPosition(outputSlot[0])
                for item in items:
                    if item.type != "Machine":
                        continue
                    machinesInStorage[item.toProduce] = machinesInStorage.get(item.toProduce,0)+1

        for room in beUsefull.getRandomPriotisedRooms(character,currentRoom):
            for buildSite in random.sample(room.buildSites,len(room.buildSites)):
                if buildSite[1] != "Machine":
                    continue
                if buildSite[2]["toProduce"] in machinesInStorage:
                    continue
                quests = [src.quests.questMap["ClearInventory"](),
                          src.quests.questMap["Machining"](toProduce=buildSite[2]["toProduce"],amount=1,produceToInventory=False)]
                return (quests,None)

        itemsToCheck = ["Wall","Case","Frame","Rod","Door","RoomBuilder","ScrapCompactor","Sword","Armor"]
        for itemType in itemsToCheck:
            if itemType not in machinesInStorage:
                quests = [src.quests.questMap["ClearInventory"](),
                          src.quests.questMap["Machining"](toProduce=itemType,amount=1,produceToInventory=False)]
                return (quests,None)
        return (None,None)
src.quests.addType(Machining)

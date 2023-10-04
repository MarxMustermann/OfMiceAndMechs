import src


class ScheduleMetalWorking(src.quests.MetaQuestSequence):
    type = "ScheduleMetalWorking"

    def __init__(self, description="metal working", creator=None, reason=None, toProduce=None, amount=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description + str(toProduce)
        self.reason = reason
        self.toProduce = toProduce
        self.amount = amount
        self.amountDone = 0

    def generateTextDescription(self):
        reason = ""
        if self.reason:
            reason = f", to {self.reason}"
        return f"""
do some metal working
"""

    def triggerCompletionCheck(self,character=None):
        if not character:
            return False

        return False

    def getNextStep(self,character,ignoreCommands=False):
        if self.subQuests:
            return (None,None)

        if character.getBigPosition() != (7, 7, 0):
            quest = src.quests.questMap["GoToTile"](targetPosition=(7,7,0),reason="go to anvil")
            return ([quest],None)

        if not character.searchInventory("MetalBars"):
            quest = src.quests.questMap["FetchItems"](toCollect="MetalBars",amount=1,reason="have some bars to work with")
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
            quest = src.quests.questMap["GoToPosition"](targetPosition=benches[0].getPosition(),ignoreEndBlocked=True,reason="go to an bench")
            return ([quest],None)

        selectionBit = ""
        if self.toProduce == "Wall":
            selectionBit = ""
        if self.toProduce == "Door":
            selectionBit = "s"
        if self.toProduce == "RoomBuilder":
            selectionBit = "ss"
        if self.toProduce == "Painter":
            selectionBit = "sss"


        pos = character.getPosition()
        benchPos = benchNearBy.getPosition()
        if (pos[0],pos[1],pos[2]) == benchPos:
            return (None,("jj"+selectionBit+"j",""))
        if (pos[0]-1,pos[1],pos[2]) == benchPos:
            return (None,("ajj"+selectionBit+"j","produce a wall"))
        if (pos[0]+1,pos[1],pos[2]) == benchPos:
            return (None,("djj"+selectionBit+"j","produce a wall"))
        if (pos[0],pos[1]-1,pos[2]) == benchPos:
            return (None,("wjj"+selectionBit+"j","produce a wall"))
        if (pos[0],pos[1]+1,pos[2]) == benchPos:
            return (None,("sjj"+selectionBit+"j","produce a wall"))

        return (None,None)

    def getSolvingCommandString(self, character, dryRun=True):
        nextStep = self.getNextStep(character)
        if nextStep == (None,None):
            return super().getSolvingCommandString(character)
        return self.getNextStep(character)[1]

    def generateSubquests(self, character=None):
        (nextQuests,nextCommand) = self.getNextStep(character,ignoreCommands=True)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
            return

    def handleQuestFailure(self,extraParam):
        if not extraParam["quest"] in self.subQuests:
            return

        self.subQuests.remove(extraParam["quest"])

        quest = extraParam["quest"]

        reason = extraParam.get("reason")
        if reason and reason.startswith("no source for item ") and "scrap hammering" in self.character.duties:
            newQuest = src.quests.questMap["ScrapHammering"](amount=1)
            self.addQuest(newQuest)
            self.startWatching(newQuest,self.handleQuestFailure,"failed")
            return
        self.fail(reason)

    def handleWorkedMetal(self, extraInfo):
        if self.completed:
            1/0
        if not self.active:
            return

        self.amountDone += 1
        if self.amount != None and self.amountDone >= self.amount:
            self.postHandler()

    def assignToCharacter(self, character):
        if self.character:
            return None

        self.startWatching(character,self.handleWorkedMetal, "worked metal")

        return super().assignToCharacter(character)


    def solver(self, character):
        (nextQuests,nextCommand) = self.getNextStep(character)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
                self.startWatching(quest,self.handleQuestFailure,"failed")
            return

        if nextCommand:
            character.runCommandString(nextCommand[0])
            return
        super().solver(character)

src.quests.addType(MetalWorking)

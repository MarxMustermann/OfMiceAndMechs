import src

class MetalWorking(src.quests.MetaQuestSequence):
    type = "MetalWorking"

    def __init__(self, description="metal working", creator=None, reason=None, toProduce=None, amount=None, produceToInventory=False):
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

        return False

    def getNextStep(self,character,ignoreCommands=False,dryRun=True):
        if self.subQuests:
            return (None,None)

        if character.macroState["submenue"] and isinstance(character.macroState["submenue"],src.interaction.InputMenu) and not ignoreCommands:
            submenue = character.macroState["submenue"]
            if self.toProduce == submenue.text:
                return (None,(["enter"],"to set the name of the item to produce"))

            correctIndex = 0
            while correctIndex < len(self.toProduce) and correctIndex < len(submenue.text):
                if self.toProduce[correctIndex] != submenue.text[correctIndex]:
                    break
                correctIndex += 1

            if correctIndex < len(submenue.text):
                return (None,(["backspace"],"to delete input"))

            return (None,(self.toProduce[correctIndex:],"to enter name of the tem to produce"))

        if character.macroState["submenue"] and isinstance(character.macroState["submenue"],src.interaction.SelectionMenu) and not ignoreCommands:
            submenue = character.macroState["submenue"]
            if submenue.tag == "metalWorkingProductSelection":
                index = None
                counter = 1
                for option in submenue.options.items():
                    if option[1] == self.toProduce:
                        index = counter
                        break
                    counter += 1

                if index == None:
                    index = counter-1

                if self.produceToInventory:
                    activationCommand = "j"
                else:
                    activationCommand = "k"

                offset = index-submenue.selectionIndex
                if offset > 0:
                    return (None,("s"*offset+activationCommand,"to produce item"))
                else:
                    return (None,("w"*(-offset)+activationCommand,"to produce item"))
            else:
                submenue = character.macroState["submenue"]
                counter = 1
                command = ""
                if submenue.selectionIndex > counter:
                    command += "w"*(submenue.selectionIndex-counter)
                if submenue.selectionIndex < counter:
                    command += "s"*(counter-submenue.selectionIndex)
                command += "j"
                return (None,(command,"to get your reward"))

        if character.macroState["submenue"] and not ignoreCommands:
            return (None,(["esc"],"to exit submenu"))

        if character.getBigPosition() != (7, 7, 0):
            quest = src.quests.questMap["GoToTile"](targetPosition=(7,7,0),reason="go to anvil")
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
            return (None,("jj","start metal working"))
        if (pos[0]-1,pos[1],pos[2]) == benchPos:
            return (None,("ajj","start metal working"))
        if (pos[0]+1,pos[1],pos[2]) == benchPos:
            return (None,("djj","start metal working"))
        if (pos[0],pos[1]-1,pos[2]) == benchPos:
            return (None,("wjj","start metal working"))
        if (pos[0],pos[1]+1,pos[2]) == benchPos:
            return (None,("sjj","start metal working"))

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
            newQuest = src.quests.questMap["ScrapHammering"](amount=1,produceToInventory=True)
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
        if self.amount != None and self.amountDone >= self.amount:
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
            return

        self.startWatching(character,self.handleWorkedMetal, "worked metal")
        self.startWatching(character,self.handleInventoryFull, "inventory full error")
        self.startWatching(character,self.handleNoMetalBars, "no metalBars error")

        return super().assignToCharacter(character)

    def solver(self, character):
        (nextQuests,nextCommand) = self.getNextStep(character, dryRun=False)
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

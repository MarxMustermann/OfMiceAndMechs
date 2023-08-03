import src

class DrawFloorPlan(src.quests.MetaQuestSequence):
    type = "DrawFloorPlan"

    def __init__(self, description="draw floor plan", creator=None, targetPosition=None,reason=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        self.shortCode = "d"
        self.targetPosition = targetPosition
        self.reason = reason

    def generateTextDescription(self):
        out = []
        reason = ""
        if self.reason:
            reason = ",\nto %s"%(self.reason,)
        text = """
Draw a floor plan assigned to a room%s.

"""%(reason,)
        return out

    def triggerCompletionCheck(self,character=None):
        if not character:
            return

    def getNextStep(self,character=None,ignoreCommands=False):
        if not self.subQuests:

            if not isinstance(character.container,src.rooms.Room):
                command = None
                if character.xPosition%15 == 0:
                    command = "d"
                if character.xPosition%15 == 14:
                    command = "a"
                if character.yPosition%15 == 0:
                    command = "s"
                if character.yPosition%15 == 14:
                    command = "w"
                return (None,(command,"draw to stockpile"))

            if not character.container.floorPlan:
                self.fail()
                return (None,None)

            if not (character.getBigPosition() == self.targetPosition):
                quest = src.quests.questMap["GoToTile"](targetPosition=self.targetPosition)
                return ([quest],None)

            if "walkingSpace" in character.container.floorPlan:
                walkingSpaces = character.container.floorPlan.get("walkingSpace")
                if walkingSpaces:
                    if walkingSpaces[-1] in character.container.walkingSpace:
                        walkingSpaces.pop()

                if walkingSpaces:
                    quest = src.quests.questMap["DrawWalkingSpace"](tryHard=True,targetPositionBig=self.targetPosition,targetPosition=walkingSpaces[-1])
                    return ([quest],None)

                if not walkingSpaces == None:
                    del character.container.floorPlan["walkingSpace"]

            if "inputSlots" in character.container.floorPlan:
                inputSlots = character.container.floorPlan.get("inputSlots")
                if inputSlots:
                    for existingInputslot in character.container.inputSlots:
                        if existingInputslot[0] == inputSlots[-1][0]:
                            inputSlots.pop()
                            break

                    if inputSlots:
                        inputSlot = inputSlots[-1]
                        quest = src.quests.questMap["DrawStockpile"](itemType=inputSlot[1],stockpileType="i",targetPositionBig=self.targetPosition,targetPosition=inputSlot[0])
                        return ([quest],None)

                if not inputSlots == None:
                    del character.container.floorPlan["inputSlots"]

            if "outputSlots" in character.container.floorPlan:
                outputSlots = character.container.floorPlan.get("outputSlots")
                if outputSlots:
                    for existingOutputSlot in character.container.outputSlots:
                        if existingOutputSlot[0] == outputSlots[-1][0]:
                            outputSlots.pop()
                            break

                    if outputSlots:
                        outputSlot = outputSlots[-1]
                        quest = src.quests.questMap["DrawStockpile"](itemType=outputSlot[1],stockpileType="o",targetPositionBig=self.targetPosition,targetPosition=outputSlot[0])
                        return ([quest],None)

                if not outputSlots == None:
                    del character.container.floorPlan["outputSlots"]

            if "storageSlots" in character.container.floorPlan:
                storageSlots = character.container.floorPlan.get("storageSlots")
                if storageSlots:
                    for existingStorageSlot in character.container.storageSlots:
                        if existingStorageSlot[0] == storageSlots[-1][0]:
                            storageSlots.pop()
                            break

                    if storageSlots:
                        storageSlot = storageSlots[-1]
                        quest = src.quests.questMap["DrawStockpile"](itemType=storageSlot[1],stockpileType="s",targetPositionBig=self.targetPosition,targetPosition=storageSlot[0])
                        return ([quest],None)

                if not storageSlots == None:
                    del character.container.floorPlan["storageSlots"]

            if "buildSites" in character.container.floorPlan:
                buildSites = character.container.floorPlan.get("buildSites")

                if buildSites:
                    for existingBuildSite in character.container.buildSites:
                        if existingBuildSite[0] == buildSites[-1][0]:
                            buildSites.pop()
                            break

                    if buildSites:
                        buildSite = buildSites[-1]
                        quest = src.quests.questMap["DrawBuildSite"](itemType=buildSite[1],targetPositionBig=self.targetPosition,targetPosition=buildSite[0],extraInfo=buildSite[2])
                        return ([quest],None)

                if not buildSites == None:
                    del character.container.floorPlan["buildSites"]

            if character.container.floorPlan:
                character.container.floorPlan = None

            self.postHandler()
            return (None,None)
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

    def solver(self, character):
        if self.triggerCompletionCheck(character):
            return
        (nextQuests,nextCommand) = self.getNextStep(character)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
            return

        if nextCommand:
            character.runCommandString(nextCommand[0])
            return
        super().solver(character)

src.quests.addType(DrawFloorPlan)

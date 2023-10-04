import random

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
            reason = f",\nto {self.reason}"
        text = f"""
Draw a floor plan assigned to a room{reason}.

"""
        return out

    def triggerCompletionCheck(self,character=None):
        if not character:
            return

    def getNextStep(self,character=None,ignoreCommands=False,dryRun=True):
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
                if command:
                    return (None,(command,"to enter room"))

            if character.getBigPosition() != self.targetPosition:
                quest = src.quests.questMap["GoToTile"](targetPosition=self.targetPosition)
                return ([quest],None)

            if not character.container.floorPlan:
                if not dryRun:
                    self.fail()
                return (None,None)

            if "walkingSpace" in character.container.floorPlan:
                walkingSpaces = character.container.floorPlan.get("walkingSpace")
                if walkingSpaces and walkingSpaces[-1] in character.container.walkingSpace:
                    walkingSpaces.pop()

                quests = []
                counter = 0
                walkingSpaces = list(walkingSpaces)
                if len(walkingSpaces) > 1:
                    index = random.randint(0,len(walkingSpaces)-1)
                    walkingSpaces = walkingSpaces[index:]+walkingSpaces[:index]
                for walkingSpace in reversed(walkingSpaces):
                    if counter > 9:
                        break
                    counter += 1
                    quest = src.quests.questMap["DrawWalkingSpace"](tryHard=True,targetPositionBig=self.targetPosition,targetPosition=walkingSpace)
                    quests.append(quest)

                if quests:
                    return (list(reversed(quests)),None)

                if walkingSpaces != None:
                    del character.container.floorPlan["walkingSpace"]

            if "outputSlots" in character.container.floorPlan:
                outputSlots = character.container.floorPlan.get("outputSlots")
                if outputSlots:
                    for existingOutputSlot in character.container.outputSlots:
                        if existingOutputSlot[0] == outputSlots[-1][0]:
                            outputSlots.pop()
                            break

                outputSlots = character.container.floorPlan.get("outputSlots")[:]
                if len(outputSlots) > 1:
                    index = random.randint(0,len(outputSlots)-1)
                    walkingSpaces = outputSlots[index:]+outputSlots[:index]
                if outputSlots:
                    quests = []
                    counter = 0
                    counter2 = 0
                    while counter < len(outputSlots):
                        if counter2 > 4:
                            break
                        outputSlot = outputSlots[counter]

                        counter += 1
                        counter2 += 1

                        quest = src.quests.questMap["DrawStockpile"](itemType=outputSlot[1],stockpileType="o",targetPositionBig=self.targetPosition,targetPosition=outputSlot[0])
                        quests.append(quest)

                        for outputSlot2 in outputSlots[counter:]:
                            if outputSlot[1] == outputSlot2[1]:
                                quest = src.quests.questMap["DrawStockpile"](itemType=outputSlot2[1],stockpileType="o",targetPositionBig=self.targetPosition,targetPosition=outputSlot2[0])
                                quests.append(quest)
                                outputSlots.remove(outputSlot2)
                                counter2 += 1

                    if quests:
                        return (list(reversed(quests)),None)

                if outputSlots != None:
                    del character.container.floorPlan["outputSlots"]

            if "buildSites" in character.container.floorPlan:
                buildSites = character.container.floorPlan.get("buildSites")
                if buildSites:
                    for existingBuildSite in character.container.buildSites:
                        if existingBuildSite[0] == buildSites[-1][0]:
                            buildSites.pop()
                            break

                buildSites = character.container.floorPlan.get("buildSites")[:]
                if len(buildSites) > 1:
                    index = random.randint(0,len(buildSites)-1)
                    buildSites = buildSites[index:]+buildSites[:index]
                if buildSites:
                    quests = []
                    counter = 0
                    counter2 = 0
                    while counter < len(buildSites):
                        if counter2 > 4:
                            break
                        buildSite = buildSites[counter]

                        counter += 1
                        counter2 += 1

                        quest = src.quests.questMap["DrawBuildSite"](itemType=buildSite[1],targetPositionBig=self.targetPosition,targetPosition=buildSite[0],extraInfo=buildSite[2])
                        quests.append(quest)

                        for buildSite2 in buildSites[counter:]:
                            if buildSite[1] == buildSite2[1] and buildSite[2] == buildSite2[2]:
                                quest = src.quests.questMap["DrawBuildSite"](itemType=buildSite2[1],targetPositionBig=self.targetPosition,targetPosition=buildSite2[0],extraInfo=buildSite2[2])
                                quests.append(quest)
                                buildSites.remove(buildSite2)
                                counter2 += 1
                                if counter2 > 9:
                                    break

                    if quests:
                        return (list(reversed(quests)),None)

                    if buildSites:
                        buildSite = buildSites[-1]
                        quest = src.quests.questMap["DrawBuildSite"](itemType=buildSite[1],targetPositionBig=self.targetPosition,targetPosition=buildSite[0],extraInfo=buildSite[2])
                        return ([quest],None)

                if buildSites != None:
                    del character.container.floorPlan["buildSites"]

            if "storageSlots" in character.container.floorPlan:
                storageSlots = character.container.floorPlan.get("storageSlots")
                if storageSlots:
                    for existingStorageSlot in character.container.storageSlots:
                        if existingStorageSlot[0] == storageSlots[-1][0]:
                            storageSlots.pop()
                            break

                storageSlots = character.container.floorPlan.get("storageSlots")[:]
                if len(storageSlots) > 1:
                    index = random.randint(0,len(storageSlots)-1)
                    storageSlots = storageSlots[index:]+storageSlots[:index]

                if storageSlots:
                    quests = []
                    counter = 0
                    counter2 = 0
                    while counter < len(storageSlots):
                        if counter2 > 4:
                            break
                        storageSlot = storageSlots[counter]

                        counter += 1
                        counter2 += 1

                        quest = src.quests.questMap["DrawStockpile"](itemType=storageSlot[1],stockpileType="s",targetPositionBig=self.targetPosition,targetPosition=storageSlot[0],extraInfo=storageSlot[2])
                        quests.append(quest)

                        for storageSlot2 in storageSlots[counter:]:
                            if storageSlot[1] == storageSlot2[1] and storageSlot[2] == storageSlot2[2]:
                                quest = src.quests.questMap["DrawStockpile"](itemType=storageSlot2[1],stockpileType="s",targetPositionBig=self.targetPosition,targetPosition=storageSlot2[0],extraInfo=storageSlot[2])
                                quests.append(quest)
                                storageSlots.remove(storageSlot2)
                                counter2 += 1

                                if counter2 > 9:
                                    break
                    if quests:
                        return (list(reversed(quests)),None)

                if storageSlots != None:
                    del character.container.floorPlan["storageSlots"]

            if "inputSlots" in character.container.floorPlan:
                inputSlots = character.container.floorPlan.get("inputSlots")
                if inputSlots:
                    for existingInputslot in character.container.inputSlots:
                        if existingInputslot[0] == inputSlots[-1][0]:
                            inputSlots.pop()
                            break

                inputSlots = character.container.floorPlan.get("inputSlots")[:]
                random.shuffle(inputSlots)
                if inputSlots:
                    quests = []
                    counter = 0
                    counter2 = 0
                    while counter < len(inputSlots):
                        if counter2 > 4:
                            break
                        inputSlot = inputSlots[counter]

                        counter += 1
                        counter2 += 1

                        quest = src.quests.questMap["DrawStockpile"](itemType=inputSlot[1],stockpileType="i",targetPositionBig=self.targetPosition,targetPosition=inputSlot[0])
                        quests.append(quest)

                        for inputSlot2 in inputSlots[counter:]:
                            if inputSlot[1] == inputSlot2[1]:
                                quest = src.quests.questMap["DrawStockpile"](itemType=inputSlot2[1],stockpileType="i",targetPositionBig=self.targetPosition,targetPosition=inputSlot2[0])
                                quests.append(quest)
                                inputSlots.remove(inputSlot2)
                                counter2 += 1

                    if quests:
                        return (list(reversed(quests)),None)

                if inputSlots != None:
                    del character.container.floorPlan["inputSlots"]

            if character.container.floorPlan:
                character.container.floorPlan = None

            if not dryRun:
                self.postHandler()
            return (None,None)
        return (None,None)

    def getSolvingCommandString(self, character, dryRun=True):
        nextStep = self.getNextStep(character)
        if nextStep == (None,None):
            return super().getSolvingCommandString(character)
        return self.getNextStep(character)[1]

    def generateSubquests(self, character=None):
        (nextQuests,nextCommand) = self.getNextStep(character,ignoreCommands=True,dryRun=False)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
            return

    def solver(self, character):
        if self.triggerCompletionCheck(character):
            return
        (nextQuests,nextCommand) = self.getNextStep(character,dryRun=False)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
            return

        if nextCommand:
            character.runCommandString(nextCommand[0])
            return
        super().solver(character)

src.quests.addType(DrawFloorPlan)

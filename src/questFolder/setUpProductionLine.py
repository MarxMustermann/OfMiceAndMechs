import src
import random

class SetUpProductionLine(src.quests.MetaQuestSequence):
    type = "SetUpProductionLine"

    def __init__(self, description="set up production line for", creator=None, command=None, lifetime=None, itemType=None,tryHard=False, targetPositionBig=None):
        questList = []
        super().__init__(questList, creator=creator, lifetime=lifetime)
        self.metaDescription = description+" "+itemType
        self.targetPositionBig = targetPositionBig
        self.itemType = itemType
        self.tryHard = tryHard

    def getProductionLineDescription(self,itemType,depth=0):
        text = "  "*depth+f"- {itemType}\n"
        neededItems = src.items.rawMaterialLookup.get(itemType,[])[:]
        if itemType == "MetalBars":
            neededItems = ["Scrap"]
        for item in neededItems:
            text += self.getProductionLineDescription(item,depth=depth+1)
        return text

    def generateTextDescription(self):
        text = f"""
set up a production line for {self.itemType}.
set the production line up on tile {self.targetPositionBig}

The full production line looks like this:

"""
        text += f"""
{self.getProductionLineDescription(self.itemType)}
"""
        
        if self.tryHard:
            text += """
Try as hard as you can to achieve this.
"""

        return text

    def solver(self, character):
        (nextQuests,nextCommand) = self.getNextStep(character)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
            return

        if nextCommand:
            character.runCommandString(nextCommand)
            return
        super().solver(character)

    def generateSubquests(self, character=None):
        (nextQuests,nextCommand) = self.getNextStep(character,ignoreCommands=True)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
            return

    def getSolvingCommandString(self, character, dryRun=True):
        nextStep = self.getNextStep(character)
        if nextStep == (None,None):
            return super().getSolvingCommandString(character)
        return self.getNextStep(character)[1]

    def getNextStep(self,character=None,ignoreCommands=False):
        if not self.subQuests:
            if self.itemType == "Door":
                foundWallOutput = False
                for room in character.getTerrain().rooms:
                    for outputSlot in room.outputSlots:
                        if outputSlot[1] == "Door":
                            foundWallOutput = True

                if foundWallOutput:
                    self.postHandler()
                    return (None,None)

                quest0 = src.quests.questMap["GoToTile"](targetPosition=(7,7,0))
                quest1 = src.quests.questMap["SetUpMachine"](targetPositionBig=self.targetPositionBig,targetPosition=(4,8,0),itemType="Door",tryHard=True)
                quest2 = src.quests.questMap["PlaceItem"](targetPositionBig=self.targetPositionBig,targetPosition=(3,7,0),itemType="ScrapCompactor",tryHard=True,boltDown=True)
                quest3 = src.quests.questMap["DrawStockpile"](tryHard=True,itemType="Scrap",stockpileType="i",targetPositionBig=self.targetPositionBig,targetPosition=(2,7,0))
                quest4 = src.quests.questMap["DrawStockpile"](tryHard=True,itemType="Case",stockpileType="i",targetPositionBig=self.targetPositionBig,targetPosition=(3,8,0))
                quest5 = src.quests.questMap["DrawStockpile"](tryHard=True,itemType="Door",stockpileType="o",targetPositionBig=self.targetPositionBig,targetPosition=(5,8,0))
                return ([quest5,quest4,quest3,quest2,quest1,quest0],None)
            if self.itemType == "Wall":
                foundWallOutput = False
                for room in character.getTerrain().rooms:
                    for outputSlot in room.outputSlots:
                        if outputSlot[1] == "Wall":
                            foundWallOutput = True

                if foundWallOutput:
                    self.postHandler()
                    return (None,None)

                quest1 = src.quests.questMap["SetUpMachine"](targetPositionBig=self.targetPositionBig,targetPosition=(9,8,0),itemType="Wall",tryHard=True)
                quest2 = src.quests.questMap["PlaceItem"](targetPositionBig=self.targetPositionBig,targetPosition=(8,7,0),itemType="ScrapCompactor",tryHard=True,boltDown=True)
                quest3 = src.quests.questMap["DrawStockpile"](tryHard=True,itemType="Scrap",stockpileType="i",targetPositionBig=self.targetPositionBig,targetPosition=(7,7,0))
                quest4 = src.quests.questMap["DrawStockpile"](tryHard=True,itemType="Case",stockpileType="i",targetPositionBig=self.targetPositionBig,targetPosition=(8,8,0))
                quest5 = src.quests.questMap["DrawStockpile"](tryHard=True,itemType="Wall",stockpileType="o",targetPositionBig=self.targetPositionBig,targetPosition=(10,8,0))
                return ([quest5,quest4,quest3,quest2,quest1],None)
            if self.itemType == "Case":
                foundCaseOutput = False
                for room in character.getTerrain().rooms:
                    for outputSlot in room.outputSlots:
                        if outputSlot[1] == "Case":
                            foundCaseOutput = True

                if foundCaseOutput:
                    self.postHandler()
                    return (None,None)

                quest1 = src.quests.questMap["SetUpMachine"](targetPositionBig=self.targetPositionBig,targetPosition=(9,10,0),itemType="Case",tryHard=True)
                quest2 = src.quests.questMap["SetUpMachine"](targetPositionBig=self.targetPositionBig,targetPosition=(7,10,0),itemType="Frame",tryHard=True)
                quest3 = src.quests.questMap["SetUpMachine"](targetPositionBig=self.targetPositionBig,targetPosition=(5,10,0),itemType="Rod",tryHard=True)
                quest4 = src.quests.questMap["PlaceItem"](targetPositionBig=self.targetPositionBig,targetPosition=(3,10,0),itemType="ScrapCompactor",tryHard=True,boltDown=True)
                quest5 = src.quests.questMap["DrawStockpile"](tryHard=True,itemType="Scrap",stockpileType="i",targetPositionBig=self.targetPositionBig,targetPosition=(2,10,0))
                quest6 = src.quests.questMap["DrawStockpile"](tryHard=True,itemType="Case",stockpileType="o",targetPositionBig=self.targetPositionBig,targetPosition=(10,10,0))
                return ([quest6,quest5,quest4,quest1,quest2,quest3],None)
        return (None,None)

    """
            if character.inventory and character.inventory[-1].type == "Machine":
                if not self.targetPosition:
                    validTargetPosition = False
                    counter = 0
                    while not validTargetPosition and counter < 10:
                        counter += 1
                        self.targetPosition = (random.randint(2,4),random.randint(2,9),0)
                        room = random.choice(character.getTerrain().rooms)

                        if room.getItemByPosition(self.targetPosition):
                            continue
                        if room.getItemByPosition((self.targetPosition[0]-1,self.targetPosition[1],0)):
                            continue
                        if room.getItemByPosition((self.targetPosition[0]+1,self.targetPosition[1],0)):
                            continue
                        if room.getItemByPosition((self.targetPosition[0],self.targetPosition[1]+1,0)):
                            continue
                        if room.getItemByPosition((self.targetPosition[0],self.targetPosition[1]-1,0)):
                            continue


                        validTargetPosition = True
                        break

                    if not validTargetPosition:
                        self.fail("no spot to build machine")
                        return (None,None)

                    self.targetPositionBig = room.getPosition()

                if not character.getBigPosition() == self.targetPositionBig:
                    quest = src.quests.questMap["GoToTile"](targetPosition=self.targetPositionBig)
                    return ([quest],None)

                if character.getDistance(self.targetPosition) > 1:
                    quest = src.quests.questMap["GoToPosition"](targetPosition=self.targetPosition,ignoreEndBlocked=True)
                    return ([quest],None)
                
                directions = [((0,0,0),"."),((0,1,0),"s"),((1,0,0),"d"),((0,-1,0),"w"),((-1,0,0),"a")]
                directionFound = None
                for direction in directions:
                    if character.getPosition(offset=direction[0]) == self.targetPosition:
                        return (None,"L"+direction[1])


            machineMachine = None
            bluePrint = None
            for room in character.getTerrain().rooms:
                for item in room.itemsOnFloor:
                    if item.type == "MachineMachine":
                        machineMachine = item
                        continue
                    if item.type == "BluePrint" and item.endProduct == self.itemType:
                        bluePrint = item
                        continue

            if not machineMachine:
                self.fail(reason="no machine machine found")
                return (None,None)

            items = machineMachine.container.getItemByPosition(machineMachine.getPosition(offset=(1,0,0)))
            if items and items[-1].type == "Machine":
                if character.getDistance(items[-1].getPosition()) > 1:
                    quest = src.quests.questMap["GoToPosition"](targetPosition=items[-1].getPosition(),ignoreEndBlocked=True)
                    return ([quest],None)
                
                directions = [((0,0,0),"."),((0,1,0),"s"),((1,0,0),"d"),((0,-1,0),"w"),((-1,0,0),"a")]
                directionFound = None
                for direction in directions:
                    if character.getPosition(offset=direction[0]) == items[-1].getPosition():
                        counter = 0
                        for endProduct in machineMachine.endProducts:
                            if endProduct == self.itemType:
                                counter += 1
                        return (None,"K"+direction[1])


            if self.itemType in machineMachine.endProducts:
                if not character.container == machineMachine.container:
                    quest = src.quests.questMap["GoToTile"](targetPosition=machineMachine.container.getPosition())
                    return ([quest],None)
                if character.getDistance(machineMachine.getPosition()) > 1:
                    quest = src.quests.questMap["GoToPosition"](targetPosition=machineMachine.getPosition(),ignoreEndBlocked=True)
                    return ([quest],None)

                items = machineMachine.container.getItemByPosition(machineMachine.getPosition(offset=(-1,0,0)))
                if not items or not items[-1].type == "MetalBars":
                    if (not character.inventory) or (not character.inventory[-1].type == "MetalBars"):
                        foundRoom = None
                        for room in character.getTerrain().rooms:
                            for item in room.itemsOnFloor:
                                if item.bolted == False and item.type == "MetalBars":
                                    foundRoom = room
                                    break
                            if foundRoom:
                                break

                        if not foundRoom:
                            if self.tryHard:
                                quest1 = src.quests.questMap["FetchItems"](toCollect="MetalBars",amount=1,takeAnyUnbolted=True,tryHard=True)
                                self.startWatching(quest1,self.unhandledSubQuestFail,"failed")
                                quest2 = src.quests.questMap["GoToTile"](targetPosition=(7,7,0))
                                return ([quest1,quest2],None)

                            self.fail("missing resource MetalBars")
                            return (None,None)

                        if not character.getBigPosition() == room.getPosition():
                            quest = src.quests.questMap["GoToTile"](targetPosition=room.getPosition())
                            return ([quest],None)

                        quest = src.quests.questMap["FetchItems"](toCollect="MetalBars",takeAnyUnbolted=True)
                        return ([quest],None)

                    if not character.container == machineMachine.container:
                        quest = src.quests.questMap["GoToTile"](targetPosition=machineMachine.container.getPosition())
                        return ([quest],None)

                    if character.getDistance(machineMachine.getPosition(offset=(-1,0,0))) > 1:
                        quest = src.quests.questMap["GoToPosition"](targetPosition=machineMachine.getPosition(offset=(-1,0,0)),ignoreEndBlocked=True)
                        return ([quest],None)
                    directions = [((0,0,0),"."),((0,1,0),"s"),((1,0,0),"d"),((0,-1,0),"w"),((-1,0,0),"a")]
                    directionFound = None
                    for direction in directions:
                        if character.getPosition(offset=direction[0]) == machineMachine.getPosition(offset=(-1,0,0)):
                            return (None,"L"+direction[1])

                    1/0

                directions = [((0,0,0),"."),((0,1,0),"s"),((1,0,0),"d"),((0,-1,0),"w"),((-1,0,0),"a")]
                directionFound = None
                for direction in directions:
                    if character.getPosition(offset=direction[0]) == machineMachine.getPosition():
                        counter = 0
                        for endProduct in machineMachine.endProducts:
                            if endProduct == self.itemType:
                                break
                            counter += 1
                        return (None,"J"+direction[1]+"sj"+(counter*"s")+"j")

            items = machineMachine.container.getItemByPosition(machineMachine.getPosition(offset=(0,-1,0)))
            placedBlueprintFound = False
            for item in items:
                if item.type == "BluePrint" and item.endProduct == self.itemType:
                    placedBlueprintFound = True
                    break

            if placedBlueprintFound:
                if not character.container == machineMachine.container:
                    quest = src.quests.questMap["GoToTile"](targetPosition=machineMachine.container.getPosition())
                    return ([quest],None)
                if character.getDistance(machineMachine.getPosition()) > 1:
                    quest = src.quests.questMap["GoToPosition"](targetPosition=machineMachine.getPosition(),ignoreEndBlocked=True)
                    return ([quest],None)
                directions = [((0,0,0),"."),((0,1,0),"s"),((1,0,0),"d"),((0,-1,0),"w"),((-1,0,0),"a")]
                directionFound = None
                for direction in directions:
                    if character.getPosition(offset=direction[0]) == machineMachine.getPosition():
                        return (None,"J"+direction[1]+"j")

            if character.inventory and character.inventory[-1].type == "BluePrint" and character.inventory[-1].endProduct == self.itemType:
                if not character.container == machineMachine.container:
                    quest = src.quests.questMap["GoToTile"](targetPosition=machineMachine.container.getPosition())
                    return ([quest],None)
                if character.getDistance(machineMachine.getPosition(offset=(0,-1,0))) > 1:
                    quest = src.quests.questMap["GoToPosition"](targetPosition=machineMachine.getPosition(offset=(0,-1,0)),ignoreEndBlocked=True)
                    return ([quest],None)
                directions = [((0,0,0),"."),((0,1,0),"s"),((1,0,0),"d"),((0,-1,0),"w"),((-1,0,0),"a")]
                directionFound = None
                for direction in directions:
                    if character.getPosition(offset=direction[0]) == machineMachine.getPosition(offset=(0,-1,0)):
                        return (None,"L"+direction[1])
                15/0

            if bluePrint:
                if not character.container == bluePrint.container:
                    quest = src.quests.questMap["GoToTile"](targetPosition=bluePrint.container.getPosition())
                    return ([quest],None)
                if not character.getPosition() == bluePrint.getPosition():
                    quest = src.quests.questMap["GoToPosition"](targetPosition=bluePrint.getPosition())
                    return ([quest],None)
                return (None,"k")

            if self.tryHard:
                quest = src.quests.questMap["ResearchBluePrint"](itemType=self.itemType,tryHard=self.tryHard)
                self.startWatching(quest,self.unhandledSubQuestFail,"failed")
                return ([quest], None)
            self.fail(reason="no blueprint for "+self.itemType)
            return (None,None)
        return (None,None)
    """
    
    def unhandledSubQuestFail(self,extraParam):
        self.fail(extraParam["reason"])

src.quests.addType(SetUpProductionLine)

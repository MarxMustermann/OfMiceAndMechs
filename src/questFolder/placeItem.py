import src
import random

class PlaceItem(src.quests.MetaQuestSequence):
    type = "PlaceItem"

    def __init__(self, description="place item", creator=None, lifetime=None, targetPosition=None, targetPositionBig=None, itemType=None, tryHard=False, boltDown=False):
        questList = []
        super().__init__(questList, creator=creator, lifetime=lifetime)
        self.metaDescription = "%s %s on position %s on tile %s"%(description,itemType,targetPosition,targetPositionBig,)
        self.targetPosition = targetPosition
        self.targetPositionBig = targetPositionBig
        self.itemType = itemType
        self.tryHard = tryHard
        self.boltDown = boltDown

    def generateTextDescription(self):
        text = """
place item %s on position %s on tile %s."""%(self.itemType,self.targetPosition,self.targetPositionBig,)
        if self.boltDown:
            text += """
Bolt down the item afterwards."""
        
        if self.tryHard:
            text += """

Try as hard as you can to achieve this.
If you don't find the items to place, produce them.
"""

        return text

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character, self.droppedItem, "dropped")
        super().assignToCharacter(character)

    def getQuestMarkersSmall(self,character,renderForTile=False):
        if isinstance(character.container,src.rooms.Room):
            if renderForTile:
                return []
        else:
            if not renderForTile:
                return []

        result = super().getQuestMarkersSmall(character,renderForTile=renderForTile)
        result.append(((self.targetPosition[0]+self.targetPositionBig[0]*15,self.targetPosition[1]+self.targetPositionBig[1]*15),"target"))
        return result


    def droppedItem(self,extraInfo):
        item = extraInfo[1]
        if item.type == self.itemType:
            if item.container.isRoom:
                if item.container.getPosition() == self.targetPositionBig and item.getPosition() == self.targetPosition:
                    self.postHandler()
            else:
                if item.getPosition() == (self.targetPosition[0]+self.targetPositionBig[0]*15,self.targetPosition[1]+self.targetPositionBig[1]*15,0):
                    self.postHandler()

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

    def getSolvingCommandString(self, character, dryRun=True):
        return self.getNextStep(character)[1]

    def generateSubquests(self, character=None):
        (nextQuests,nextCommand) = self.getNextStep(character,ignoreCommands=True)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
            return

    def unhandledSubQuestFail(self,extraParam):
        self.fail(extraParam["reason"])

    def getNextStep(self,character=None,ignoreCommands=False):
        if not self.subQuests:
            itemFound = None
            for item in character.inventory:
                if item.type == self.itemType:
                    itemFound = item
                    break

            if not itemFound:
                if not character.getBigPosition() == (7,7,0):
                    quest = src.quests.questMap["GoToTile"](targetPosition=(7,7,0),description="go to base, workaround")
                    return ([quest],None)

                quest = src.quests.questMap["FetchItems"](toCollect=self.itemType,amount=1,takeAnyUnbolted=True,tryHard=self.tryHard)
                return ([quest],None)

            if not character.getBigPosition() == self.targetPositionBig:
                quest = src.quests.questMap["GoToTile"](targetPosition=self.targetPositionBig,description="go to buildsite")
                return ([quest],None)

            if not character.getSpacePosition() == self.targetPosition:
                quest = src.quests.questMap["GoToPosition"](targetPosition=self.targetPosition,description="go to placement spot")
                return ([quest],None)

            if self.boltDown:
                return (None,"lcb")
            else:
                return (None,"l")
            14/0
            if self.itemType == "MetalBars":
                foundRoom = None
                foundItem = None
                for room in character.getTerrain().rooms:
                    for item in room.itemsOnFloor:
                        if item.type == "ScrapCompactor":
                            foundRoom = room
                            foundItem = item
                            break
                    if foundRoom:
                        break

                if not foundRoom:
                    self.fail("missing machine ScrapCompactor")
                    return

                if not character.getPositionBig() == room.getPosition():
                    quest = src.quests.questMap["GoToTile"](targetPosition=room.getPosition())
                    return ([quest], None)

                items = foundItem.container.getItemByPosition(foundItem.getPosition(offset=(-1,0,0)))
                if not items or not items[-1].type == "Scrap":
                    if not character.inventory or not character.inventory[-1].type == "Scrap":
                        scrapField = random.choice(character.getTerrain().scrapFields)

                        quest1 = src.quests.questMap["GoToTile"](targetPosition=room.getPosition())
                        quest2 = src.quests.questMap["GatherScrap"](targetPosition=scrapField)
                        quest3 = src.quests.questMap["GoToTile"](targetPosition=scrapField)
                        return ([quest1,quest2,quest3], None)

                    if character.getDistance(item.getPosition(offset=(-1,0,0))) > 1:
                        quest = src.quests.questMap["GoToPosition"](targetPosition=item.getPosition(offset=(-1,0,0)),ignoreEndBlocked=True)
                        return ([quest], None)

                    offsets = {(0,0,0):"l",(1,0,0):"Ld",(-1,0,0):"La",(0,1,0):"Ls",(0,-1,0):"Lw"}
                    for (offset,command) in offsets.items():
                        if character.getPosition(offset=offset) == foundItem.getPosition(offset=(-1,0,0)):
                            return (None, command)

                if character.getDistance(foundItem.getPosition()) > 1:
                    quest = src.quests.questMap["GoToPosition"](targetPosition=foundItem.getPosition(),ignoreEndBlocked=True)
                    return ([quest], None)

                offsets = {(0,0,0):"j",(1,0,0):"Jd",(-1,0,0):"Ja",(0,1,0):"Js",(0,-1,0):"Jw"}
                for (offset,command) in offsets.items():
                    if character.getPosition(offset=offset) == foundItem.getPosition():
                        return (None, command)
                1/0

            foundMachine = None
            for room in character.getTerrain().rooms:
                for item in room.itemsOnFloor:
                    if item.type == "Machine" and item.toProduce == self.itemType:
                        foundMachine = item
                        break
                if foundMachine:
                    break

            if foundMachine:
                neededItems = src.items.rawMaterialLookup.get(self.itemType,[])[:]
                inputOffsets = [(-1,0,0),(0,1,0),(0,-1,0)]
                counter = 0
                for neededItem in neededItems:
                    inputOffset = inputOffsets[counter]
                    items = foundMachine.container.getItemByPosition(foundMachine.getPosition(offset=inputOffset))
                    if not items or not items[-1].type == neededItem:
                        if not character.inventory or not character.inventory[-1].type == neededItem:
                            if self.tryHard:
                                quest1 = src.quests.questMap["FetchItems"](toCollect=neededItem,amount=1,takeAnyUnbolted=True,tryHard=True)
                                self.startWatching(quest1,self.unhandledSubQuestFail,"failed")
                                quest2 = src.quests.questMap["GoToTile"](targetPosition=foundMachine.container.getPosition())
                                quest3 = src.quests.questMap["GoToPosition"](targetPosition=foundMachine.getPosition(offset=inputOffset))
                                return ([quest1,quest2,quest3],None)
                            self.fail("missing resource %s"%(neededItem,))
                            return (None,None)

                        if not character.container == foundMachine.container:
                            quest = src.quests.questMap["GoToTile"](targetPosition=foundMachine.container.getPosition())
                            return ([quest], None)


                        if character.getDistance(foundMachine.getPosition(offset=inputOffset)) > 1:
                            quest = src.quests.questMap["GoToPosition"](targetPosition=foundMachine.getPosition(offset=inputOffset))
                            return ([quest], None)

                        offsets = {(0,0,0):"l",(1,0,0):"Ld",(-1,0,0):"La",(0,1,0):"Ls",(0,-1,0):"Lw"}
                        for (offset,command) in offsets.items():
                            if character.getPosition(offset=offset) == foundMachine.getPosition(inputOffset):
                                return (None, command)
                        1/0
                    counter += 1

                if not character.container == foundMachine.container:
                    quest = src.quests.questMap["GoToTile"](targetPosition=foundMachine.container.getPosition())
                    return ([quest], None)

                if character.getDistance(foundMachine.getPosition()) > 1:
                    quest = src.quests.questMap["GoToPosition"](targetPosition=foundMachine.getPosition(),ignoreEndBlocked=True)
                    return ([quest], None)

                offsets = {(0,0,0):"j",(1,0,0):"Jd",(-1,0,0):"Ja",(0,1,0):"Js",(0,-1,0):"Jw"}
                for (offset,command) in offsets.items():
                    if character.getPosition(offset=offset) == foundMachine.getPosition():
                        return (None, command)
                1/0

            if self.tryHard:
                quest = src.quests.questMap["SetUpMachine"](itemType=self.itemType,tryHard=self.tryHard)
                self.startWatching(quest,self.unhandledSubQuestFail,"failed")
                return ([quest], None)

            self.fail("no machine for "+self.itemType)
            return (None,None)
        return (None,None)
    
    def triggerCompletionCheck(self,character=None):
        return False

src.quests.addType(PlaceItem)

import src


class ProduceItem(src.quests.MetaQuestSequenceV2):
    type = "ProduceItem"

    def __init__(self, description="produce item", creator=None, command=None, lifetime=None, targetPosition=None, itemType=None,tryHard=False,reason=None):
        questList = []
        super().__init__(questList, creator=creator, lifetime=lifetime)
        self.metaDescription = description+" "+itemType
        self.targetPosition = targetPosition
        self.itemType = itemType
        self.tryHard = tryHard
        self.reason = reason

    def generateTextDescription(self):
        reason = ""
        if self.reason:
            reason = f", to {self.reason}"
        text = f"""
produce {self.itemType}{reason}.

"""

        neededItems = src.items.rawMaterialLookup.get(self.itemType,[])[:]
        text += f"""
{self.itemType} are produced by a {self.itemType} machine (X\\).
{", ".join(neededItems)} are needed as raw material.
Examine the {self.itemType} machine to get detailed information.
"""

        if self.tryHard:
            text += f"""
Try as hard as you can to achieve this.
If you don't find the raw materials, produce them.
If you don't find a {self.itemType} machine needed, build it.
"""

        return text

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character, self.producedItem, "producedItem")
        super().assignToCharacter(character)

    def producedItem(self,extraInfo):
        if not self.active:
            return

        if extraInfo["item"].type == self.itemType:
            self.postHandler()

    def unhandledSubQuestFail(self,extraParam):
        self.fail(extraParam["reason"])

    def getNextStep(self,character=None,ignoreCommands=False, dryRun = True):
        if not self.subQuests:
            if self.itemType == "MetalBars":
                foundRoom = None
                foundItem = None
                for room in character.getTerrain().rooms:
                    for item in room.itemsOnFloor:
                        if item.bolted and item.type == "ScrapCompactor":
                            foundRoom = room
                            foundItem = item
                            break
                    if foundRoom:
                        break

                if not foundRoom:
                    self.fail("missing machine ScrapCompactor")
                    return None

                if character.getBigPosition() != room.getPosition():
                    quest = src.quests.questMap["GoToTile"](targetPosition=room.getPosition())
                    return ([quest], None)

                items = foundItem.container.getItemByPosition(foundItem.getPosition(offset=(-1,0,0)))
                if not items or items[-1].type != "Scrap":
                    quest = src.quests.questMap["PlaceItem"](targetPosition=foundItem.getPosition(offset=(-1,0,0)),targetPositionBig=foundItem.container.getPosition(),itemType="Scrap",tryHard=self.tryHard)
                    return ([quest], None)
                """
                    if not character.inventory or not character.inventory[-1].type == "Scrap":
                        scrapField = random.choice(character.getTerrain().scrapFields)

                        quest1 = src.quests.questMap["GoToTile"](targetPosition=room.getPosition())
                        quest2 = src.quests.questMap["GatherScrap"](targetPosition=scrapField)
                        quest3 = src.quests.questMap["GoToTile"](targetPosition=scrapField)
                        return ([quest3,quest2,quest1], None)

                    if character.getDistance(item.getPosition(offset=(-1,0,0))) > 1:
                        quest = src.quests.questMap["GoToPosition"](targetPosition=item.getPosition(offset=(-1,0,0)),ignoreEndBlocked=True)
                        return ([quest], None)

                    offsets = {(0,0,0):"l",(1,0,0):"Ld",(-1,0,0):"La",(0,1,0):"Ls",(0,-1,0):"Lw"}
                    for (offset,command) in offsets.items():
                        if character.getPosition(offset=offset) == foundItem.getPosition(offset=(-1,0,0)):
                            return (None, (command,"place scrap to compact"))
                """

                items = foundItem.container.getItemByPosition(foundItem.getPosition(offset=(1,0,0)))
                if items:
                    quest = src.quests.questMap["CleanSpace"](targetPosition=foundItem.getPosition(offset=(1,0,0)),targetPositionBig=room.getPosition())
                    return ([quest], None)

                if character.getDistance(foundItem.getPosition()) > 1:
                    quest = src.quests.questMap["GoToPosition"](targetPosition=foundItem.getPosition(),ignoreEndBlocked=True)
                    return ([quest], None)

                offsets = {(0,0,0):"j",(1,0,0):"Jd",(-1,0,0):"Ja",(0,1,0):"Js",(0,-1,0):"Jw"}
                for (offset,command) in offsets.items():
                    if character.getPosition(offset=offset) == foundItem.getPosition():
                        return (None, (command,"use the ScrapCompactor"))
                1/0

            foundMachine = None
            for room in character.getTerrain().rooms:
                for item in room.itemsOnFloor:
                    if not (item.type == "Machine" and item.toProduce == self.itemType):
                        continue
                    if not item.bolted:
                        continue
                    foundMachine = item
                    break
                if foundMachine:
                    break

            if foundMachine:
                neededItems = src.items.rawMaterialLookup.get(self.itemType,[])[:]
                inputOffsets = [(-1,0,0),(0,1,0),(0,-1,0)]
                for neededItem in neededItems:
                    foundItem = False
                    for inputOffset in inputOffsets:
                        items = foundMachine.container.getItemByPosition(foundMachine.getPosition(offset=inputOffset))
                        if not items or items[-1].type != neededItem:
                            continue
                        foundItem = True
                        break

                    if foundItem:
                        continue

                    enptyInputOffsets = []
                    for inputOffset in inputOffsets:
                        items = foundMachine.container.getItemByPosition(foundMachine.getPosition(offset=inputOffset))
                        if items and not items[-1].walkable:
                            continue
                        if items and len(items) < 25:
                            continue
                        enptyInputOffsets.append(inputOffset)

                    preferedOffset = None
                    for inputOffset in enptyInputOffsets:
                        newPos = foundMachine.getPosition(offset=inputOffset)
                        for inputStockpile in foundMachine.container.inputSlots:
                            if inputStockpile[0] != newPos:
                                continue
                            if inputStockpile[1] != neededItem:
                                continue

                            quest = src.quests.questMap["PlaceItem"](targetPosition=foundMachine.getPosition(offset=inputOffset),targetPositionBig=foundMachine.container.getPosition(),itemType=neededItem,tryHard=self.tryHard)
                            return ([quest], None)


                    if enptyInputOffsets:
                        inputOffset = enptyInputOffsets[0]
                        quest = src.quests.questMap["PlaceItem"](targetPosition=foundMachine.getPosition(offset=inputOffset),targetPositionBig=foundMachine.container.getPosition(),itemType=neededItem,tryHard=self.tryHard)
                        return ([quest], None)

                items = foundMachine.container.getItemByPosition(foundMachine.getPosition(offset=(1,0,0)))
                if items:
                    quest = src.quests.questMap["CleanSpace"](targetPosition=foundMachine.getPosition(offset=(1,0,0)),targetPositionBig=room.getPosition())
                    return ([quest], None)

                if character.container != foundMachine.container:
                    quest = src.quests.questMap["GoToTile"](targetPosition=foundMachine.container.getPosition())
                    return ([quest], None)

                if character.getDistance(foundMachine.getPosition()) > 1:
                    quest = src.quests.questMap["GoToPosition"](targetPosition=foundMachine.getPosition(),ignoreEndBlocked=True)
                    return ([quest], None)

                if not foundMachine.checkCoolDownEnded():
                    return (None,("10.","wait for the machine to be ready again"))

                offsets = {(0,0,0):"j",(1,0,0):"Jd",(-1,0,0):"Ja",(0,1,0):"Js",(0,-1,0):"Jw"}
                for (offset,command) in offsets.items():
                    if character.getPosition(offset=offset) == foundMachine.getPosition():
                        return (None, (command,"use the machine"))
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

src.quests.addType(ProduceItem)

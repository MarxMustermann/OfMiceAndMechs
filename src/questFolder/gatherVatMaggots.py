import src
import random

class GatherVatMaggots(src.quests.MetaQuestSequenceV2):
    type = "GatherVatMaggots"

    def __init__(self, description="gather vat maggots", creator=None, targetPosition=None,lifetime=None):
        questList = []
        super().__init__(questList, creator=creator,lifetime=lifetime)
        self.metaDescription = description

        if targetPosition:
            self.setParameters({"targetPosition":targetPosition})

    def generateTextDescription(self):
        return """

"""

    def wrapedTriggerCompletionCheck(self, extraInfo):
        if not self.active:
            return

        self.triggerCompletionCheck(extraInfo[0])

    def setParameters(self,parameters):
        if "targetPosition" in parameters and "targetPosition" in parameters:
            self.targetPosition = parameters["targetPosition"]
        return super().setParameters(parameters)

    def getRequiredParameters(self):
        parameters = super().getRequiredParameters()
        parameters.append({"name":"targetPosition","type":"coordinate"})
        return parameters

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.wrapedTriggerCompletionCheck, "moved")
        super().assignToCharacter(character)

    def triggerCompletionCheck(self,character=None):
        if self.completed:
            return

        if not character:
            return

        if not character.getFreeInventorySpace() < 1:
            return

        if character.inventory[-1].type != "VatMaggot":
            return

        self.postHandler()

    def getNextStep(self, character=None, ignoreCommands=False, dryRun = True):

        self.triggerCompletionCheck(character)

        if character.getFreeInventorySpace() < 1 and character.inventory[-1].type != "VatMaggot":
           quest = src.quests.questMap["ClearInventory"]()
           return ([quest],None)

        foundDirectPickup = None
        for direction in ((-1,0),(1,0),(0,-1),(0,1),(0,0)):
            neighbour = (character.xPosition+direction[0],character.yPosition+direction[1],character.zPosition)
            items = character.container.getItemByPosition(neighbour)
            if items and items[-1].type == "VatMaggot":
                foundDirectPickup = (neighbour,direction)
                break

        if foundDirectPickup:
            if foundDirectPickup[1] == (-1,0):
                command = "Ka"
            if foundDirectPickup[1] == (1,0):
                command = "Kd"
            if foundDirectPickup[1] == (0,-1):
                command = "Kw"
            if foundDirectPickup[1] == (0,1):
                command = "Ks"
            if foundDirectPickup[1] == (0,0):
                command = "k"
            return (None,(command,"pickup maggot"))

        items = character.container.getNearbyItems(character)
        maggotFound = None
        treeFound = None
        for item in items:
            if item.type == "VatMaggot":
                maggotFound = item
                break
            if item.type == "Tree":
                treeFound = item

        if maggotFound:
            quest = src.quests.questMap["GoToPosition"](targetPosition=maggotFound.getSmallPosition(),ignoreEndBlocked=True)
            return ([quest],None)

        if treeFound:
            foundDirectTree = None
            for direction in ((-1,0),(1,0),(0,-1),(0,1),(0,0)):
                neighbour = (character.xPosition+direction[0],character.yPosition+direction[1],character.zPosition)
                items = character.container.getItemByPosition(neighbour)
                if items and items[-1].type == "Tree":
                    foundDirectTree = (neighbour,direction)
                    break

            if foundDirectTree:
                if foundDirectTree[1] == (-1,0):
                    command = "Ja"
                if foundDirectTree[1] == (1,0):
                    command = "Jd"
                if foundDirectTree[1] == (0,-1):
                    command = "Jw"
                if foundDirectTree[1] == (0,1):
                    command = "Js"
                if foundDirectTree[1] == (0,0):
                    command = "j"
                if treeFound.numMaggots == 0:
                    command = "500."+command
                return (None,(command,"pickup maggot"))

            quest = src.quests.questMap["GoToPosition"](targetPosition=treeFound.getSmallPosition(),ignoreEndBlocked=True)
            return ([quest],None)

        self.fail(reason="no tree")
        return (None,None)
    @staticmethod
    def generateDutyQuest(beUsefull,character,currentRoom):
        terrain = character.getTerrain()
        if terrain.alarm:
            return None
        for room in beUsefull.getRandomPriotisedRooms(character,currentRoom):
            emptyInputSlots = room.getEmptyInputslots(itemType="VatMaggot")
            if emptyInputSlots:
                for inputSlot in emptyInputSlots:
                    if inputSlot[1] != "VatMaggot":
                        continue

                    source = None
                    if room.sources:
                        for potentialSource in random.sample(list(room.sources),len(room.sources)):
                            if potentialSource[1] == "rawVatMaggots":
                                source = potentialSource
                                break

                    if source is None and not character.getTerrain().forests:
                        continue

                    if src.quests.questMap["ClearInventory"].generateDutyQuest(beUsefull,character,room):
                        beUsefull.idleCounter = 0
                        return True

                    if source:
                        pos = source[0]
                    else:
                        pos = random.choice(character.getTerrain().forests)

                    beUsefull.addQuest(src.quests.questMap["RestockRoom"](toRestock="VatMaggot"))
                    beUsefull.addQuest(src.quests.questMap["GoToTile"](targetPosition=(room.xPosition,room.yPosition)))
                    beUsefull.addQuest(src.quests.questMap["GatherVatMaggots"](targetPosition=pos))
                    beUsefull.addQuest(src.quests.questMap["GoToTile"](targetPosition=pos))
                    beUsefull.idleCounter = 0
                    return True
        return None

src.quests.addType(GatherVatMaggots)

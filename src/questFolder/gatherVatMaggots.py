import src


class GatherVatMaggots(src.quests.MetaQuestSequence):
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

    def solver(self, character):

        self.triggerCompletionCheck(character)

        if self.subQuests:
            return super().solver(character)

        if character.getFreeInventorySpace() < 1 and character.inventory[-1].type != "VatMaggot":
            self.addQuest(src.quests.questMap["ClearInventory"]())
            return None

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
            character.runCommandString(command)
            return None

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
            quest.assignToCharacter(character)
            quest.activate()
            self.addQuest(quest)
            return None

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
                character.runCommandString(command)
                return None

            quest = src.quests.questMap["GoToPosition"](targetPosition=treeFound.getSmallPosition(),ignoreEndBlocked=True)
            quest.assignToCharacter(character)
            quest.activate()
            self.addQuest(quest)
            return None

        self.fail(reason="no tree")
        return None

src.quests.addType(GatherVatMaggots)

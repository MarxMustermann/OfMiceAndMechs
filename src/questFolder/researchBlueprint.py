import src


class ResearchBluePrint(src.quests.MetaQuestSequence):
    type = "ResearchBluePrint"

    def __init__(self, description="research blueprint", creator=None, command=None, lifetime=None, targetPosition=None, itemType=None, tryHard=False,reason=None):
        questList = []
        super().__init__(questList, creator=creator, lifetime=lifetime)
        self.metaDescription = description+" "+itemType
        self.shortCode = "M"
        self.targetPosition = targetPosition
        self.itemType = itemType
        self.tryHard = tryHard
        self.reason = reason

    def generateTextDescription(self):
        reason = ""
        if self.reason:
            reason = f",\nto {self.reason}"
        text = f"""
research a blueprint for {self.itemType}{reason}.

"""

        neededItems = src.items.rawMaterialLookup.get(self.itemType,[])[:]
        text += f"""
Blueprints are produced by a blueprinter (sX).
{", ".join(self.getNeededResources())} is needed to research a blueprint for {self.itemType}.
You also need a sheet to print the blueprint on.
Examine the blueprinter for more details.
"""

        if self.tryHard:
            text += """
Try as hard as you can to achieve this.
If you miss resources, produce them.
"""

        return text

    def getNeededResources(self):
        itemMap = {
                    "Case"            :["Frame","MetalBars"],
                    "Frame"           :["Rod","MetalBars"],
                    "Rod"             :["Rod"],
                    "ScrapCompactor"  :["Scrap"],
                    "Wall"            :["MetalBars"],
                    "Door"            :["Connector"],
                    "Connector"       :["Mount","MetalBars"],
                    "Mount"           :["Mount"],
                    "Sheet"           :["Sheet"],
                    "GooFlask"        :["Tank"],
                    "Heater"          :["Radiator","MetalBars"],
                    "MemoryCell"      :["Connector","MetalBars"],
                    "Tank"            :["Sheet","MetalBars"],
                    "Painter"         :["Tank", "Heater"],
                  }
        if self.itemType not in itemMap:
            raise Exception("no known base ressources for {self.itemType}")
        return itemMap.get(self.itemType)

    def solver(self, character):
        (nextQuests,nextCommand) = self.getNextStep(character)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
            return

        if nextCommand:
            character.runCommandString(nextCommand[0])
            return
        super().solver(character)

    def generateSubquests(self, character=None):
        (nextQuests,nextCommand) = self.getNextStep(character,ignoreCommands=True)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
            return

    def getNextStep(self,character=None,ignoreCommands=False):
        if not self.subQuests:
            room = character.getTerrain().getRoomByPosition((7,7,0))[0]
            items = room.getItemByPosition((9,7,0))
            if not items or items[-1].type != "Sheet":
                quest = src.quests.questMap["PlaceItem"](targetPosition=(9,7,0),targetPositionBig=room.getPosition(),itemType="Sheet",tryHard=self.tryHard)
                return ([quest],None)

            neededResources = self.getNeededResources()

            counter = 0
            for neededResource in neededResources:
                items = room.getItemByPosition((8,8,0))
                if (not len(items) > counter) or (items[-1 - counter].type != neededResource):
                    quest = src.quests.questMap["PlaceItem"](targetPosition=(8,8,0),targetPositionBig=room.getPosition(),itemType=neededResource,tryHard=self.tryHard)
                    return ([quest],None)
                counter += 1

            if character.getBigPosition() != (7, 7, 0):
                quest = src.quests.questMap["GoToTile"](targetPosition=(7,7,0))
                return ([quest],None)
            if character.getDistance((9,8,0)) > 1:
                quest = src.quests.questMap["GoToPosition"](targetPosition=(9,8,0),ignoreEndBlocked=True)
                return ([quest],None)

            directions = [((0,0,0),"."),((0,1,0),"s"),((1,0,0),"d"),((0,-1,0),"w"),((-1,0,0),"a")]
            directionFound = None
            for direction in directions:
                if character.getPosition(offset=direction[0]) == (9,8,0):
                    return (None,("J"+direction[1],"research blueprint"))
            1/0

        return (None,None)

    def triggerCompletionCheck(self,character=None):
        return False

    def getSolvingCommandString(self, character, dryRun=True):
        nextStep = self.getNextStep(character)
        if nextStep == (None,None):
            return super().getSolvingCommandString(character)
        return self.getNextStep(character)[1]

    def producedBlueprint(self,extraInfo):
        if extraInfo["itemType"] == self.itemType:
            self.postHandler()

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character, self.producedBlueprint, "producedBlueprint")
        super().assignToCharacter(character)

    def unhandledSubQuestFail(self,extraParam):
        self.fail(extraParam["reason"])

src.quests.addType(ResearchBluePrint)

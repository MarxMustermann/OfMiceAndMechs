import src

class DrawBuildSite(src.quests.MetaQuestSequence):
    type = "DrawBuildSite"

    def __init__(self, description="draw buildsite", creator=None, targetPosition=None, targetPositionBig=None,itemType=None,stockpileType=None,tryHard=False,reason=None,extraInfo=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        self.targetPosition = targetPosition
        self.targetPositionBig = targetPositionBig
        self.itemType = itemType
        self.tryHard = tryHard
        self.painterPos = None
        if not extraInfo:
            self.extraInfo = {}
        else:
            self.extraInfo = extraInfo
        self.reason = reason

    def triggerCompletionCheck(self,character=None):
        if not character:
            return

        room = character.getTerrain().getRoomByPosition(self.targetPositionBig)[0]
        for buildSite in room.buildSites:
            if buildSite[0] == self.targetPosition:
                self.postHandler()
                return True

    def generateTextDescription(self):
        reason = ""
        if self.reason:
            reason = f", to {self.reason}"
        text = """
draw buildsite

"""

        text += """
Buildsites are drawn using a Painter (xi).
Examine the Painter for more details.
"""

        if self.tryHard:
            text += """
Try as hard as you can to achieve this.
"""

        return text

    def solver(self, character):
        (nextQuests,nextCommand) = self.getNextStep(character,dryRun=False)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
            return

        if nextCommand:
            character.runCommandString(nextCommand[0])
            return
        super().solver(character)

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

    def getNextStep(self,character=None,ignoreCommands=False,dryRun=True):
        if not self.subQuests:
            submenue = character.macroState.get("submenue")
            if submenue:
                if submenue.tag == "paintModeSelection":
                    if submenue.text == "":
                        return (None,(["b"],"to configure the painter to build site"))
                    elif submenue.text == "b":
                        return (None,(["enter"],"to configure the painter to nuild site"))
                    else:
                        return (None,(["backspace"],"to delete input"))

                if submenue.tag == "paintTypeSelection":
                    itemType = self.itemType
                    if not itemType:
                        itemType = ""

                    if itemType == submenue.text:
                        return (None,(["enter"],"to configure the item type"))

                    correctIndex = 0
                    while correctIndex < len(itemType) and correctIndex < len(submenue.text):
                        if not itemType[correctIndex] == submenue.text[correctIndex]:
                            break
                        correctIndex += 1

                    if correctIndex < len(submenue.text):
                        return (None,(["backspace"],"to delete input"))

                    return (None,(itemType[correctIndex:],"to enter type"))

                if submenue.tag == "paintExtraParamName":
                    nameToSet = "toProduce"

                    if nameToSet == submenue.text:
                        return (None,(["enter"],"to set the name of the extra parameter"))

                    correctIndex = 0
                    while correctIndex < len(nameToSet) and correctIndex < len(submenue.text):
                        if not nameToSet[correctIndex] == submenue.text[correctIndex]:
                            break
                        correctIndex += 1

                    if correctIndex < len(submenue.text):
                        return (None,(["backspace"],"to delete input"))

                    return (None,(nameToSet[correctIndex:],"to enter name of the extra parameter"))

                if submenue.tag == "paintExtraParamValue":
                    valueToSet = self.extraInfo["toProduce"]

                    if valueToSet == submenue.text:
                        return (None,(["enter"],"to set the value of the extra parameter"))

                    correctIndex = 0
                    while correctIndex < len(valueToSet) and correctIndex < len(submenue.text):
                        if not valueToSet[correctIndex] == submenue.text[correctIndex]:
                            break
                        correctIndex += 1

                    if correctIndex < len(submenue.text):
                        return (None,(["backspace"],"to delete input"))

                    return (None,(valueToSet[correctIndex:],"to enter value of the extra parameter"))

            rooms = character.getTerrain().getRoomByPosition(self.targetPositionBig)
            if not rooms:
                if not dryRun:
                    self.fail("target room missing")
                return (None,None)
            room = rooms[0]

            for buildSite in room.buildSites:
                if buildSite[0] == self.targetPosition:
                    if not dryRun:
                        self.postHandler()
                    return (None,None)

            offsets = ((0,0,0),(0,1,0),(1,0,0),(0,-1,0),(-1,0,0))
            foundOffset = None
            for offset in offsets:
                items = room.getItemByPosition((self.targetPosition[0]+offset[0],self.targetPosition[1]+offset[1],self.targetPosition[2]+offset[2]))
                if not items or not items[-1].type == "Painter":
                    continue

                foundOffset = (offset,items[-1])
            if foundOffset:
                item = foundOffset[1]
                if character.getDistance(item.getPosition()) > 0:
                    quest = src.quests.questMap["GoToPosition"](targetPosition=item.getPosition(),reason="get to the painter")
                    return ([quest],None)

                if not item.paintMode == "buildSite":
                    return (None,(["c","m","b","enter"],"to configure the painter to paint build site"))

                if not (self.itemType == item.paintType):
                    return (None,(["c","t"] + list(self.itemType) + ["enter"],"to configure the item type for the build site"))

                for (key,value) in item.paintExtraInfo.items():
                    if not key in self.extraInfo:
                        return (None,(["c","c"],"to clear the painters extra info"))

                for (key,value) in self.extraInfo.items():
                    if (not key in item.paintExtraInfo) or (not value == item.paintExtraInfo[key]):
                        return (None,(["c","e",key,"enter",value,"enter"],"to clear the painters extra info"))

                if not (item.offset == (0,0,0)):
                    return (None,(["c","d","."] + ["enter"],"to remove the offset from the painter"))

                return (None,("jk","draw to stockpile"))

            if not self.painterPos:
                if not character.inventory or not character.inventory[-1].type == "Painter":
                    quest = src.quests.questMap["FetchItems"](toCollect="Painter",amount=1,reason="be able to draw a stockpile")
                    return ([quest],None)
                painter = character.inventory[-1]

            if not character.getBigPosition() == self.targetPositionBig:
                quest = src.quests.questMap["GoToTile"](targetPosition=self.targetPositionBig,reason="get nearby to the drawing spot")
                return ([quest],None)

            if character.getDistance(self.targetPosition) > 0:
                quest = src.quests.questMap["GoToPosition"](targetPosition=self.targetPosition,reason="get to the drawing spot")
                return ([quest],None)

            return (None,("l","drop the Painter"))

        return (None,None)

    def getQuestMarkersTile(self,character):
        result = super().getQuestMarkersTile(character)
        result.append(((self.targetPositionBig[0],self.targetPositionBig[1]),"target"))
        return result

    def getQuestMarkersSmall(self,character,renderForTile=False):
        if isinstance(character.container,src.rooms.Room):
            if renderForTile:
                return []
        else:
            if not renderForTile:
                return []

        result = super().getQuestMarkersSmall(character,renderForTile=renderForTile)
        if renderForTile:
            result.append(((self.targetPosition[0]+self.targetPositionBig[0]*15,self.targetPosition[1]+self.targetPositionBig[1]*15),"target"))
        else:
            if character.getBigPosition() == self.targetPositionBig:
                result.append(((self.targetPosition[0],self.targetPosition[1]),"target"))
        return result

    def handleDrewMarking(self,extraInfo):
        if not self.active:
            return
        if self.completed:
            1/0

        self.triggerCompletionCheck(self.character)

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.handleDrewMarking, "drew marking")

        return super().assignToCharacter(character)

src.quests.addType(DrawBuildSite)

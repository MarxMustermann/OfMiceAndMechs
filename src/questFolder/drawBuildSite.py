import src


class DrawBuildSite(src.quests.MetaQuestSequence):
    '''
    quest to draw a build site
    '''
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
        '''
        check for quest completion and end quest
        '''

        # abort on weird state
        if not character:
            return False

        # end the quest if build site exists
        room = character.getTerrain().getRoomByPosition(self.targetPositionBig)[0]
        for buildSite in room.buildSites:
            if buildSite[0] == self.targetPosition:
                self.postHandler()
                return True
        return False

    def generateTextDescription(self):
        '''
        generates a text description
        '''
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


    def getNextStep(self,character=None,ignoreCommands=False,dryRun=True):
        '''
        generates next step to solve the quest
        TDOD: use painter in hand -_-
        '''
        if self.subQuests:
            return (None,None)

        # navigate the painter menu
        submenue = character.macroState.get("submenue")
        if submenue:
            # select the right paint mode
            if submenue.tag == "paintModeSelection":
                if submenue.text == "":
                    return (None,(["b"],"configure the painter to build site"))
                elif submenue.text == "b":
                    return (None,(["enter"],"configure the painter to build site"))
                else:
                    return (None,(["backspace"],"delete input"))

            # select the right item type
            if submenue.tag == "paintTypeSelection":
                itemType = self.itemType
                if not itemType:
                    itemType = ""

                if itemType == submenue.text:
                    return (None,(["enter"],"configure the item type"))

                correctIndex = 0
                while correctIndex < len(itemType) and correctIndex < len(submenue.text):
                    if itemType[correctIndex] != submenue.text[correctIndex]:
                        break
                    correctIndex += 1

                if correctIndex < len(submenue.text):
                    return (None,(["backspace"],"delete input"))

                return (None,(itemType[correctIndex:],"enter type"))

            # enter the name for extra parameters
            if submenue.tag == "paintExtraParamName":
                nameToSet = "toProduce"

                if nameToSet == submenue.text:
                    return (None,(["enter"],"set the name of the extra parameter"))

                correctIndex = 0
                while correctIndex < len(nameToSet) and correctIndex < len(submenue.text):
                    if nameToSet[correctIndex] != submenue.text[correctIndex]:
                        break
                    correctIndex += 1

                if correctIndex < len(submenue.text):
                    return (None,(["backspace"],"delete input"))

                return (None,(nameToSet[correctIndex:],"enter name of the extra parameter"))

            # enter the value for extra parameters
            if submenue.tag == "paintExtraParamValue":
                valueToSet = self.extraInfo["toProduce"]

                if valueToSet == submenue.text:
                    return (None,(["enter"],"set the value of the extra parameter"))

                correctIndex = 0
                while correctIndex < len(valueToSet) and correctIndex < len(submenue.text):
                    if valueToSet[correctIndex] != submenue.text[correctIndex]:
                        break
                    correctIndex += 1

                if correctIndex < len(submenue.text):
                    return (None,(["backspace"],"delete input"))

                return (None,(valueToSet[correctIndex:],"enter value of the extra parameter"))

        # get target room
        rooms = character.getTerrain().getRoomByPosition(self.targetPositionBig)
        if not rooms:
            if not dryRun:
                self.fail("target room missing")
            return (None,None)
        room = rooms[0]

        # do extra check for completion, lol
        for buildSite in room.buildSites:
            if buildSite[0] == self.targetPosition:
                if not dryRun:
                    self.postHandler()
                return (None,None)

        # check for painters next to the target
        offsets = ((0,0,0),(0,1,0),(1,0,0),(0,-1,0),(-1,0,0))
        foundOffset = None
        for offset in offsets:
            items = room.getItemByPosition((self.targetPosition[0]+offset[0],self.targetPosition[1]+offset[1],self.targetPosition[2]+offset[2]))
            if not items or items[-1].type != "Painter":
                continue

            foundOffset = (offset,items[-1])

        # use the painter to draw
        if foundOffset:
            item = foundOffset[1]
            if character.getDistance(item.getPosition()) > 0:
                quest = src.quests.questMap["GoToPosition"](targetPosition=item.getPosition(),reason="get to the painter")
                return ([quest],None)

            if item.paintMode != "buildSite":
                return (None,(["c","m","b","enter"],"configure the painter to paint build site"))

            if self.itemType != item.paintType:
                return (None,(["c", "t", *list(self.itemType), "enter"],"configure the item type for the build site"))

            for (key,_value) in item.paintExtraInfo.items():
                if key not in self.extraInfo:
                    return (None,(["c","c"],"clear the painters extra info"))

            for (key,value) in self.extraInfo.items():
                if (key not in item.paintExtraInfo) or (value != item.paintExtraInfo[key]):
                    return (None,(["c","e",key,"enter",value,"enter"],"clear the painters extra info"))

            if item.offset != (0, 0, 0):
                return (None,(["c", "d", ".", "enter"],"remove the offset from the painter"))

            return (None,("jk","draw to stockpile"))

        # fetch a painter
        if not self.painterPos:
            if not character.inventory or character.inventory[-1].type != "Painter":
                quest = src.quests.questMap["FetchItems"](toCollect="Painter",amount=1,reason="be able to draw a stockpile")
                return ([quest],None)
            painter = character.inventory[-1]

        # go to drawing spot
        if character.getBigPosition() != self.targetPositionBig:
            quest = src.quests.questMap["GoToTile"](targetPosition=self.targetPositionBig,reason="get nearby to the drawing spot")
            return ([quest],None)
        if character.getDistance(self.targetPosition) > 0:
            quest = src.quests.questMap["GoToPosition"](targetPosition=self.targetPosition,reason="get to the drawing spot")
            return ([quest],None)

        # clear spot
        if character.container.getItemByPosition(self.targetPosition):
            quest = src.quests.questMap["CleanSpace"](targetPosition=self.targetPosition,reason="unclutter the drawing spot",targetPositionBig=self.targetPositionBig,pickupBolted=True,)
            return ([quest],None)

        # drop painter next to target
        return (None,("l","drop the Painter"))

    def getQuestMarkersTile(self,character):
        '''
        returns quest markers for the minimap
        '''
        result = super().getQuestMarkersTile(character)
        result.append(((self.targetPositionBig[0],self.targetPositionBig[1]),"target"))
        return result

    def getQuestMarkersSmall(self,character,renderForTile=False):
        '''
        returns quest markers for the normal map
        '''
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
        '''
        handle the event indicating quest completion
        '''
        if not self.active:
            return
        if self.completed:
            1/0

        self.triggerCompletionCheck(self.character)

    def assignToCharacter(self, character):
        '''
        assign the quest to a character
        '''
        if self.character:
            return None

        self.startWatching(character,self.handleDrewMarking, "drew marking")

        return super().assignToCharacter(character)

    def handleQuestFailure(self,extraParam):
        '''
        fail recursively
        '''
        self.fail(reason=extraParam["reason"])
        super().handleQuestFailure(extraParam)

# register quest
src.quests.addType(DrawBuildSite)

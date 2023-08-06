import src

class DrawWalkingSpace(src.quests.MetaQuestSequence):
    type = "DrawWalkingSpace"

    def __init__(self, description="draw walking space", creator=None, targetPosition=None, targetPositionBig=None,tryHard=False,reason=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        self.targetPosition = targetPosition
        self.targetPositionBig = targetPositionBig
        self.tryHard = tryHard
        self.painterPos = None
        self.reason = reason

    def triggerCompletionCheck(self,character=None):
        if not character:
            return

    def generateTextDescription(self):
        reason = ""
        if self.reason:
            reason = ", to %s"%(self.reason,)
        text = """
draw a walkingspace on position %s on tile %s%s.

"""%(self.targetPosition,self.targetPositionBig,reason)

        text += """
Walkingspaces are drawn using a Painter (xw).
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

    def getNextStep(self,character=None,ignoreCommands=False, dryRun=True):
        if not self.subQuests:
            rooms = character.getTerrain().getRoomByPosition(self.targetPositionBig)
            if not rooms:
                if dryRun:
                    self.fail("target room missing")
                return (None,None)
            room = rooms[0]

            for pos in room.walkingSpace:
                if pos == self.targetPosition:
                    if not dryRun:
                        self.postHandler()
                    return (None,None)

            offsets = ((0,0,0),(0,1,0),(1,0,0),(0,-1,0),(-1,0,0))
            foundOffset = None
            for offset in offsets:
                items = room.getItemByPosition((self.targetPosition[0]+offset[0],self.targetPosition[1]+offset[1],self.targetPosition[2]+offset[2]))
                if not items or not items[0].type == "Painter":
                    continue

                foundOffset = (offset,items[0])
            if foundOffset:
                item = foundOffset[1]
                if character.getDistance(item.getPosition()) > 0:
                    quest = src.quests.questMap["GoToPosition"](targetPosition=item.getPosition(),reason="get to the painter")
                    return ([quest],None)

                if not item.paintMode == "walkingSpace":
                    return (None,(["c","m","w","enter"],"to configure the painter to walking space"))
                if not (item.offset == (0,0,0)):
                    return (None,(["c","d","."] + ["enter"],"to remove the offset from the painter"))
                return (None,("jk","draw the walkingspace"))

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

src.quests.addType(DrawWalkingSpace)

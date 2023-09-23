import src

class DeleteMarking(src.quests.MetaQuestSequence):
    type = "DeleteMarking"

    def __init__(self, description="delete marking", creator=None, targetPosition=None, targetPositionBig=None,tryHard=False,reason=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.targetPosition = targetPosition
        self.targetPositionBig = targetPositionBig
        self.tryHard = tryHard
        self.painterPos = None
        self.reason = reason

        self.metaDescription = description

    def triggerCompletionCheck(self,character=None):
        if not character:
            return

        terrain = character.getTerrain()

        checkRoom = terrain.getRoomByPosition(self.targetPositionBig)[0]
        if not checkRoom.getPaintedByPosition(self.targetPosition):
            self.postHandler()
            return True

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
            rooms = character.getTerrain().getRoomByPosition(self.targetPositionBig)
            if not rooms:
                if not dryRun:
                    self.fail("target room missing")
                return (None,None)
            room = rooms[0]

            if not character.getBigPosition() == self.targetPositionBig:
                quest = src.quests.questMap["GoToTile"](targetPosition=self.targetPositionBig,reason="get near the target tile")
                return ([quest], None)

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

                painterOffset = None
                for checkOffset in offsets:
                    if item.getPosition(offset=checkOffset) == self.targetPosition:
                        painterOffset = checkOffset
                    
                if painterOffset == (0,0,0):
                    if not (painterOffset == item.offset):
                        return (None,(["c","d",".","enter"],"to configure painter direction"))
                if painterOffset == (0,1,0):
                    if not (painterOffset == item.offset):
                        return (None,(["c","d","s","enter"],"to configure painter direction"))
                if painterOffset == (0,-1,0):
                    if not (painterOffset == item.offset):
                        return (None,(["c","d","w","enter"],"to configure painter direction"))
                if painterOffset == (1,0,0):
                    if not (painterOffset == item.offset):
                        return (None,(["c","d","d","enter"],"to configure painter direction"))
                if painterOffset == (-1,0,0):
                    if not (painterOffset == item.offset):
                        return (None,(["c","d","a","enter"],"to configure painter direction"))

                if not item.paintMode == "delete":
                    return (None,(["c","m","d","enter"],"to configure the painter to input stockpile"))

                return (None,("jk","delete marking"))

            if not self.painterPos:
                painter = None
                painterIndex = -1
                if character.inventory:
                    if character.inventory[-1].type == "Painter":
                        painter = character.inventory[-1]

                if not painter:
                    counter = 0
                    for item in character.inventory:
                        if item.type == "Painter":
                            painter = item
                            break
                        counter += 1
                    if painter:
                        painterIndex = counter

                if not painter:
                    quest = src.quests.questMap["FetchItems"](toCollect="Painter",amount=1,reason="be able to delete marking")
                    return ([quest],None)

            if not character.getBigPosition() == self.targetPositionBig:
                quest = src.quests.questMap["GoToTile"](targetPosition=self.targetPositionBig,reason="get nearby to the marking to delete")
                return ([quest],None)

            if character.getDistance(self.targetPosition) > 1:
                quest = src.quests.questMap["GoToPosition"](targetPosition=self.targetPosition,reason="get to the marking to delete",ignoreEndBlocked=True)
                return ([quest],None)

            if painterIndex == -1:
                return (None,("l","drop the Painter"))
            else:
                return (None,("il"+"s"*painterIndex+"j","drop the Painter"))

        return (None,None)

    def handleDeletedMarking(self,extraInfo):
        if not self.active:
            return
        if self.completed:
            1/0

        self.triggerCompletionCheck(self.character)

    def assignToCharacter(self, character):
        if self.character:
            return
        
        self.startWatching(character,self.handleDeletedMarking, "deleted marking")

        return super().assignToCharacter(character)

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

src.quests.addType(DeleteMarking)

import src


class DrawWalkingSpace(src.quests.MetaQuestSequence):
    '''
    quest to draw walkingspaces
    '''
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
        '''
        check for quest completion and end quest
        '''

        # abort on weird state
        if not character:
            return False

        # end quest if thw walkingspace is drawn
        room = character.getTerrain().getRoomByPosition(self.targetPositionBig)[0]
        if self.targetPosition in room.walkingSpace:
            self.postHandler()
            return True

        # continue working otherwise
        return False

    def generateTextDescription(self):
        '''
        generate a text description
        '''
        reason = ""
        if self.reason:
            reason = f", to {self.reason}"
        text = f"""
draw a walkingspace on position {self.targetPosition} on tile {self.targetPositionBig}{reason}.

"""

        text += """
Walkingspaces are drawn using a Painter (xw).
Examine the Painter for more details.
"""

        if self.tryHard:
            text += """
Try as hard as you can to achieve this.
"""

        return text

    def getNextStep(self,character=None,ignoreCommands=False, dryRun=True):
        '''
        generate the next step to solve the quest
        '''

        # do nothing if there is no subquest
        if self.subQuests:
            return (None,None)

        # get the room
        rooms = character.getTerrain().getRoomByPosition(self.targetPositionBig)
        if not rooms:
            if dryRun:
                self.fail("target room missing")
            return (None,None)
        room = rooms[0]

        # do an extra completion check
        for pos in room.walkingSpace:
            if pos == self.targetPosition:
                if not dryRun:
                    self.postHandler()
                return (None,None)

        # search for a painter near the target
        offsets = ((0,0,0),(0,1,0),(1,0,0),(0,-1,0),(-1,0,0))
        foundOffset = None
        for offset in offsets:
            items = room.getItemByPosition((self.targetPosition[0]+offset[0],self.targetPosition[1]+offset[1],self.targetPosition[2]+offset[2]))
            if not items or items[0].type != "Painter":
                continue

            foundOffset = (offset,items[0])

        # use the painter to draw
        if foundOffset:
            item = foundOffset[1]
            if character.getDistance(item.getPosition()) > 0:
                quest = src.quests.questMap["GoToPosition"](targetPosition=item.getPosition(),reason="get to the painter")
                return ([quest],None)

            if item.paintMode != "walkingSpace":
                return (None,(["c","m","w","enter"],"configure the painter to walking space"))
            if item.offset != (0, 0, 0):
                return (None,(["c", "d", ".", "enter"],"remove the offset from the painter"))
            return (None,("jk","draw the walkingspace"))

        # ensure player has a painter
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
            quest = src.quests.questMap["CleanSpace"](targetPosition=self.targetPosition,reason="unclutter the drawing spot",targetPositionBig=self.targetPositionBig,pickupBolted=True)
            return ([quest],None)

        # drop the painter next to the target
        return (None,("l","drop the Painter"))

    def handleDrewMarking(self,extraInfo):
        if not self.active:
            return
        if self.completed:
            1/0

        self.triggerCompletionCheck(self.character)

    def assignToCharacter(self, character):
        if self.character:
            return None

        self.startWatching(character,self.handleDrewMarking, "drew marking")

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


    def handleQuestFailure(self,extraParam):
        self.fail(reason=extraParam["reason"])
        super().handleQuestFailure(extraParam)

src.quests.addType(DrawWalkingSpace)

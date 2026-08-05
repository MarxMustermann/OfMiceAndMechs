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

    def triggerCompletionCheck(self,character=None,dryRun=True):
        '''
        check for quest completion and end quest
        '''

        # abort on weird state
        if not character:
            return False

        # end quest if thw walkingspace is drawn
        room = character.getTerrain().getRoomByPosition(self.targetPositionBig)[0]
        if self.targetPosition in room.walkingSpace:
            if not dryRun:
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

        # handle weird edge case
        if self.subQuests:
            return (None,None)

        # handle configuration submenu
        if "advancedConfigure" in character.interactionState:
            if not character.inventory or character.inventory[-1].type != "Painter":
                return (None,(".","clear interaction state"))
            return (None,("i","activate Painter"))


        # handle menus
        submenue = character.macroState.get("submenue")
        if submenue:

            # select what to configure
            if submenue.tag == "PainterActivitySelection":
                item = submenue.extraInfo["item"]
                if item.paintMode != "walkingSpace":
                    return (None,(["m","w","enter"],"configure the painter to draw walking space"))

            # set painting mode
            if submenue.tag == "paintModeSelection":
                if submenue.text == "":
                    return (None,(["w","enter"],"configure the painter to draw walking space"))
                elif submenue.text == "w":
                    return (None,(["enter"],"configure the painter to draw walking space"))
                else:
                    return (None,(["backspace"],"delete input"))

            # close menu
            return (None,(["esc"],"close menu"))

        # set up helper variables
        rooms = character.getTerrain().getRoomByPosition(self.targetPositionBig)
        if not rooms:
            return self._solver_trigger_fail(dryRun,"target room missing")
        room = rooms[0]

        # end quest, if completed
        if self.targetPosition in room.walkingSpace:
            return self._solver_trigger_success(dryRun)

        # ensure a painter is available
        if not character.inventory or character.inventory[-1].type != "Painter":
            quest = src.quests.questMap["FetchItems"](toCollect="Painter",amount=1)
            return ([quest],None)

        # get the painter object
        item = character.inventory[-1]

        # go near the drawing spot
        if self.targetPositionBig != character.getBigPosition():
            quest = src.quests.questMap["GoToTile"](targetPosition=self.targetPositionBig,reason="go to the tile the walking space should be drawn in")
            return ([quest],None)
        if character.getDistance(self.targetPosition) > 0:
            quest = src.quests.questMap["GoToPosition"](targetPosition=self.targetPosition,reason="get to the drawing spot")
            return ([quest],None)

        # check what direction to paint in
        offsets = ((0,0,0),(0,1,0),(1,0,0),(0,-1,0),(-1,0,0))
        foundOffset = None
        for offset in offsets:
            if character.getPosition(offset=offset) == self.targetPosition:
                foundOffset = offset

        # configure the Painter
        if item.paintMode != "walkingSpace":
            return (None,(["C","i","m","w","enter"],"configure the painter to walking space"))
        if item.offset != (0, 0, 0):
            return (None,(["C", "i", "d", ".", "enter"],"remove the offset from the painter"))

        # draw the marker
        return (None,("Ji","draw the walking space"))

    def handleDrewMarking(self,extraInfo):
        if not self.active:
            return
        if self.completed:
            1/0

        self.triggerCompletionCheck(self.character,dryRun=False)

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

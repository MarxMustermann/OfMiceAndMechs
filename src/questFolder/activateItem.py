import src

class ActivateItem(src.quests.MetaQuestSequence):
    '''
    story quest pretending to try to contact a higher command
    '''
    type = "ActivateItem"
    def __init__(self, description="activate item", creator=None, lifetime=None, targetPosition=None, targetPositionBig=None, reason=None, activateFromTop=False):
        questList = []
        super().__init__(questList, creator=creator,lifetime=lifetime)
        self.metaDescription = description
        self.reason = reason
        self.targetPosition = targetPosition
        self.targetPositionBig = targetPositionBig
        self.activateFromTop = activateFromTop

    def getNextStep(self,character=None,ignoreCommands=False, dryRun = True):
        '''
        generate the next step toward solving the quest
        '''

        if self.subQuests:
            return (None,None)

        if not character:
            return (None,None)

        # enter rooms properly
        if not character.container.isRoom:
            if character.xPosition%15 == 0:
                return (None,("d","enter room"))
            if character.xPosition%15 == 14:
                return (None,("a","enter room"))
            if character.yPosition%15 == 0:
                return (None,("s","enter room"))
            if character.yPosition%15 == 14:
                return (None,("w","enter room"))

        # activate correct item when marked
        action = self.generate_confirm_interaction_command(allowedItems=("MemorialPlate",))
        if action:
            return action

        if not character.getBigPosition() == self.targetPositionBig:
            quest = src.quests.questMap["GoToTile"](targetPosition=self.targetPositionBig,reason="reach the item",description="go to room with the item")
            return ([quest],None)

        # handle from top activation
        if self.activateFromTop:
            if character.getDistance(self.targetPosition) > 0:
                quest = src.quests.questMap["GoToPosition"](targetPosition=self.targetPosition,reason="to be able to use the item",description="go to item",clearPath=True)
                return ([quest],None)

            return (None,("j","activate information plate"))

        # handle menus
        submenue = character.macroState["submenue"]
        if submenue and not ignoreCommands:
            if submenue.tag not in ("advancedInteractionSelection",):
                return (None,(["esc"],"close menu"))

        # go to the tile the item is on
        if self.targetPositionBig and character.getBigPosition() != self.targetPositionBig:
            quest = src.quests.questMap["GoToTile"](targetPosition=self.targetPositionBig,reason="get to the tile the item is on")
            return ([quest],None)

        # go to the item
        pos = character.getPosition()
        if self.targetPosition not in (pos,(pos[0],pos[1]+1,pos[2]),(pos[0]-1,pos[1],pos[2]),(pos[0]+1,pos[1],pos[2]),(pos[0],pos[1]-1,pos[2])):
            quest = src.quests.questMap["GoToPosition"](targetPosition=self.targetPosition,ignoreEndBlocked=True,reason="get near the item")
            return ([quest],None)

        # activate the item
        interactionCommand = "J"
        if submenue:
            if submenue.tag == "advancedInteractionSelection":
                interactionCommand = ""
            else:
                return (None,(["esc"],"close menu"))
        if (pos[0],pos[1],pos[2]) == self.targetPosition:
            return (None,("j","activate item"))
        if (pos[0]-1,pos[1],pos[2]) == self.targetPosition:
            return (None,(interactionCommand+"a","activate item"))
        if (pos[0]+1,pos[1],pos[2]) == self.targetPosition:
            return (None,(interactionCommand+"d","activate item"))
        if (pos[0],pos[1]-1,pos[2]) == self.targetPosition:
            return (None,(interactionCommand+"w","activate item"))
        if (pos[0],pos[1]+1,pos[2]) == self.targetPosition:
            return (None,(interactionCommand+"s","activate item"))
        return (None,(".","stand around confused"))

    def generateTextDescription(self):
        return [f"""
Activate item on Position {self.targetPosition} in tile {self.targetPositionBig}.
"""]

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character, self.handleRawApplied, "raw applied")
        super().assignToCharacter(character)

    def handleRawApplied(self,extraInfo):
        if self.completed:
            1/0
        if not self.active:
            return

        item = extraInfo["item"]

        if item.getPosition() != self.targetPosition:
            return
        if item.getBigPosition() != self.targetPositionBig:
            return

        self.postHandler()

    def triggerCompletionCheck(self,character=None, dryRun=True):
        if not character:
            return False
        return False

    def getQuestMarkersSmall(self,character,renderForTile=False):
        '''
        return the quest markers for the normal map
        '''
        if isinstance(character.container,src.rooms.Room):
            if renderForTile:
                return []
        else:
            if not renderForTile:
                return []

        result = super().getQuestMarkersSmall(character,renderForTile=renderForTile)
        if not renderForTile:
            if isinstance(character.container,src.rooms.Room) and character.getBigPosition() == self.targetPositionBig:
                result.append((self.targetPosition,"target"))
        return result

src.quests.addType(ActivateItem)

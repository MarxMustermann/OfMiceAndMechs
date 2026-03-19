import src

class ReadMemorialPlate(src.quests.MetaQuestSequence):
    '''
    story quest pretending to try to contact a higher command
    '''
    type = "ReadMemorialPlate"
    def __init__(self, description="read information plate", creator=None, lifetime=None, targetPosition=None, targetPositionBig=None, reason=None):
        questList = []
        super().__init__(questList, creator=creator,lifetime=lifetime)
        self.metaDescription = description
        self.reason = reason
        self.targetPosition = targetPosition
        self.targetPositionBig = targetPositionBig

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

        # handle menus
        submenue = character.macroState.get("submenue")
        if submenue and not ignoreCommands:
            return (None,(["esc"],"close the menu"))

        # activate correct item when marked
        action = self.generate_confirm_interaction_command(allowedItems=("MemorialPlate",))
        if action:
            return action

        if not character.getBigPosition() == self.targetPositionBig:
            quest = src.quests.questMap["GoToTile"](targetPosition=self.targetPositionBig,reason="reach the information plate",description="go to room with information plate")
            return ([quest],None)

        if not character.container.isRoom:
            return (None,(".","stand around confused"))

        if character.getDistance(self.targetPosition) > 0:
            quest = src.quests.questMap["GoToPosition"](targetPosition=self.targetPosition,reason="to be able to use the MemorialPlate",description="go to information plate")
            return ([quest],None)

        return (None,("j","activate information plate"))

    def generateTextDescription(self):
        return [f"""
Read the information from the MemorialPlate on Position {self.targetPosition} in tile {self.targetPositionBig}.

Activate the MemorialPlate to read it.
"""]

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character, self.handleReadMemorialPlate, "read memorial plate")
        super().assignToCharacter(character)

    def handleReadMemorialPlate(self,extraInfo):
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
            if isinstance(character.container,src.rooms.Room):
                for item in character.container.itemsOnFloor:
                    if not item.type == "Communicator":
                        continue
                    if not item.bolted:
                        continue
                    result.append((item.getPosition(),"target"))
        return result

src.quests.addType(ReadMemorialPlate)

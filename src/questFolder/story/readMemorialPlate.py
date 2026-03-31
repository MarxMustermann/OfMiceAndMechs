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

        quest = src.quests.questMap["ActivateItem"](targetPosition=self.targetPosition,targetPositionBig=self.targetPositionBig,reason="read the information plate",targetItemType="MemorialPlate")
        return ([quest],None)

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
                    if not item.container:
                        continue
                    if self.targetPositionBig and item.getBigPosition() != self.targetPositionBig:
                        break
                    if self.targetPosition and item.getPosition() != self.targetPosition:
                        continue
                    if not item.type == "MemorialPlate":
                        continue
                    if not item.bolted:
                        continue
                    result.append((item.getPosition(),"target"))
        return result

src.quests.addType(ReadMemorialPlate)

import src

class Meditate(src.quests.MetaQuestSequence):
    '''
    story quest pretending to try to contact a higher command
    '''
    type = "Meditate"
    def __init__(self, description="recover health", creator=None, lifetime=None, targetPosition=None, targetPositionBig=None, reason=None):
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

        quest = src.quests.questMap["ActivateItem"](targetPosition=self.targetPosition,targetPositionBig=self.targetPositionBig,reason="mediate",activateFromTop=True,targetItemType="MeditationPlate")
        return ([quest],None)

    def generateTextDescription(self):
        result = [f"""
Meditate on the MeditationPlate on {self.targetPosition} in room {self.targetPositionBig}
This will recover you health up to 50 HP.

Activate the MeditationPlate to meditate
"""]
        if self.subQuests:
            result.append("""
This quest has subquests. More information is shown there.
Press the d key to show the subquest description.
Press the a key to return to this quest again.
""")
        return result

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character, self.handleMeditated, "meditated")
        super().assignToCharacter(character)

    def handleMeditated(self,extraInfo):
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
        if character.health > 50:
            if not dryRun:
                self.postHandler()
            return True
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
                    if not item.type == "MeditationPlate":
                        continue
                    if not item.bolted:
                        continue
                    result.append((item.getPosition(),"target"))
        return result

src.quests.addType(Meditate)

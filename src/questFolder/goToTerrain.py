import src


class GoToTerrain(src.quests.MetaQuestSequenceV2):
    type = "GoToTerrain"

    def __init__(self, description="go to terrain", creator=None, targetTerrain=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.targetTerrain = targetTerrain
        self.metaDescription = description + " " + str(self.targetTerrain)

    def triggerCompletionCheck(self,character=None):
        if character is None:
            return None
        if len(self.targetTerrain) < 3:
            self.targetTerrain = (self.targetTerrain[0],self.targetTerrain[1],0)
        if self.targetTerrain == character.getTerrainPosition():
            self.postHandler()
            return True
        return False

    def getNextStep(self,character,ignoreCommands=False, dryRun = True):
        if self.subQuests:
            return (None,None)

        if character.getTerrain().yPosition > self.targetTerrain[1]:
            if character.getBigPosition() not in ((7,1,0),(7,0,0)):
                quest = src.quests.questMap["GoToTile"](targetPosition=(7,1,0))
                return ([quest],None)
            if character.getPosition() != (7 * 15 + 7, 15 * 1 + 1, 0) and character.getBigPosition() not in ((7,0,0),):
                quest = src.quests.questMap["GoToPosition"](targetPosition=(7,1,0))
                return ([quest],None)
            return (None,"w")

        if character.getTerrain().yPosition < self.targetTerrain[1]:
            if character.getBigPosition() not in ((7,13,0),(7,14,0)):
                quest = src.quests.questMap["GoToTile"](targetPosition=(7,13,0))
                return ([quest],None)
            if character.getPosition() != (7 * 15 + 7, 15 * 13 + 13, 0) and character.getBigPosition() not in ((7,14,0),):
                quest = src.quests.questMap["GoToPosition"](targetPosition=(7,13,0))
                return ([quest],None)
            return (None,"s")

        if character.getTerrain().xPosition > self.targetTerrain[0]:
            if character.getBigPosition() not in ((1,7,0),(0,7,0)):
                quest = src.quests.questMap["GoToTile"](targetPosition=(1,7,0))
                return ([quest],None)
            if character.getPosition() != (1 * 15 + 1, 15 * 7 + 7, 0) and character.getBigPosition() not in ((0,7,0),):
                quest = src.quests.questMap["GoToPosition"](targetPosition=(1,7,0))
                return ([quest],None)
            return (None,"a")

        if character.getTerrain().xPosition < self.targetTerrain[0]:
            if character.getBigPosition() not in ((13,7,0),(14,7,0)):
                quest = src.quests.questMap["GoToTile"](targetPosition=(13,7,0))
                return ([quest],None)
            if character.getPosition() != (13 * 15 + 13, 15 * 7 + 7, 0) and character.getBigPosition() not in ((14,7,0),):
                quest = src.quests.questMap["GoToPosition"](targetPosition=(13,7,0))
                return ([quest],None)
            return (None,"d")
        return (None,None)

        quest = src.quests.questMap["TeleportToTerrain"](targetPosition=self.targetTerrain)
        return ([quest],None)

    def handleChangedTerrain(self,extraInfo):
        self.triggerCompletionCheck(extraInfo["character"])

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.handleChangedTerrain, "changedTerrain")
        super().assignToCharacter(character)

src.quests.addType(GoToTerrain)

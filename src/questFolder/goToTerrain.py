import src

class GoToTerrain(src.quests.MetaQuestSequence):
    type = "GoToTerrain"

    def __init__(self, description="go to terrain", creator=None, targetTerrain=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        self.targetTerrain = targetTerrain

    def generateTextDescription(self):
        return """
obtain the special item from the base on %s
"""%(self.targetTerrain,)

    def triggerCompletionCheck(self,character=None):
        if character == None:
            return
        if len(self.targetTerrain) < 3:
            self.targetTerrain = (self.targetTerrain[0],self.targetTerrain[1],0)
        if self.targetTerrain == character.getTerrainPosition():
            self.postHandler()
            return True
        return False

    def generateSubquests(self,character=None):
        if character == None:
            return
        self.addQuest(src.quests.questMap["TeleportToTerrain"](targetPosition=self.targetTerrain))
        return

    def solver(self, character):
        if self.triggerCompletionCheck(character):
            return

        if not self.subQuests:
            self.generateSubquests(character)
            if self.subQuests:
                return
        command = self.getSolvingCommandString(character,dryRun=False)
        if command:
            character.runCommandString(command)
            return
        super().solver(character)

    def handleChangedTerrain(self,extraInfo):
        self.triggerCompletionCheck(extraInfo["character"])
            
    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.handleChangedTerrain, "changedTerrain")
        super().assignToCharacter(character)

src.quests.addType(GoToTerrain)

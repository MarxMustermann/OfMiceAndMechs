import src

class ObtainSpecialItem(src.quests.MetaQuestSequence):
    type = "ObtainSpecialItem"

    def __init__(self, description="obtain special item", creator=None, targetTerrain=None, itemId=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        self.targetTerrain = targetTerrain
        self.itemId = itemId

    def generateTextDescription(self):
        return """
obtain the special item from the base on %s
"""%(self.targetTerrain,)

    def triggerCompletionCheck(self):
        return False

    def generateSubquests(self,character=None):
        if character == None:
            return

        self.addQuest(src.quests.questMap["GoToTerrain"](targetTerrain=self.targetTerrain))
        return

    def solver(self, character):
        if not self.subQuests:
            self.generateSubquests(character)
            if self.subQuests:
                return
        command = self.getSolvingCommandString(character,dryRun=False)
        if command:
            character.runCommandString(command)
            return
        super().solver(character)

src.quests.addType(ObtainSpecialItem)

import src

class SecureTiles(src.quests.MetaQuestSequence):
    type = "SecureTiles"

    def __init__(self, description="secure tiles", toSecure=None):
        super().__init__()
        self.metaDescription = description
        self.toSecure = toSecure

    def generateTextDescription(self):
        text = """
Secure a group of tiles.

Secure the following tiles:

"""
        for tile in self.toSecure:
            text += str(tile)+"\n"
        return text

    def triggerCompletionCheck(self,character=None):
        if self.toSecure:
            return False

        self.postHandler()
        return True

    def solver(self,character):
        self.triggerCompletionCheck(character)
        if not self.subQuests:
            targetPosition = self.toSecure.pop()
            quest = src.quests.questMap["SecureTile"](toSecure=targetPosition,endWhenCleared=True)
            quest.assignToCharacter(character)
            quest.activate()
            self.addQuest(quest)
            return
        super().solver(character)

src.quests.addType(SecureTiles)

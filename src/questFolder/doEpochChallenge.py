import src

class DoEpochChallenge(src.quests.MetaQuestSequence):
    type = "DoEpochChallenge"

    def __init__(self, description="do epoch challenge", creator=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description

    def generateTextDescription(self):
        text = """
Complete a task for the epoch artwork.

Use the epoch artwork to fetch a task and complete it.
"""
        return text

    """
    never complete
    """
    def triggerCompletionCheck(self, character=None):
        return

    def getSolvingCommandString(self,character,dryRun=True):
        pos = character.getBigPosition()
        if pos == (7,7,0):
            if character.getPosition() == (6,7,0):
                return list("Jw.")+["enter"]*2
        return super().getSolvingCommandString(character)

    def generateSubquests(self,character): 
        
        while self.subQuests:
            if not self.subQuests[-1].completed:
                break
            self.subQuests.pop()

        if self.subQuests:
            return

        pos = character.getBigPosition()

        if pos == (7,7,0):
            if not character.getPosition() == (6,7,0):
                quest = src.quests.questMap["GoToPosition"](targetPosition=(6,7,0), description="go to epoch artwork")
                quest.activate()
                self.addQuest(quest)
                return
            return

        quest = src.quests.questMap["GoHome"](description="go to command centre")
        self.addQuest(quest)
        quest.assignToCharacter(character)
        quest.activate()
        return

    def solver(self,character):
        if self.triggerCompletionCheck(character):
            return
        if not self.subQuests:
            self.generateSubquests(character)

            if self.subQuests:
                return

        """
        command = self.getSolvingCommandString(character)
        if command:
            character.runCommandString(command)
            return
        """

        super().solver(character)

src.quests.addType(DoEpochChallenge)

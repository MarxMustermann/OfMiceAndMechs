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
            epochArtwork = character.container.getItemsByType("EpochArtwork")[0]
            command = None
            if character.getPosition(offset=(1,0,0)) == epochArtwork.getPosition():
                command = "d"
            if character.getPosition(offset=(-1,0,0)) == epochArtwork.getPosition():
                command = "a"
            if character.getPosition(offset=(0,1,0)) == epochArtwork.getPosition():
                command = "s"
            if character.getPosition(offset=(0,-1,0)) == epochArtwork.getPosition():
                command = "w"

            if command:
                return list("J"+command)+["enter"]*2
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
            epochArtwork = character.container.getItemsByType("EpochArtwork")[0]
            if character.getDistance(epochArtwork.getPosition()) > 1:
                quest = src.quests.questMap["GoToPosition"](targetPosition=epochArtwork.getPosition(), description="go to epoch artwork",ignoreEndBlocked=True)
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

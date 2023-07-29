import src

class GetEpochReward(src.quests.MetaQuestSequence):
    type = "GetEpochReward"

    def __init__(self, description="get epoch reward", creator=None,rewardType=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        self.rewardType = rewardType

    def generateTextDescription(self):
        out = []
        text = """
You accumulated some glass tears.

Now claim the actual reward.

"""
        out.append(text)
        return out

    def getNextStep(self,character=None,ignoreCommands=False):
        
        while self.subQuests:
            if not self.subQuests[-1].completed:
                break
            self.subQuests.pop()

        if self.subQuests:
            return (None,None)

        if character.macroState["submenue"] and isinstance(character.macroState["submenue"],src.interaction.SelectionMenu) and not ignoreCommands:
            submenue = character.macroState["submenue"]
            if submenue.tag == "rewardSelection":
                rewardIndex = 0
                if self.rewardType == "room building":
                    rewardIndex = 8
                if self.rewardType == "scavenging":
                    rewardIndex = 10
                if self.rewardType == "machine operating":
                    rewardIndex = 3
                if self.rewardType == "resource fetching":
                    rewardIndex = 4
                if self.rewardType == "resource gathering":
                    rewardIndex = 2

                offset = rewardIndex-submenue.selectionIndex
                if offset > 0:
                    return (None,("s"*offset+"j","to get your reward"))
                else:
                    return (None,("w"*(-offset)+"j","to get your reward"))
            else:
                return (None,("sj","to get your reward"))

        if character.macroState["submenue"] and not ignoreCommands:
            return (None,(["esc"],"to exit submenu"))

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
                return (None,("J"+command,"to activate the epoch artwork"))

            quest = src.quests.questMap["GoToPosition"](targetPosition=epochArtwork.getPosition(), description="go to epoch artwork",ignoreEndBlocked=True)
            return ([quest],None)

        quest = src.quests.questMap["GoHome"](description="go to command centre")
        return ([quest],None)

    def handleGotEpochReward(self, extraInfo):
        if self.completed:
            1/0

        self.postHandler()
        return

    def assignToCharacter(self, character):
        if self.character:
            return
        
        self.startWatching(character,self.handleGotEpochReward, "got epoch reward")

        return super().assignToCharacter(character)

    """
    never complete
    """
    def triggerCompletionCheck(self,character=None):
        return False

    def getSolvingCommandString(self, character, dryRun=True):
        nextStep = self.getNextStep(character)
        if nextStep == (None,None):
            return super().getSolvingCommandString(character)
        return self.getNextStep(character)[1]

    def generateSubquests(self, character=None):
        (nextQuests,nextCommand) = self.getNextStep(character,ignoreCommands=True)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
            return

    def solver(self, character):
        if self.triggerCompletionCheck(character):
            return

        (nextQuests,nextCommand) = self.getNextStep(character)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
            return

        if nextCommand:
            character.runCommandString(nextCommand[0])
            return
        super().solver(character)


src.quests.addType(GetEpochReward)

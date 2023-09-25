import src

class DoEpochChallenge(src.quests.MetaQuestSequence):
    type = "DoEpochChallenge"

    def __init__(self, description="do epoch challenge", creator=None,reason=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        self.reason = reason

    def generateTextDescription(self):
        out = []
        reason = ""
        if self.reason:
            reason = f", to {self.reason}"
        text = f"""
Complete a task for the epoch artwork{reason}.

Use the epoch artwork to fetch a task and complete it.

"""
        out.append(text)
        if not self.subQuests:
            out.append((src.interaction.urwid.AttrSpec("#f00", "black"),"""
Press r to generate the subquests that will help you do that.
"""))
        else:
            out.append((src.interaction.urwid.AttrSpec("#0a0", "black"),"""
Press d to the show the description for the subQuest.
"""))

        return out

    def getNextStep(self,character=None,ignoreCommands=False):

        while self.subQuests:
            if not self.subQuests[-1].completed:
                break
            self.subQuests.pop()

        if self.subQuests:
            return (None,None)

        if character.macroState["submenue"] and isinstance(character.macroState["submenue"],src.interaction.SelectionMenu) and not ignoreCommands:
            return (None,(["enter"],"to select option"))

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
                return (None,(list("J"+command)+["enter"]*2,"get a challenge from the epoch artwork"))

            quest = src.quests.questMap["GoToPosition"](targetPosition=epochArtwork.getPosition(), description="go to epoch artwork",ignoreEndBlocked=True, reason="get in reach of the EpochArtwork")
            return ([quest],None)

        quest = src.quests.questMap["GoHome"](description="go to command centre")
        return ([quest],None)

    """
    never complete
    """
    def triggerCompletionCheck(self,character=None):
        return

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


src.quests.addType(DoEpochChallenge)

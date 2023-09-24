import src

class GetEpochEvaluation(src.quests.MetaQuestSequence):
    type = "GetEpochEvaluation"

    def __init__(self, description="get epoch evaluation", creator=None,reason=None):
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
Get your epoch evaluation{reason}.

You completed a part of the epoch challenge.
You will get a reward for that.

Claim the glass tears you have earned.
You can spend them later to get an actual reward.

"""
        out.append(text)
        return out

    def gotEpochEvaluation(self):
        self.triggerCompletionCheck(self.character)

    def assignToCharacter(self, character):
        if self.character:
            return
        
        self.startWatching(character,self.gotEpochEvaluation, "got epoch evaluation")

        return super().assignToCharacter(character)

    def getNextStep(self,character=None,ignoreCommands=False):
        
        while self.subQuests:
            if not self.subQuests[-1].completed:
                break
            self.subQuests.pop()

        if self.subQuests:
            return (None,None)

        if not isinstance(character.container,src.rooms.Room):
            if character.yPosition%15 == 14:
                return (None,("w","enter tile"))
            if character.yPosition%15 == 0:
                return (None,("s","enter tile"))
            if character.xPosition%15 == 14:
                return (None,("a","enter tile"))
            if character.xPosition%15 == 0:
                return (None,("d","enter tile"))
                    
        if character.macroState["submenue"] and isinstance(character.macroState["submenue"],src.interaction.SelectionMenu) and not ignoreCommands:
            submenue = character.macroState["submenue"]
            counter = 3
            command = ""
            if submenue.selectionIndex > counter:
                command += "w"*(submenue.selectionIndex-counter)
            if submenue.selectionIndex < counter:
                command += "s"*(counter-submenue.selectionIndex)
            command += "j"
            return (None,(command,"to collect the glass tears"))

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

            quest = src.quests.questMap["GoToPosition"](targetPosition=epochArtwork.getPosition(), description="go to epoch artwork",ignoreEndBlocked=True,reason="go to epoch artwork")
            return ([quest],None)

        quest = src.quests.questMap["GoHome"](description="go to command centre",reason="go to the command centre")
        return ([quest],None)

    """
    never complete
    """
    def triggerCompletionCheck(self,character=None):
        if not character:
            return False

        room = character.getTerrain().getRoomByPosition((7,7,0))[0]
        epochArtwork = room.getItemsByType("EpochArtwork")[0]
        if not epochArtwork.recalculateGlasstears(character,dryRun=True):
            self.postHandler()
            return True
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


src.quests.addType(GetEpochEvaluation)

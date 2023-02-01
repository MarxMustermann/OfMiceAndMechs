import src

class OperateMachine(src.quests.MetaQuestSequence):
    type = "OperateMachine"

    def __init__(self, description="operate machine", creator=None, targetPosition=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        self.targetPosition = targetPosition

    def handleOperatedMachine(self, extraInfo):
        if self.completed:
            1/0

        if extraInfo["machine"].getPosition() == self.targetPosition:
            self.postHandler()
            return

    def assignToCharacter(self, character):
        if self.character:
            return
        
        self.startWatching(character,self.handleOperatedMachine, "operated machine")

        return super().assignToCharacter(character)

    def generateTextDescription(self):
        return """
operate the machine on %s
"""%(self.targetPosition,)

    def triggerCompletionCheck(self):
        return False

    def generateSubquests(self,character=None):
        if character == None:
            return

        pos = character.getPosition()
        if not self.targetPosition in (pos,(pos[0],pos[1],pos[2]),(pos[0]-1,pos[1],pos[2]),(pos[0]+1,pos[1],pos[2]),(pos[0],pos[1]-1,pos[2])):
            self.addQuest(src.quests.questMap["GoToPosition"](targetPosition=self.targetPosition,ignoreEndBlocked=True))
            return

    def getSolvingCommandString(self, character, dryRun=True):
        pos = character.getPosition()
        if (pos[0],pos[1],pos[2]) == self.targetPosition:
            return "j"
        if (pos[0]-1,pos[1],pos[2]) == self.targetPosition:
            return "Ja"
        if (pos[0]+1,pos[1],pos[2]) == self.targetPosition:
            return "Jd"
        if (pos[0],pos[1]-1,pos[2]) == self.targetPosition:
            return "Jw"
        if (pos[0],pos[1]+1,pos[2]) == self.targetPosition:
            return "Js"
        super().getSolvingCommandString(character,dryRun=dryRun)

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

src.quests.addType(OperateMachine)

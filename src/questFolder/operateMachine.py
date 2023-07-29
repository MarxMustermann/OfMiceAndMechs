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

    def triggerCompletionCheck(self,character=None):
        if not character:
            return False

        if not character.container.isRoom:
            self.fail()
            return True

        items = character.container.getItemByPosition(self.targetPosition)
        if not items or not items[0].type in ("Machine","ScrapCompactor","MaggotFermenter","BioPress","GooProducer"):
            self.fail()
            return True

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
        self.triggerCompletionCheck(character)
        if not self.subQuests:
            self.generateSubquests(character)
            if self.subQuests:
                return
        command = self.getSolvingCommandString(character,dryRun=False)
        if command:
            character.runCommandString(command)
            return
        super().solver(character)

    def getQuestMarkersSmall(self,character,renderForTile=False):
        if isinstance(character.container,src.rooms.Room):
            if renderForTile:
                return []
        else:
            if not renderForTile:
                return []

        result = super().getQuestMarkersSmall(character,renderForTile=renderForTile)
        if renderForTile:
            result.append(((self.targetPosition[0]+self.targetPositionBig[0]*15,self.targetPosition[1]+self.targetPositionBig[1]*15),"target"))
        else:
            result.append(((self.targetPosition[0],self.targetPosition[1]),"target"))
        return result


src.quests.addType(OperateMachine)

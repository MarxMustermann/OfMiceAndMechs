import src

class OperateMachine(src.quests.MetaQuestSequence):
    type = "OperateMachine"

    def __init__(self, description="operate machine", creator=None, targetPosition=None, targetPositionBig=None,reason=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        self.targetPosition = targetPosition
        self.targetPositionBig = targetPositionBig
        self.reason = reason

    def handleOperatedMachine(self, extraInfo):
        if self.completed:
            1/0
        if not self.active:
            return

        if extraInfo["machine"].getPosition() == self.targetPosition:
            self.postHandler()
            return

    def assignToCharacter(self, character):
        if self.character:
            return
        
        self.startWatching(character,self.handleOperatedMachine, "operated machine")

        return super().assignToCharacter(character)

    def generateTextDescription(self):
        reason = ""
        if self.reason:
            reason = ", to %s"%(self.reason,)
        return """
operate the machine on %s%s.
"""%(self.targetPosition,reason,)

    def triggerCompletionCheck(self,character=None):
        if not character:
            return False

        if self.targetPositionBig and not character.getBigPosition() == self.targetPositionBig:
            return False

        if not character.container.isRoom:
            self.fail()
            return True

        items = character.container.getItemByPosition(self.targetPosition)
        if not items or not items[0].type in ("Machine","ScrapCompactor","MaggotFermenter","BioPress","GooProducer"):
            self.fail()
            return True

        return False

    def getNextStep(self,character,ignoreCommands=False):
        if self.subQuests:
            return (None,None)

        if self.targetPositionBig and not character.getBigPosition() == self.targetPositionBig:
            quest = src.quests.questMap["GoToTile"](targetPosition=self.targetPositionBig,reason="get to the tile the machine is on")
            return ([quest],None)

        pos = character.getPosition()
        if not self.targetPosition in (pos,(pos[0],pos[1]+1,pos[2]),(pos[0]-1,pos[1],pos[2]),(pos[0]+1,pos[1],pos[2]),(pos[0],pos[1]-1,pos[2])):
            quest = src.quests.questMap["GoToPosition"](targetPosition=self.targetPosition,ignoreEndBlocked=True,reason="get near the machine")
            return ([quest],None)

        if (pos[0],pos[1],pos[2]) == self.targetPosition:
            return (None,("j","activate machine"))
        if (pos[0]-1,pos[1],pos[2]) == self.targetPosition:
            return (None,("Ja","activate machine"))
        if (pos[0]+1,pos[1],pos[2]) == self.targetPosition:
            return (None,("Jd","activate machine"))
        if (pos[0],pos[1]-1,pos[2]) == self.targetPosition:
            return (None,("Jw","activate machine"))
        if (pos[0],pos[1]+1,pos[2]) == self.targetPosition:
            return (None,("Js","activate machine"))

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
        (nextQuests,nextCommand) = self.getNextStep(character)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
            return

        if nextCommand:
            character.runCommandString(nextCommand[0])
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
            if self.targetPosition and self.targetPositionBig:
                result.append(((self.targetPosition[0]+self.targetPositionBig[0]*15,self.targetPosition[1]+self.targetPositionBig[1]*15),"target"))
        else:
            if character.getBigPosition() == self.targetPositionBig:
                result.append(((self.targetPosition[0],self.targetPosition[1]),"target"))
        return result


src.quests.addType(OperateMachine)

import src

class Ascend(src.quests.MetaQuestSequence):
    type = "Ascend"

    def __init__(self, description="ascend", creator=None, reason=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        self.reason = reason

    def handleAscended(self, extraInfo):
        if self.completed:
            1/0
        if not self.active:
            return

        self.postHandler()

    def assignToCharacter(self, character):
        if self.character:
            return None

        self.startWatching(character,self.handleAscended, "ascended")

        return super().assignToCharacter(character)

    def triggerCompletionCheck(self,character=None):
        if not character:
            return False

        return False

    def getNextStep(self,character,ignoreCommands=False,dryRun=True):
        if self.subQuests:
            return (None,None)

        terrain = character.getTerrain()
        for room in terrain.rooms:
            throne = room.getItemByType("Throne",needsBolted=True)
            if throne:
                break

        if not throne:
            if not dryRun:
                self.fail("no throne")
            return (None,None)

        if character.container != room:
            quest = src.quests.questMap["GoToTile"](targetPosition=room.getPosition(),reason="get to the temple")
            return ([quest],None)

        pos = character.getPosition()
        targetPosition = throne.getPosition()
        if not targetPosition in (pos,(pos[0],pos[1]+1,pos[2]),(pos[0]-1,pos[1],pos[2]),(pos[0]+1,pos[1],pos[2]),(pos[0],pos[1]-1,pos[2])):
            quest = src.quests.questMap["GoToPosition"](targetPosition=targetPosition,ignoreEndBlocked=True,reason="get near the throne")
            return ([quest],None)

        if (pos[0],pos[1],pos[2]) == targetPosition:
            return (None,("j","activate the Throne"))
        if (pos[0]-1,pos[1],pos[2]) == targetPosition:
            return (None,("Ja","activate the Throne"))
        if (pos[0]+1,pos[1],pos[2]) == targetPosition:
            return (None,("Jd","activate the Throne"))
        if (pos[0],pos[1]-1,pos[2]) == targetPosition:
            return (None,("Jw","activate the Throne"))
        if (pos[0],pos[1]+1,pos[2]) == targetPosition:
            return (None,("Js","activate the Throne"))

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
        (nextQuests,nextCommand) = self.getNextStep(character,dryRun=False)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
            return

        if nextCommand:
            character.runCommandString(nextCommand[0])
            return
        super().solver(character)

src.quests.addType(Ascend)

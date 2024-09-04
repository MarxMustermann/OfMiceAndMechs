import src


class ActivateGlassStatue(src.quests.MetaQuestSequence):
    type = "ActivateGlassStatue"

    def __init__(self, description="activate glass statue", creator=None, targetPosition=None, targetPositionBig=None, reason=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        self.reason = reason
        self.targetPosition = targetPosition
        self.targetPositionBig = targetPositionBig

    def handleActivatedGlassStatue(self):
        if self.completed:
            1/0
        if not self.active:
            return

        self.postHandler()

    def handleStatueUsed(self, extraInfo):
        self.postHandler()

    def assignToCharacter(self, character):
        if self.character:
            return None

        self.startWatching(character,self.handleStatueUsed, "glass statue used")

        return super().assignToCharacter(character)

    def triggerCompletionCheck(self,character=None):
        if not character:
            return False

        if character.rank != 1:
            return False

        self.postHandler()

    def getNextStep(self,character,ignoreCommands=False,dryRun=True):
        if self.subQuests:
            return (None,None)

        terrain = character.getTerrain()
        for room in terrain.rooms:
            throne = room.getItemByType("Throne",needsBolted=True)
            if throne:
                break

        if character.getBigPosition() != self.targetPositionBig:
            quest = src.quests.questMap["GoToTile"](targetPosition=self.targetPositionBig,description="go to the temple",reason="to reach the GlassStatue")
            return ([quest],None)

        if character.getDistance(self.targetPosition) > 1:
            quest = src.quests.questMap["GoToPosition"](targetPosition=self.targetPosition,ignoreEndBlocked=True,description="go to the GlassStatue",reason="be able to activae the GlassStatue")
            return ([quest],None)

        pos = character.getPosition()
        direction = "."
        if (pos[0]-1,pos[1],pos[2]) == self.targetPosition:
            direction = "a"
        if (pos[0]+1,pos[1],pos[2]) == self.targetPosition:
            direction = "d"
        if (pos[0],pos[1]-1,pos[2]) == self.targetPosition:
            direction = "w"
        if (pos[0],pos[1]+1,pos[2]) == self.targetPosition:
            direction = "s"
        return (None,("J"+direction+"wj","activate the GlassStatue"))

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

    def generateTextDescription(self):
        text = ["""
The GlassStatues are connected to the heart of their god. 
Pray at the GlassStatue to be teleported to the terrain the heart is on.

Expect combat after the teleport.
"""]
        return text

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

src.quests.addType(ActivateGlassStatue)

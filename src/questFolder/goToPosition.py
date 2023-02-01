import src

class GoToPosition(src.quests.Quest):
    type = "GoToPosition"

    def __init__(self, description="go to position", creator=None,targetPosition=None,ignoreEnd=False,ignoreEndBlocked=False):
        questList = []
        super().__init__(questList, creator=creator)
        self.targetPosition = None
        self.description = description
        self.metaDescription = description
        self.hasListener = False
        self.ignoreEndBlocked = False
        if targetPosition:
            self.setParameters({"targetPosition":targetPosition})
        if ignoreEndBlocked:
            self.setParameters({"ignoreEndBlocked":ignoreEndBlocked})

        self.tuplesToStore.append("targetPosition")
        
        self.shortCode = "g"
        self.smallPath = []

    def generateTextDescription(self):
        extraText = ""
        if self.ignoreEndBlocked:
            extraText = """

The position you should go might be blocked.
So it is enough to go next to the target position to end this quest.
"""

        text = """
go to position %s in the same room you are in.

This quest ends after you do this."""%(self.targetPosition,) 
        return text

    def getQuestMarkersSmall(self,character,renderForTile=False):
        if isinstance(character.container,src.rooms.Room):
            if renderForTile:
                return []
        else:
            if not renderForTile:
                return []

        self.getSolvingCommandString(character)
        result = super().getQuestMarkersSmall(character,renderForTile=renderForTile)
        if self.smallPath:
            if isinstance(character.container,src.rooms.Room):
                pos = (character.xPosition,character.yPosition)
            else:
                pos = (character.xPosition%15,character.yPosition%15)
            for step in self.smallPath:
                pos = (pos[0]+step[0],pos[1]+step[1])
                result.append((pos,"path"))
        return result

    def wrapedTriggerCompletionCheck(self, extraInfo):
        if not self.active:
            return
        if self.completed:
            return

        self.triggerCompletionCheck(extraInfo[0])

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.wrapedTriggerCompletionCheck, "moved")

        super().assignToCharacter(character)

    def getSolvingCommandString(self, character, dryRun=True):
        if character.macroState.get("submenue"):
            return ["esc"]
        if character.xPosition%15 == 0:
            return "d"
        if character.xPosition%15 == 14:
            return "a"
        if character.yPosition%15 == 0:
            return "s"
        if character.yPosition%15 == 14:
            return "w"
        if not self.targetPosition:
            return ".12.."

        localRandom = random.Random(self.randomSeed)

        if isinstance(character.container,src.rooms.Room):
            (command,self.smallPath) = character.container.getPathCommandTile(character.getPosition(),self.targetPosition,localRandom=localRandom,ignoreEndBlocked=self.ignoreEndBlocked,character=character)
            if not command:
                (command,self.smallPath) = character.container.getPathCommandTile(character.getPosition(),self.targetPosition,localRandom=localRandom,tryHard=True,ignoreEndBlocked=self.ignoreEndBlocked,character=character)
            if not command:
                return None
            return command
        else:
            charPos = (character.xPosition%15,character.yPosition%15,character.zPosition%15)
            tilePos = (character.xPosition//15,character.yPosition//15,character.zPosition//15)

            (command,self.smallPath) = character.container.getPathCommandTile(tilePos,charPos,self.targetPosition,localRandom=localRandom,ignoreEndBlocked=self.ignoreEndBlocked,character=character)
            if not command:
                (command,self.smallPath) = character.container.getPathCommandTile(tilePos,charPos,self.targetPosition,localRandom=localRandom,tryHard=True,ignoreEndBlocked=self.ignoreEndBlocked,character=character)
            if not command:
                return None
            return command

    def triggerCompletionCheck(self, character=None):
        if not self.targetPosition:
            return False
        if not character:
            return False
        if not self.active:
            return

        if character.xPosition%15 == self.targetPosition[0] and character.yPosition%15 == self.targetPosition[1]:
            self.postHandler()
            return True
        if self.ignoreEndBlocked:
            if abs(character.xPosition%15-self.targetPosition[0])+abs(character.yPosition%15-self.targetPosition[1]) == 1:
                self.postHandler()
                return True
        return False

    def setParameters(self,parameters):
        if "targetPosition" in parameters and "targetPosition" in parameters:
            self.targetPosition = parameters["targetPosition"]
            self.description = self.metaDescription+" %s"%(self.targetPosition,)
        if "ignoreEndBlocked" in parameters and "ignoreEndBlocked" in parameters:
            self.ignoreEndBlocked = parameters["ignoreEndBlocked"]
        return super().setParameters(parameters)

    def solver(self, character):
        self.triggerCompletionCheck(character)
        commandString = self.getSolvingCommandString(character)
        self.randomSeed = random.random()
        if commandString:
            character.runCommandString(commandString)
            return False
        else:
            self.fail()
            return True

    def getRequiredParameters(self):
        parameters = super().getRequiredParameters()
        parameters.append({"name":"targetPosition","type":"coordinate"})
        return parameters

src.quests.addType(GoToPosition)

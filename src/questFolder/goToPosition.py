import src
import random

class GoToPosition(src.quests.MetaQuestSequence):
    type = "GoToPosition"

    def __init__(self, description="go to position", creator=None,targetPosition=None,ignoreEnd=False,ignoreEndBlocked=False):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        self.baseDescription = description
        self.targetPosition = None
        self.hasListener = False
        self.ignoreEndBlocked = False
        if targetPosition:
            self.setParameters({"targetPosition":targetPosition})
        if ignoreEndBlocked:
            self.setParameters({"ignoreEndBlocked":ignoreEndBlocked})

        self.tuplesToStore.append("targetPosition")
        
        self.shortCode = "g"
        self.smallPath = []
        self.path = []

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
        if self.path:
            if isinstance(character.container,src.rooms.Room):
                pos = (character.xPosition,character.yPosition)
            else:
                pos = (character.xPosition%15,character.yPosition%15)
            pos = character.getPosition()
            for step in self.path:
                pos = (pos[0]+step[0],pos[1]+step[1])
                result.append((pos,"path"))
        return result

    def handleMoved(self, extraInfo):
        if not self.active:
            return
        if self.completed:
            return

        convertedDirection = None
        if extraInfo[1] == "west":
            convertedDirection = (-1,0)
        if extraInfo[1] == "east":
            convertedDirection = (1,0)
        if extraInfo[1] == "north":
            convertedDirection = (0,-1)
        if extraInfo[1] == "south":
            convertedDirection = (0,1)

        if self.path and self.path[0] == convertedDirection:
            self.path = self.path[1:]
            if not self.path:
                self.triggerCompletionCheck(extraInfo[0])
                return
            if self.ignoreEndBlocked and len(self.path) == 1:
                self.triggerCompletionCheck(extraInfo[0])
                return
        else:
            if self.path:
                if self.character == src.gamestate.gamestate.mainChar:
                    print(self.path)
                    print(extraInfo)
                    print(convertedDirection)
                    print(self)
            self.generatePath(self.character)

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.handleMoved, "moved")

        super().assignToCharacter(character)

    def getSolvingCommandString(self, character, dryRun=True):

        if character.macroState.get("submenue"):
            return ["esc"]

        if not self.path:
            return

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

        command  = ""
        for step in self.path:
            if step == (1,0):
                command += "d"
            if step == (-1,0):
                command += "a"
            if step == (0,1):
                command += "s"
            if step == (0,-1):
                command += "w"
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

    def generatePath(self,character):
        if character.container.isRoom:
            self.path = character.container.getPathCommandTile(character.getSpacePosition(),self.targetPosition,ignoreEndBlocked=self.ignoreEndBlocked,character=character)[1]
        else:
            self.path = character.container.getPathCommandTile(character.getTilePosition(),character.getSpacePosition(),self.targetPosition,ignoreEndBlocked=self.ignoreEndBlocked,character=character)[1]

    def setParameters(self,parameters):
        if "targetPosition" in parameters and "targetPosition" in parameters:
            self.targetPosition = parameters["targetPosition"]
            self.metaDescription = self.baseDescription+" %s"%(self.targetPosition,)
        if "ignoreEndBlocked" in parameters and "ignoreEndBlocked" in parameters:
            self.ignoreEndBlocked = parameters["ignoreEndBlocked"]
        return super().setParameters(parameters)

    def solver(self, character):
        if not self.path:
            self.generatePath(character)
            return

        if not self.subQuests:
            self.generateSubquests(character)
            if self.subQuests:
                return

        command = self.getSolvingCommandString(character,dryRun=False)
        if command:
            character.runCommandString(command)
            return

        super().solver(character)

    def getRequiredParameters(self):
        parameters = super().getRequiredParameters()
        parameters.append({"name":"targetPosition","type":"coordinate"})
        return parameters

src.quests.addType(GoToPosition)

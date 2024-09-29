import src
import logging

logger = logging.getLogger(__name__)

class GoToPosition(src.quests.MetaQuestSequence):
    type = "GoToPosition"

    def __init__(self, description="go to position", creator=None,targetPosition=None,ignoreEndBlocked=False,reason=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        self.baseDescription = description
        self.targetPosition = None
        self.hasListener = False
        self.ignoreEndBlocked = ignoreEndBlocked
        if targetPosition:
            self.setParameters({"targetPosition":targetPosition})
        if ignoreEndBlocked:
            self.setParameters({"ignoreEndBlocked":ignoreEndBlocked})
        self.reason = reason

        self.shortCode = "g"
        self.smallPath = []
        self.path = []

    def generateTextDescription(self):
        reason = ""
        if self.reason:
            reason = f",\nto {self.reason}"
        extraText = ""
        if self.ignoreEndBlocked:
            extraText = """

The position you should go might be blocked.
So it is enough to go next to the target position to end this quest.
"""

        if self.character.container.isRoom:
            containerString = "room"
        else:
            containerString = "tile"

        text = f"""
Go to position {self.targetPosition} in the same {containerString} you are in{reason}.

This quest ends after you do this.{extraText}"""

        text += """


This quest will not resolve further into subQuests.
Close this menu by pressing esc and follow the instructions on the left hand menu.
"""
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
            pos = character.getPosition()
            for step in self.path:
                pos = (pos[0]+step[0],pos[1]+step[1])
                result.append((pos,"path"))

        result.append(((self.targetPosition[0]+character.getBigPosition()[0]*15,self.targetPosition[1]%15+character.getBigPosition()[1]*15),"target"))
        return result

    def recCheck(self,quest):
        if quest == self:
            return True

        for subQuest in quest.subQuests:
            if self.recCheck(subQuest):
                return True
        return None

    def handleMoved(self, extraInfo):
        if not self.active:
            return
        if self.completed:
            1/0

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

            if not self.isPathSane(extraInfo[0]):
                self.generatePath(extraInfo[0])
                if not self.path:
                    self.fail("no path found")
        else:
            self.generatePath(self.character)

    def handleChangedTile(self, extraInfo=None):
        if not self.active:
            return
        if self.completed:
            1/0
        self.fail()

    def handleCollision(self, extraInfo=None):
        if not self.active:
            return
        if self.completed:
            1/0
        #self.fail()
        self.smallPath = []
        self.path = []

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.handleMoved, "moved")
        self.startWatching(character,self.handleChangedTile, "changedTile")
        self.startWatching(character,self.handleChangedTile, "entered terrain")
        self.startWatching(character,self.handleChangedTile, "entered room")
        self.startWatching(character,self.handleCollision, "itemCollision")

        self.generatePath(character)

        super().assignToCharacter(character)

    def getSolvingCommandString(self, character, dryRun=True):

        if character.macroState.get("submenue"):
            return (["esc"],"exit submenu")

        if not self.path:
            return None

        if character.xPosition%15 == 0:
            return ("d","enter tile")
        if character.xPosition%15 == 14:
            return ("a","enter tile")
        if character.yPosition%15 == 0:
            return ("s","enter tile")
        if character.yPosition%15 == 14:
            return ("w","enter tile")
        if not self.targetPosition:
            return (".12..","wait")

        if self.ignoreEndBlocked and len(self.path) == 1:
            return None

        command  = ""
        movementMap = {(1,0):"d",(-1,0):"a",(0,1):"s",(0,-1):"w"}
        pos = list(character.getPosition())
        for step in self.path:
            pos[0] += step[0]
            pos[1] += step[1]

            items = character.container.getItemByPosition(tuple(pos))
            if items and items[0].type == "Bush":
                command += "J"+movementMap[step]

            command += movementMap[step]
        return (command,"go to target position")

    def triggerCompletionCheck(self, character=None):
        if not self.targetPosition:
            return False
        if not character:
            return False
        if not self.active:
            return None

        if character.xPosition%15 == self.targetPosition[0] and character.yPosition%15 == self.targetPosition[1]:
            self.postHandler()
            return True
        if self.ignoreEndBlocked:
            if abs(character.xPosition%15-self.targetPosition[0])+abs(character.yPosition%15-self.targetPosition[1]) == 1:
                self.postHandler()
                return True
        return False

    def generatePath(self,character,dryRun=True):
        if not character.container:
            self.fail()
            return

        if character.container.isRoom:
            self.path = character.container.getPathCommandTile(character.getSpacePosition(),self.targetPosition,ignoreEndBlocked=self.ignoreEndBlocked,character=character)[1]
        else:
            self.path = character.container.getPathCommandTile(character.getTilePosition(),character.getSpacePosition(),self.targetPosition,ignoreEndBlocked=self.ignoreEndBlocked,character=character)[1]
        if not self.path:
            #if character.room.isRoom:
            #    character.room.cachedPathfinder = None
            if not dryRun:
                character.addMessage(f"moving failed - no path found to {self.targetPosition}")
                self.fail("no path found")

    def setParameters(self,parameters):
        if "targetPosition" in parameters and "targetPosition" in parameters:
            self.targetPosition = parameters["targetPosition"]
            self.metaDescription = self.baseDescription+f" {self.targetPosition}"
        if "ignoreEndBlocked" in parameters and "ignoreEndBlocked" in parameters:
            self.ignoreEndBlocked = parameters["ignoreEndBlocked"]
        return super().setParameters(parameters)

    def solver(self, character):
        if self.triggerCompletionCheck(character):
            return

        if not self.path:
            self.generatePath(character,dryRun=False)
            return

        if not self.isPathSane(character):
            self.generatePath(character,dryRun=False)
            if not self.path:
                character.addMessage("moving failed - no path found (solver)")
                self.fail("no path found")
                return

        if not self.subQuests:
            self.generateSubquests(character)
            if self.subQuests:
                return

        command = self.getSolvingCommandString(character,dryRun=False)
        if command:
            character.runCommandString(command[0])
            return

        super().solver(character)

    def getRequiredParameters(self):
        parameters = super().getRequiredParameters()
        parameters.append({"name":"targetPosition","type":"coordinate"})
        return parameters

    def isPathSane(self,character):
        if not self.path:
            return False

        pos = character.getSpacePosition()
        if not pos:
            logger.error("checking path in non placed character")
            return False
        pos = list(character.getSpacePosition())
        for step in self.path:
            pos[0] += step[0]
            pos[1] += step[1]

        if tuple(pos) == self.targetPosition:
            return True

        return False

src.quests.addType(GoToPosition)

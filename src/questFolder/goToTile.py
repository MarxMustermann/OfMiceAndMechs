import src
import random

class GoToTile(src.quests.Quest):
    type = "GoToTile"

    def __init__(self, description="go to tile", creator=None, lifetime=None, targetPosition=None, paranoid=False, showCoordinates=True):
        questList = []
        super().__init__(questList, creator=creator, lifetime=lifetime)
        self.targetPosition = None
        self.showCoordinates = showCoordinates
        self.description = description
        self.metaDescription = description
        self.path = None
        self.expectedPosition = None
        self.lastPos = None
        self.lastDirection = None
        self.smallPath = None
        self.paranoid = paranoid
        self.sentSubordinates = False

        if targetPosition: 
            self.setParameters({"targetPosition":targetPosition})

        self.attributesToStore.extend([
            "hasListener","paranoid","sentSubordinates" ])

        self.tupleListsToStore.extend([
            "path", "smallPath" ])

        self.tuplesToStore.extend([
            "targetPosition","expectedPosition","lastPos","lastDirection"])

        self.type = "GoToTile"

        self.shortCode = "G"

    def generateTextDescription(self):
        return """
Go to tile %s

This is a pretty common quest.
You have to go from one place to another pretty often.



Quests like this can be pretty boring.
Press c now to use auto move to complete this quest.
Press crtl-d to stop your character from moving.%s
"""%(self.targetPosition,self.showCoordinates,)

    def getQuestMarkersSmall(self,character,dryRun=True,renderForTile=False):
        if isinstance(character.container,src.rooms.Room):
            if renderForTile:
                return []
        else:
            if not renderForTile:
                return []
        self.getSolvingCommandString(character, dryRun=dryRun)
        result = super().getQuestMarkersSmall(character,renderForTile=renderForTile)
        if self.smallPath:
            pos = (character.xPosition,character.yPosition)
            for step in self.smallPath:
                pos = (pos[0]+step[0],pos[1]+step[1])
                result.append((pos,"path"))
        return result

    def getQuestMarkersTile(self,character):
        if self.character.xPosition%15 == 0 or  self.character.yPosition%15 == 0 or self.character.xPosition%15 == 14 or self.character.yPosition%15 == 14:
            return []
        result = super().getQuestMarkersTile(character)
        self.getSolvingCommandString(character)
        if self.expectedPosition:
            result.append((self.expectedPosition,"path"))
        if self.path:
            if self.expectedPosition:
                pos = self.expectedPosition
            elif isinstance(character.container,src.rooms.Room):
                pos = (character.container.xPosition,character.container.yPosition)
            else:
                pos = (character.xPosition//15,character.yPosition//15)
            for step in reversed(self.path):
                pos = (pos[0]+step[0],pos[1]+step[1])
                result.append((pos,"path"))
        result.append((self.targetPosition,"target"))
        return result

    def handleMoved(self, extraInfo):
        if self.completed:
            1/0
        if not self.active:
            return

        converedDirection = None
        if extraInfo[1] == "west":
            converedDirection = (-1,0)
        if extraInfo[1] == "east":
            converedDirection = (1,0)
        if extraInfo[1] == "north":
            converedDirection = (0,-1)
        if extraInfo[1] == "south":
            converedDirection = (0,1)
        if self.smallPath:
            if converedDirection == self.smallPath[0]:
                self.smallPath = self.smallPath[1:]
                return
            else:
                self.smallPath = None

        self.triggerCompletionCheck(extraInfo[0])

    def handleTileChange(self):
        pos = self.character.getBigPosition()
        if pos == self.lastPos:
            return
        self.lastPos = pos

        converedDirection = None
        if self.character.xPosition%15 == 0:
            converedDirection = (1,0)
        if self.character.yPosition%15 == 0:
            converedDirection = (0,1)
        if self.character.xPosition%15 in (13,14):
            converedDirection = (-1,0)
        if self.character.yPosition%15 in (13,14):
            converedDirection = (0,-1)
        if self.path:
            if converedDirection == self.path[-1]:
                self.expectedPosition = None
                self.path = self.path[:-1]
                return
            else:
                self.path = None
                self.getSolvingCommandString(self.character,dryRun=False)
                return
        return

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.handleMoved, "moved")
        self.startWatching(character,self.handleTileChange, "changedTile")

        super().assignToCharacter(character)

    def triggerCompletionCheck(self, character=None):
        if not self.targetPosition:
            return False
        if not character:
            return False
        if not self.active:
            return
        if isinstance(character.container,src.rooms.Room):
            if character.container.xPosition == self.targetPosition[0] and character.container.yPosition == self.targetPosition[1]:
                self.postHandler()
                return True
        elif character.xPosition//15 == self.targetPosition[0] and character.yPosition//15 == self.targetPosition[1]:
            self.postHandler()
            return True
        return False

    def solver(self, character):
        self.activate()
        self.assignToCharacter(character)
        self.smallPath = None
        self.triggerCompletionCheck(character)
        commandString = self.getSolvingCommandString(character,dryRun=False)
        self.randomSeed = random.random()
        if commandString:
            character.runCommandString(commandString)
            return False
        else:
            return True

    def setParameters(self,parameters):
        if "targetPosition" in parameters and "targetPosition" in parameters:
            if not len(parameters["targetPosition"]) > 2:
                parameters["targetPosition"] = (parameters["targetPosition"][0],parameters["targetPosition"][1],0)
            self.targetPosition = parameters["targetPosition"]
            self.description = self.metaDescription
            if self.showCoordinates:
                self.description += " %s"%(self.targetPosition,)
        return super().setParameters(parameters)

    def getRequiredParameters(self):
        parameters = super().getRequiredParameters()
        parameters.append({"name":"targetPosition","type":"coordinate"})
        return parameters

    def reroll(self):
        self.path = None
        super().reroll()

    def getSolvingCommandString(self, character, dryRun = True):
        if not self.targetPosition:
            return ".10.."

        if self.smallPath:

            if isinstance(character.container,src.rooms.TrapRoom) and not (character.faction == character.container.faction):
                actionMap = {(1,0):"Lddk",(-1,0):"Laak",(0,1):"Lssk",(0,-1):"Lwwk"}
            else:
                actionMap = {(1,0):"d",(-1,0):"a",(0,1):"s",(0,-1):"w"}
            command = ""
            for step in self.smallPath:
                command += actionMap[step]

            return command

        if character.macroState.get("submenue"):
            return ["esc"]

        localRandom = random.Random(self.randomSeed)
        if isinstance(character.container, src.rooms.Room):
            if not self.paranoid and localRandom.random() < 0.5 and "fighting" in self.character.skills:
                for otherCharacter in character.container.characters:
                    if otherCharacter.faction == character.faction:
                        continue
                    return "gg"

            charPos = (character.xPosition,character.yPosition,0)
            tilePos = (character.container.xPosition,character.container.yPosition,0)

            direction = None
            path = self.path
            """
            if self.expectedPosition and not (tilePos == self.expectedPosition):
                if tilePos == self.lastPos:
                    direction = self.lastDirection
                else:
                    path = None
            """

            targetPos = (self.targetPosition[0],self.targetPosition[1],0)
            if not path:
                basePath = character.container.container.getPath(tilePos,targetPos,localRandom=localRandom,character=character)
                if not basePath:
                    return ".14..."
                path = list(reversed(basePath))

            if not dryRun:
                self.path = path

            if not path:
                return ".13.."

            if not direction:
                direction = path[-1]

            """
            if self.paranoid:
                if not self.sentSubordinates and character.subordinates:
                    if not dryRun:
                        self.sentSubordinates = True
                    command = "QSNSecureTile\n%s,%s\nlifetime:40; ."%(tilePos[0]+direction[0],tilePos[1]+direction[1],)
                    return command
                if not dryRun:
                    self.sentSubordinates = False
            """

            if direction == (1,0):
                if charPos == (12,6,0):
                    return "d"
                (command,self.smallPath) = character.container.getPathCommandTile(charPos,(12,6,0),localRandom=localRandom,character=character)
                if not command:
                    (command,self.smallPath) = character.container.getPathCommandTile(charPos,(12,6,0),localRandom=localRandom,tryHard=True,character=character)
                if not command and not dryRun:
                    self.path = None
                    self.lastDirection = None
                    return ".19.."
                return command
            if direction == (-1,0):
                if charPos == (0,6,0):
                    return "a"
                (command,self.smallPath) = character.container.getPathCommandTile(charPos,(0,6,0),localRandom=localRandom,character=character)
                if not command:
                    (command,self.smallPath) = character.container.getPathCommandTile(charPos,(0,6,0),localRandom=localRandom,tryHard=True,character=character)
                if not command and not dryRun:
                    self.path = None
                    self.lastDirection = None
                    return ".18.."
                return command
            if direction == (0,1):
                if charPos == (6,12,0):
                    return "s"
                (command,self.smallPath) = character.container.getPathCommandTile(charPos,(6,12,0),localRandom=localRandom,character=character)
                if not command:
                    (command,self.smallPath) = character.container.getPathCommandTile(charPos,(6,12,0),localRandom=localRandom,tryHard=True,character=character)
                if not command and not dryRun:
                    self.path = None
                    self.lastDirection = None
                    return ".17.."
                return command
            if direction == (0,-1):
                if charPos == (6,0,0):
                    return "w"
                (command,self.smallPath) = character.container.getPathCommandTile(charPos,(6,0,0),localRandom=localRandom,character=character)
                if not command:
                    (command,self.smallPath) = character.container.getPathCommandTile(charPos,(6,0,0),localRandom=localRandom,tryHard=True,character=character)
                if not command and not dryRun:
                    self.path = None
                    self.lastDirection = None
                    return ".16.."
                return command
            return ".15.."
        else:
            if not self.paranoid and localRandom.random() < 0.5 and "fighting" in self.character.skills:
                for otherCharacter in character.container.characters:
                    if not (otherCharacter.xPosition//15 == character.xPosition//15 and otherCharacter.yPosition//15 == character.yPosition//15):
                        continue
                    if otherCharacter.faction == character.faction:
                        continue
                    return "gg"

            tilePos = (character.xPosition//15,character.yPosition//15,0)
            charPos = (character.xPosition%15,character.yPosition%15,0)

            direction = None
            path = self.path
            """
            if self.expectedPosition and not (tilePos == self.expectedPosition):
                if tilePos == self.lastPos:
                    direction = self.lastDirection
                else:
                    path = None
            """

            targetPos = (self.targetPosition[0],self.targetPosition[1],0)
            if not path and not direction:
                basePath = character.container.getPath(tilePos,targetPos,localRandom=localRandom)
                if not basePath:
                    return ".3.."
                path = list(reversed(basePath))

            if not dryRun:
                self.path = path

            if not path and not direction:
                return ".26.."

            if direction == None:
                if charPos == (0,7,0):
                    return "d"
                if charPos == (7,14,0):
                    return "w"
                if charPos == (7,0,0):
                    return "s"
                if charPos == (14,7,0):
                    return "a"

            if not direction:
                direction = path[-1]

            """
            if self.paranoid:
                if not self.sentSubordinates and character.subordinates:
                    if not dryRun:
                        self.sentSubordinates = True
                    command = "QSNSecureTile\n%s,%s\nlifetime:40; ."%(tilePos[0]+direction[0],tilePos[1]+direction[1],)
                    return command
                self.sentSubordinates = False
            """

            if direction == (1,0):
                if charPos == (13,7,0):
                    return "d"
                if charPos == (14,7,0):
                    return "d"
                (command,self.smallPath) = character.container.getPathCommandTile(tilePos,charPos,(13,7,0),localRandom=localRandom,character=character)
                if not command:
                    (command,self.smallPath) = character.container.getPathCommandTile(tilePos,charPos,(13,7,0),localRandom=localRandom,tryHard=True,character=character)
                if not command and not dryRun:
                    self.path = None
                    self.lastDirection = None
                    items = character.container.getItemByPosition(character.getPosition(offset=(1,0,0)))
                    if not items:
                        return "d"
                    else:
                        dropDirection = random.choice(["l","La","Ls","Lw"])
                        return "dk"+dropDirection
                    return ".12.."
                return command
            if direction == (-1,0):
                if charPos == (1,7,0):
                    return "a"
                if charPos == (0,7,0):
                    return "a"
                (command,self.smallPath) = character.container.getPathCommandTile(tilePos,charPos,(1,7,0),localRandom=localRandom,character=character)
                if not command:
                    (command,self.smallPath) = character.container.getPathCommandTile(tilePos,charPos,(1,7,0),localRandom=localRandom,tryHard=True,character=character)
                if not command and not dryRun:
                    self.path = None
                    self.lastDirection = None
                    items = character.container.getItemByPosition(character.getPosition(offset=(-1,0,0)))
                    if not items:
                        return "a"
                    else:
                        dropDirection = random.choice(["l","Ls","Lw","Ld"])
                        return "ak"+dropDirection
                    return ".12.."
                return command
            if direction == (0,1):
                if charPos == (7,13,0):
                    return "s"
                if charPos == (7,14,0):
                    return "s"
                (command,self.smallPath) = character.container.getPathCommandTile(tilePos,charPos,(7,13,0),localRandom=localRandom,character=character)
                if not command:
                    (command,self.smallPath) = character.container.getPathCommandTile(tilePos,charPos,(7,13,0),localRandom=localRandom,tryHard=True,character=character)
                if not command and not dryRun:
                    self.path = None
                    self.lastDirection = None
                    items = character.container.getItemByPosition(character.getPosition(offset=(0,1,0)))
                    if not items:
                        return "s"
                    else:
                        dropDirection = random.choice(["l","La","Lw","Ld"])
                        return "sk"+dropDirection
                    return ".12.."
                return command
            if direction == (0,-1):
                if charPos == (7,1,0):
                    return "w"
                if charPos == (7,0,0):
                    return "w"
                (command,self.smallPath) = character.container.getPathCommandTile(tilePos,charPos,(7,1,0),localRandom=localRandom,character=character)
                if not command:
                    (command,self.smallPath) = character.container.getPathCommandTile(tilePos,charPos,(7,1,0),localRandom=localRandom,tryHard=True,character=character)
                if not command and not dryRun:
                    self.path = None
                    self.lastDirection = None
                    items = character.container.getItemByPosition(character.getPosition(offset=(0,-1,0)))
                    if not items:
                        return "w"
                    else:
                        dropDirection = random.choice(["l","La","Ls","Ld"])
                        return "wk"+dropDirection
                    return ".12.."
                return command
            return ".17.."
        return ".20.."

src.quests.addType(GoToTile)

import src
import random

class GoToTile(src.quests.MetaQuestSequence):
    type = "GoToTile"

    def __init__(self, description="go to tile", creator=None, targetPosition=None, lifetime=None, paranoid=False, showCoordinates=True,reason=None):
        questList = []
        super().__init__(questList, creator=creator, lifetime=lifetime)
        self.metaDescription = "%s %s"%(description,targetPosition,)
        if len(targetPosition) < 3:
            targetPosition = (targetPosition[0],targetPosition[1],0)
        self.targetPosition = targetPosition
        self.path = None
        self.lastPos = None
        self.paranoid = paranoid
        self.showCoordinates = showCoordinates
        self.reason = reason

    def sanatiyCheckPath(self):
        1/0

    def handleChangedTile(self):
        if not self.active:
            return

        if self.completed:
            1/0

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
            if converedDirection == self.path[0]:
                self.expectedPosition = None
                self.path = self.path[1:]
                if not self.path:
                    self.triggerCompletionCheck(self.character)
                return
            else:
                self.path = None
                self.generatePath(self.character)
                return
        return

    def handleMoved(self,extraInfo):
        if not self.active:
            return

        if self.completed:
            1/0

        if not self.character:
            return

        #self.generateSubquests(self.character)

    def getQuestMarkersTile(self,character):
        if self.character.xPosition%15 == 0 or  self.character.yPosition%15 == 0 or self.character.xPosition%15 == 14 or self.character.yPosition%15 == 14:
            return []
        result = super().getQuestMarkersTile(character)
        self.getSolvingCommandString(character)
        if self.path:
            if isinstance(character.container,src.rooms.Room):
                pos = (character.container.xPosition,character.container.yPosition)
            else:
                pos = (character.xPosition//15,character.yPosition//15)
            for step in self.path:
                pos = (pos[0]+step[0],pos[1]+step[1])
                result.append((pos,"path"))
        result.append((self.targetPosition,"target"))
        return result

    def assignToCharacter(self, character):
        if self.character:
            return
        
        self.startWatching(character,self.handleChangedTile, "changedTile")
        self.startWatching(character,self.handleMoved, "moved")

        return super().assignToCharacter(character)

    def generateTextDescription(self):
        reason = ""
        if self.reason:
            reason = ", to %s"%(self.reason,)

        text = """
Go to tile %s%s.
"""%(self.targetPosition,reason,)

        if self.character.getBigPosition() == self.targetPosition:
            text += """

You are on the target tile.
"""
        else:
            direction = ""
            diffXBig = self.targetPosition[0] - self.character.getBigPosition()[0]
            if diffXBig < 0:
                direction = "and %s tiles to the west"%(-diffXBig,)
            if diffXBig > 0:
                direction = "and %s tiles to the east"%(diffXBig,)
            diffYBig = self.targetPosition[1] - self.character.getBigPosition()[1]
            if diffYBig < 0:
                direction = "and %s tiles to the north"%(-diffYBig,)
            if diffYBig > 0:
                direction = "and %s tiles to the south"%(diffYBig,)
            text += """

The target tile is %s
"""%(direction[4:],)
        return text

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

    def isPathSane(self,character):
        if not self.path:
            return False

        bigPos = list(character.getBigPosition())
        for step in self.path:
            bigPos[0] += step[0]
            bigPos[1] += step[1]

        if tuple(bigPos) == self.targetPosition:
            return True
        
        return False

    def getNextStep(self,character=None,ignoreCommands=False):
        if character == None:
            return (None,None)

        if not ignoreCommands and character.macroState.get("submenue"):
            return (None,(["esc"],"exit submenu"))

        if not self.path:
            self.generatePath(character)

        if not self.path:
            return (None,None)

        if self.subQuests:
            return (None,None)

        if isinstance(character.container,src.rooms.Room):
            # TODO: reenable random
            if not self.paranoid and random.random() < 1.5 and "fighting" in self.character.skills:
                for otherCharacter in character.container.characters:
                    if otherCharacter.faction == character.faction:
                        continue
                    return (None,("gg","guard the room"))

            if not self.isPathSane(character):
                self.generatePath(character)
                if not self.path:
                    self.fail()
                    return (None,None)

            if self.path[0] == (0,1):
                if character.getPosition() == (6,12,0):
                    return (None,("ss","exit the room"))
                quest = src.quests.questMap["GoToPosition"](targetPosition=(6,12,0),description="go to room exit",reason="reach the rooms exit")
                quest.assignToCharacter(character)
                quest.generatePath(character)
                return ([quest],None)
            if self.path[0] == (0,-1):
                if character.getPosition() == (6,0,0):
                    return (None,("ww","exit the room"))
                quest = src.quests.questMap["GoToPosition"](targetPosition=(6,0,0),description="go to room exit",reason="reach the rooms exit")
                quest.assignToCharacter(character)
                quest.generatePath(character)
                return ([quest],None)
            if self.path[0] == (1,0):
                if character.getPosition() == (12,6,0):
                    return (None,("dd","exit the room"))
                quest = src.quests.questMap["GoToPosition"](targetPosition=(12,6,0),description="go to room exit",reason="reach the rooms exit")
                quest.assignToCharacter(character)
                quest.generatePath(character)
                return ([quest],None)
            if self.path[0] == (-1,0):
                if character.getPosition() == (0,6,0):
                    return (None,("aa","exit the room"))
                quest = src.quests.questMap["GoToPosition"](targetPosition=(0,6,0),description="go to room exit",reason="reach the rooms exit")
                quest.assignToCharacter(character)
                quest.generatePath(character)
                return ([quest],None)
        else:
            # TODO: reenable random
            if not self.paranoid and random.random() < 1.5 and "fighting" in self.character.skills:
                if character.container.getEnemiesOnTile(character):
                    return (None,("gg","guard the tile"))
            if character.xPosition%15 == 7 and character.yPosition%15 == 14:
                return (None,("w","enter the tile"))
            if character.xPosition%15 == 7 and character.yPosition%15 == 0:
                return (None,("s","enter the tile"))
            if character.xPosition%15 == 14 and character.yPosition%15 == 7:
                return (None,("a","enter the tile"))
            if character.xPosition%15 == 0 and character.yPosition%15 == 7:
                return (None,("d","enter the tile"))

            if not self.isPathSane(character):
                self.generatePath(character)
                if not self.path:
                    self.fail()
                    return (None,None)

            if self.path[0] == (0,1):
                if character.xPosition%15 == 7 and character.yPosition%15 == 13:
                    return (None,("s","exit the tile"))
                quest = src.quests.questMap["GoToPosition"](targetPosition=(7,13,0),description="go to tile edge",reason="reach the tiles edge")
                quest.generatePath(character)
                return ([quest],None)
            if self.path[0] == (0,-1):
                if character.xPosition%15 == 7 and character.yPosition%15 == 1:
                    return (None,("w","exit the tile"))
                quest = src.quests.questMap["GoToPosition"](targetPosition=(7,1,0),description="go to tile edge",reason="reach the tiles edge")
                quest.generatePath(character)
                return ([quest],None)
            if self.path[0] == (1,0):
                if character.xPosition%15 == 13 and character.yPosition%15 == 7:
                    return (None,("d","exit the tile"))
                quest = src.quests.questMap["GoToPosition"](targetPosition=(13,7,0),description="go to tile edge",reason="reach the tiles edge")
                quest.generatePath(character)
                return ([quest],None)
            if self.path[0] == (-1,0):
                if character.xPosition%15 == 1 and character.yPosition%15 == 7:
                    return (None,("a","exit the tile"))
                quest = src.quests.questMap["GoToPosition"](targetPosition=(1,7,0),description="go to tile edge",reason="reach the tiles edge")
                quest.generatePath(character)
                return ([quest],None)
    
    def generateSubquests(self, character=None):
        (nextQuests,nextCommand) = self.getNextStep(character,ignoreCommands=True)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
            return

    def getSolvingCommandString(self, character, dryRun=True):
        nextStep = self.getNextStep(character)
        if nextStep == (None,None):
            return super().getSolvingCommandString(character)
        return nextStep[1]

    def generatePath(self,character):
        self.path = character.getTerrain().getPath(character.getBigPosition(),self.targetPosition,character=character)

    def solver(self, character):
        if not self.path:
            self.generatePath(character)

        (nextQuests,nextCommand) = self.getNextStep(character)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
                self.startWatching(quest,self.unhandledSubQuestFail,"failed")
            return

        if nextCommand:
            character.runCommandString(nextCommand[0])
            return
        super().solver(character)

    def unhandledSubQuestFail(self,extraParam):
        if not extraParam["quest"] in self.subQuests:
            return

        self.subQuests.remove(extraParam["quest"])

        if extraParam["reason"] and "no path found" in extraParam["reason"]:
            quest = src.quests.questMap["ClearPathToPosition"](targetPosition=extraParam["quest"].targetPosition)
            self.addQuest(quest)
            self.startWatching(quest,self.unhandledSubQuestFail,"failed")
            return

        self.fail(extraParam["reason"])


src.quests.addType(GoToTile)

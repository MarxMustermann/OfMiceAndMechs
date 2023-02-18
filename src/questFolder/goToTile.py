import src
import random

class GoToTile(src.quests.MetaQuestSequence):
    type = "GoToTile"

    def __init__(self, description="go to tile", creator=None, targetPosition=None, lifetime=None, paranoid=False, showCoordinates=True):
        questList = []
        super().__init__(questList, creator=creator, lifetime=lifetime)
        self.metaDescription = description
        if len(targetPosition) < 3:
            targetPosition = (targetPosition[0],targetPosition[1],0)
        self.targetPosition = targetPosition
        self.path = None
        self.lastPos = None
        self.paranoid = paranoid
        self.showCoordinates = showCoordinates

    def sanatiyCheckPath(self):
        1/0

    def handleChangedTile(self):
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
        if self.completed:
            1/0

        if not self.character:
            return

        self.generateSubquests(self.character)

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
        return """
operate the machine on %s
"""%(self.targetPosition,)

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

    def getNextStep(self,character=None):
        if character == None:
            return (None,None)

        if character.macroState.get("submenue"):
            return (None,["esc"])

        if not self.path:
            self.generatePath(character)

        if not self.path:
            return (None,None)

        if self.subQuests:
            return (None,None)

        if isinstance(character.container,src.rooms.Room):
            if not self.paranoid and random.random() < 0.5 and "fighting" in self.character.skills:
                for otherCharacter in character.container.characters:
                    if otherCharacter.faction == character.faction:
                        continue
                    print("go fight within room")
                    return (None,"gg")

            if not self.isPathSane(character):
                self.generatePath(character)
                if not self.path:
                    self.fail()
                    return (None,None)

            if self.path[0] == (0,1):
                if character.getPosition() == (6,12,0):
                    return (None,"ss")
                quest = src.quests.questMap["GoToPosition"](targetPosition=(6,12,0))
                quest.assignToCharacter(character)
                quest.generatePath(character)
                return ([quest],None)
            if self.path[0] == (0,-1):
                if character.getPosition() == (6,0,0):
                    return (None,"ww")
                quest = src.quests.questMap["GoToPosition"](targetPosition=(6,0,0))
                quest.assignToCharacter(character)
                quest.generatePath(character)
                return ([quest],None)
            if self.path[0] == (1,0):
                if character.getPosition() == (12,6,0):
                    return (None,"dd")
                quest = src.quests.questMap["GoToPosition"](targetPosition=(12,6,0))
                quest.assignToCharacter(character)
                quest.generatePath(character)
                return ([quest],None)
            if self.path[0] == (-1,0):
                if character.getPosition() == (0,6,0):
                    return (None,"aa")
                quest = src.quests.questMap["GoToPosition"](targetPosition=(0,6,0))
                quest.assignToCharacter(character)
                quest.generatePath(character)
                return ([quest],None)
        else:
            if not self.paranoid and random.random() < 0.5 and "fighting" in self.character.skills:
                if character.container.getEnemiesOnTile(character):
                    return (None,"gg")
            if character.xPosition%15 == 7 and character.yPosition%15 == 14:
                return (None,"w")
            if character.xPosition%15 == 7 and character.yPosition%15 == 0:
                return (None,"s")
            if character.xPosition%15 == 14 and character.yPosition%15 == 7:
                return (None,"a")
            if character.xPosition%15 == 0 and character.yPosition%15 == 7:
                return (None,"d")

            if not self.isPathSane(character):
                self.generatePath(character)
                if not self.path:
                    self.fail()
                    return (None,None)

            if self.path[0] == (0,1):
                if character.xPosition%15 == 7 and character.yPosition%15 == 13:
                    return (None,"s")
                quest = src.quests.questMap["GoToPosition"](targetPosition=(7,13,0))
                quest.generatePath(character)
                return ([quest],None)
            if self.path[0] == (0,-1):
                if character.xPosition%15 == 7 and character.yPosition%15 == 1:
                    return (None,"w")
                quest = src.quests.questMap["GoToPosition"](targetPosition=(7,1,0))
                quest.generatePath(character)
                return ([quest],None)
            if self.path[0] == (1,0):
                if character.xPosition%15 == 13 and character.yPosition%15 == 7:
                    return (None,"d")
                quest = src.quests.questMap["GoToPosition"](targetPosition=(13,7,0))
                quest.generatePath(character)
                return ([quest],None)
            if self.path[0] == (-1,0):
                if character.xPosition%15 == 1 and character.yPosition%15 == 7:
                    return (None,"a")
                quest = src.quests.questMap["GoToPosition"](targetPosition=(1,7,0))
                quest.generatePath(character)
                return ([quest],None)
    
    def generateSubquests(self, character=None):
        return self.getNextStep(character)[0]

    def getSolvingCommandString(self, character, dryRun=True):
        return self.getNextStep(character)[1]

    def generatePath(self,character):
        self.path = character.getTerrain().getPath(character.getBigPosition(),self.targetPosition)

    def solver(self, character):
        if not self.path:
            self.generatePath(character)

        (nextQuests,nextCommand) = self.getNextStep(character)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
            return

        if nextCommand:
            character.runCommandString(nextCommand)
            return
        super().solver(character)

src.quests.addType(GoToTile)

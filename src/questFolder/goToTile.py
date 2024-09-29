import random

import src


class GoToTile(src.quests.MetaQuestSequenceV2):
    type = "GoToTile"

    def __init__(self, description="go to tile", creator=None, targetPosition=None, lifetime=None, paranoid=False, showCoordinates=True,reason=None,abortHealthPercentage=0):
        questList = []
        super().__init__(questList, creator=creator, lifetime=lifetime)
        self.metaDescription = f"{description} {targetPosition}"
        if len(targetPosition) < 3:
            targetPosition = (targetPosition[0],targetPosition[1],0)
        self.targetPosition = targetPosition
        self.path = None
        self.lastPos = None
        self.paranoid = paranoid
        self.showCoordinates = showCoordinates
        self.reason = reason
        self.abortHealthPercentage = abortHealthPercentage

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
            return None

        self.startWatching(character,self.handleChangedTile, "changedTile")
        self.startWatching(character,self.handleMoved, "moved")

        return super().assignToCharacter(character)

    def generateTextDescription(self):
        reason = ""
        if self.reason:
            reason = f", to {self.reason}"

        text = f"""
Go to tile {self.targetPosition}{reason}.
"""

        if self.character.getBigPosition() == self.targetPosition:
            text += """

You are on the target tile.
"""
        else:
            direction = ""
            diffXBig = self.targetPosition[0] - self.character.getBigPosition()[0]
            if diffXBig < 0:
                direction = f"and {-diffXBig} tiles to the west"
            if diffXBig > 0:
                direction = f"and {diffXBig} tiles to the east"
            diffYBig = self.targetPosition[1] - self.character.getBigPosition()[1]
            if diffYBig < 0:
                direction = f"and {-diffYBig} tiles to the north"
            if diffYBig > 0:
                direction = f"and {diffYBig} tiles to the south"
            text += f"""

The target tile is {direction[4:]}
"""
        return text

    def triggerCompletionCheck(self, character=None):
        if not self.targetPosition:
            return False
        if not character:
            return False
        if not self.active:
            return None
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

    def getNextStep(self,character=None,ignoreCommands=False,dryRun=True):
        if character is None:
            return (None,None)

        if not ignoreCommands and character.macroState.get("submenue"):
            return (None,(["esc"],"exit submenu"))

        if character.health < character.maxHealth*self.abortHealthPercentage:
            if not dryRun:
                self.fail("low health")
            return (None,None)

        if not self.path:
            self.generatePath(character)

        if not self.path:
            return (None,None)

        if self.subQuests:
            return (None,None)

        if isinstance(character.container,src.rooms.Room):
            # TODO: reenable random
            if not self.paranoid:
                if random.random() < 1.5 and "fighting" in self.character.skills:
                    for otherCharacter in character.container.characters:
                        if otherCharacter.faction == character.faction:
                            continue
                        return (None,("gg","guard the room"))

                for otherCharacter in character.container.characters:
                    if otherCharacter.faction == character.faction:
                        continue
                    if character.health < character.maxHealth//5:
                        quest = src.quests.questMap["Flee"]()
                        return ([quest],None)
                    else:
                        quest = src.quests.questMap["Fight"]()
                        return ([quest],None)

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
            return None
        else:
            if character.xPosition%15 == 7 and character.yPosition%15 == 14:
                return (None,("w","enter the tile"))
            if character.xPosition%15 == 7 and character.yPosition%15 == 0:
                return (None,("s","enter the tile"))
            if character.xPosition%15 == 14 and character.yPosition%15 == 7:
                return (None,("a","enter the tile"))
            if character.xPosition%15 == 0 and character.yPosition%15 == 7:
                return (None,("d","enter the tile"))

            # TODO: reenable random
            if not self.paranoid:
                if random.random() < 1.5 and "fighting" in self.character.skills:
                    if character.container.getEnemiesOnTile(character):
                        return (None,("gg","guard the tile"))

                    if character.container.getEnemiesOnTile(character):
                        if character.health < character.maxHealth//5:
                            quest = src.quests.questMap["Flee"]()
                            return ([quest],None)
                        else:
                            quest = src.quests.questMap["Fight"]()
                            return ([quest],None)

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
            return None


    def generatePath(self,character):
        self.path = character.getTerrain().getPath(character.getBigPosition(),self.targetPosition,character=character,avoidEnemies=True)

    def unhandledSubQuestFail(self,extraParam):
        if extraParam["quest"] not in self.subQuests:
            return

        self.subQuests.remove(extraParam["quest"])

        if extraParam["reason"] and "no path found" in extraParam["reason"]:
            quest = src.quests.questMap["ClearPathToPosition"](targetPosition=extraParam["quest"].targetPosition)
            self.addQuest(quest)
            self.startWatching(quest,self.unhandledSubQuestFail,"failed")
            return

        self.fail(extraParam["reason"])


src.quests.addType(GoToTile)

import logging

import numpy as np
import tcod

import src

logger = logging.getLogger(__name__)


class GoToTerrain(src.quests.MetaQuestSequence):
    '''
    quest to move to a specific terrain

    Params:
        description: the description shown on the UI
        creator: 
    '''
    type = "GoToTerrain"
    lowLevel = True
    def __init__(self, description="go to terrain", creator=None, targetTerrain=None, allowTerrainMenu=True, reason=None,terrainsWeight= None):
        if targetTerrain:
            if targetTerrain[0] < 1 or targetTerrain[0] > 13:
                raise ValueError("target position out of range")
            if targetTerrain[1] < 1 or targetTerrain[1] > 13:
                raise ValueError("target position out of range")

        questList = []
        super().__init__(questList, creator=creator)
        self.targetTerrain = targetTerrain
        self.allowTerrainMenu = allowTerrainMenu
        self.metaDescription = description + " " + str(self.targetTerrain)
        self.reason = reason
        self.terrainsWeight = terrainsWeight

    def triggerCompletionCheck(self,character=None):
        if character is None:
            return False
        if len(self.targetTerrain) < 3:
            self.targetTerrain = (self.targetTerrain[0],self.targetTerrain[1],0)

        if character.getBigPosition()[0] == 0:
            return False
        if character.getBigPosition()[0] == 14:
            return False
        if character.getBigPosition()[1] == 0:
            return False
        if character.getBigPosition()[1] == 14:
            return False

        if self.targetTerrain == character.getTerrainPosition():
            self.postHandler()
            return True
        return False

    def getTerrainPath(self,startPos,targetPos):

        if self.terrainsWeight:
            terrainMap = np.zeros((14,14),dtype=np.int16)

            min_weight = min(self.terrainsWeight.values())
            if min_weight<0:
                logger.warn("Terrains Weight Map is wrongly constructed")

            for x in range(1,14):
                for y in range(1,14):
                    terrainMap[x][y] = self.terrainsWeight[(x,y,0)]
        else:
            terrainMap = np.ones((14,14),dtype=np.int16)

        pathfinder = tcod.path.AStar(terrainMap,diagonal = 0)
        path = pathfinder.get_path(startPos[0],startPos[1],targetPos[0],targetPos[1])

        return path

    def getNextStep(self,character,ignoreCommands=False, dryRun = True):
        if self.subQuests:
            return (None,None)

        terrainPos = character.getTerrainPosition()

        if terrainPos != self.targetTerrain:
            path = self.getTerrainPath(terrainPos,self.targetTerrain)
            if not len(path):
                self.fail("Empty Path")

            targetTerrain = path[0]
        else:
            targetTerrain = self.targetTerrain

        submenue = character.macroState.get("submenue")
        if submenue:
            if submenue.tag == "terrainMovementmenu":
                movementCommand = ""
                movementCommand += "s"*(targetTerrain[1]-submenue.cursor[1])
                movementCommand += "w"*(submenue.cursor[1]-targetTerrain[1])
                movementCommand += "d"*(targetTerrain[0]-submenue.cursor[0])
                movementCommand += "a"*(submenue.cursor[0]-targetTerrain[0])
                return (None,(movementCommand+"j","start the auto movement"))
            return (None,(["esc"],"close the menu"))

        try:
            self.allowTerrainMenu
        except:
            self.allowTerrainMenu = True

        if self.allowTerrainMenu:
            movementCommand = ""
            movementCommand += "s"*(targetTerrain[1]-character.getTerrain().yPosition)
            movementCommand += "w"*(character.getTerrain().yPosition-targetTerrain[1])
            movementCommand += "d"*(targetTerrain[0]-character.getTerrain().xPosition)
            movementCommand += "a"*(character.getTerrain().xPosition-targetTerrain[0])

            menuCommand = "g"
            if "runaction" in character.interactionState:
                menuCommand = ""

            return (None,(menuCommand+"M"+movementCommand+"j","auto move to terrain"))

        if character.getTerrain().yPosition > targetTerrain[1]:
            if character.getBigPosition()[0] == 0:
                return (None, ("d","enter the terrain"))
            if character.getBigPosition()[0] == 14:
                return (None, ("a","enter the terrain"))
            if character.getBigPosition()[1] == 14:
                return (None, ("w","enter the terrain"))
            
            if character.getBigPosition() not in ((7,1,0),(7,0,0)) and not (character.getBigPosition()[0] in (0,14,) or character.getBigPosition()[1] in (0,14,)):
                return (None,("gmW","go to north tile edge"))
            if character.getPosition() != (7 * 15 + 7, 15 * 1 + 1, 0) and character.getBigPosition() not in ((7,0,0),):
                quest = src.quests.questMap["GoToPosition"](targetPosition=(7,1,0))
                return ([quest],None)
            return (None,("w","go to terrain"))

        if character.getTerrain().yPosition < targetTerrain[1]:
            if character.getBigPosition()[0] == 0:
                return (None, ("d","enter the terrain"))
            if character.getBigPosition()[0] == 14:
                return (None, ("a","enter the terrain"))
            if character.getBigPosition()[1] == 0:
                return (None, ("s","enter the terrain"))
            
            if character.getBigPosition() not in ((7,13,0),(7,14,0)) and not (character.getBigPosition()[0] in (0,14,) or character.getBigPosition()[1] in (0,14,)):
                return (None,("gmS","go to south tile edge"))
            if character.getPosition() != (7 * 15 + 7, 15 * 13 + 13, 0) and character.getBigPosition() not in ((7,14,0),):
                quest = src.quests.questMap["GoToPosition"](targetPosition=(7,13,0))
                return ([quest],None)
            return (None,("s","go to terrain"))

        if character.getTerrain().xPosition > targetTerrain[0]:
            if character.getBigPosition()[0] == 14:
                return (None, ("a","enter the terrain"))
            if character.getBigPosition()[1] == 0:
                return (None, ("s","enter the terrain"))
            if character.getBigPosition()[1] == 14:
                return (None, ("w","enter the terrain"))
            
            if character.getBigPosition() not in ((1,7,0),(0,7,0)) and not (character.getBigPosition()[0] in (0,14,) or character.getBigPosition()[1] in (0,14,)):
                return (None,("gmA","go to west tile edge"))
            if character.getPosition() != (1 * 15 + 1, 15 * 7 + 7, 0) and character.getBigPosition() not in ((0,7,0),):
                quest = src.quests.questMap["GoToPosition"](targetPosition=(1,7,0))
                return ([quest],None)
            return (None,("a","go to terrain"))

        if character.getTerrain().xPosition < targetTerrain[0]:
            if character.getBigPosition()[0] == 0:
                return (None, ("d","enter the terrain"))
            if character.getBigPosition()[1] == 0:
                return (None, ("s","enter the terrain"))
            if character.getBigPosition()[1] == 14:
                return (None, ("w","enter the terrain"))
            
            if character.getBigPosition() not in ((13,7,0),(14,7,0)) and not (character.getBigPosition()[0] in (0,14,) or character.getBigPosition()[1] in (0,14,)):
                return (None,("gmD","go to east tile edge"))
            if character.getPosition() != (13 * 15 + 13, 15 * 7 + 7, 0) and character.getBigPosition() not in ((14,7,0),):
                quest = src.quests.questMap["GoToPosition"](targetPosition=(13,7,0))
                return ([quest],None)
            return (None,("d","go to terrain"))

        if character.getBigPosition()[0] == 14:
            return (None, ("a","enter the terrain"))
        if character.getBigPosition()[0] == 0:
            return (None, ("d","enter the terrain"))
        if character.getBigPosition()[1] == 0:
            return (None, ("s","enter the terrain"))
        if character.getBigPosition()[1] == 14:
            return (None, ("w","enter the terrain"))

        return (None,None)

    def handleChangedTerrain(self,extraInfo):
        self.triggerCompletionCheck(extraInfo["character"])

    def handleChangedTile(self,extraInfo=None):
        self.triggerCompletionCheck(self.character)

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.handleChangedTerrain, "changedTerrain")
        self.startWatching(character,self.handleChangedTile, "changedTile")
        super().assignToCharacter(character)

src.quests.addType(GoToTerrain)

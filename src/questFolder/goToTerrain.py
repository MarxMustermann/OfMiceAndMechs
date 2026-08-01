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

    def triggerCompletionCheck(self,character=None,dryRun=True):
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
            if not dryRun:
                self.postHandler()
            return True
        return False

    def generateTextDescription(self):
        '''
        generate a description of this quest
        '''
        reason = (src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),".")
        if self.reason:
            reason = (src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),f",",f" to {self.reason}")

        directionString = ""
        current_position = self.character.getTerrainPosition()
        directions = []
        if current_position[0] < self.targetTerrain[0]:
            amount = self.targetTerrain[0]-current_position[0]
            directions.append(f"{amount} terrains to the east")
        if current_position[0] > self.targetTerrain[0]:
            amount = current_position[0]-self.targetTerrain[0]
            directions.append(f"{amount} terrains to the west")
        if current_position[1] < self.targetTerrain[1]:
            amount = self.targetTerrain[1]-current_position[1]
            directions.append(f"{amount} terrains to the south")
        if current_position[1] > self.targetTerrain[1]:
            amount = current_position[1]-self.targetTerrain[1]
            directions.append(f"{amount} terrains to the north")
        directionString = " and ".join(directions)

        text = []
        text.extend([(src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),f"Go to terrain {self.targetTerrain}"),reason,f"""

""",(src.pseudoUrwid.AttrSpec(src.interaction.ui_hint_color,"black"),"You can change terrains by simply moving through the blue stuff at the edge of the map."),f"""

The target terrain is {directionString}.

"""])

        return text

    def getTerrainPath(self,startPos,targetPos):

        if self.terrainsWeight:
            terrainMap = np.zeros((14,14),dtype=np.int16)

            min_weight = min(self.terrainsWeight.values())
            if min_weight<0:
                logger.warn("Terrains Weight Map is wrongly constructed")

            for x in range(1,14):
                for y in range(1,14):
                    terrainMap[x][y] = self.terrainsWeight[(x,y,0)]
            terrainMap[7][7] = 32000
        else:
            terrainMap = np.ones((14,14),dtype=np.int16)
            terrainMap[7][7] = 32000

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
                return self._solver_trigger_fail(dryRun,"empty path")

            targetTerrain = path[0]
        else:
            targetTerrain = self.targetTerrain
        if self.allowTerrainMenu:
            targetTerrain = self.targetTerrain

        submenue = character.macroState.get("submenue")
        if submenue:
            if submenue.tag == "activitySelection":
                if self.allowTerrainMenu:
                    return (None,("M","open the terrain auto movement menu"))
                else:
                    return (None,("m","open the tile auto movement menu"))
            if submenue.tag == "terrainMovementmenu":
                command = submenue.get_command_to_select_position(targetTerrain)
                return (None,(command,"start the auto movement"))
            if submenue.tag == "tileMovementmenu":
                if character.getTerrain().yPosition > targetTerrain[1]:
                    if character.getBigPosition() not in ((7,1,0),(7,0,0)) and not (character.getBigPosition()[0] in (0,14,) or character.getBigPosition()[1] in (0,14,)):
                        return (None,("W","go to north tile edge"))
                if character.getTerrain().yPosition < targetTerrain[1]:
                    if character.getBigPosition() not in ((7,13,0),(7,14,0)) and not (character.getBigPosition()[0] in (0,14,) or character.getBigPosition()[1] in (0,14,)):
                        return (None,("S","go to south tile edge"))
                if character.getTerrain().xPosition > targetTerrain[0]:
                    if character.getBigPosition() not in ((1,7,0),(0,7,0)) and not (character.getBigPosition()[0] in (0,14,) or character.getBigPosition()[1] in (0,14,)):
                        return (None,("A","go to west tile edge"))
                if character.getTerrain().xPosition < targetTerrain[0]:
                    if character.getBigPosition() not in ((13,7,0),(14,7,0)) and not (character.getBigPosition()[0] in (0,14,) or character.getBigPosition()[1] in (0,14,)):
                        return (None,("D","go to east tile edge"))
            return (None,(["esc"],"close the menu"))

        if character.getNearbyEnemies():
            quest = src.quests.questMap["Fight"]()
            return ([quest],None)

        # open the terrain fast movement code
        if self.allowTerrainMenu:
            return (None,("gM","open terrain fast travel menu"))

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

        return (None,(".","wait"))

    def handleChangedTerrain(self,extraInfo):
        self.triggerCompletionCheck(extraInfo["character"],dryRun=False)

    def handleChangedTile(self,extraInfo=None):
        self.triggerCompletionCheck(self.character,dryRun=False)

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.handleChangedTerrain, "changedTerrain")
        self.startWatching(character,self.handleChangedTile, "changedTile")
        super().assignToCharacter(character)


    def handleQuestFailure(self,extraParam):
        '''
        react to a subquest failing
        '''

        # ensure the quest is actually active
        if extraParam["quest"] not in self.subQuests:
            return

        # remove failed quest
        self.subQuests.remove(extraParam["quest"])

        # clear the path to target
        if extraParam["reason"] and "no path found" in extraParam["reason"]:
            if extraParam["quest"].idleMovement:
                return
            quest = src.quests.questMap["ClearPathToPosition"](targetPosition=extraParam["quest"].targetPosition)
            self.addQuest(quest)
            self.startWatching(quest,self.handleQuestFailure,"failed")
            return

        # fail recursively
        self.fail(extraParam["reason"])

src.quests.addType(GoToTerrain)

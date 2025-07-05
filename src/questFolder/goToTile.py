import random

import src


class GoToTile(src.quests.MetaQuestSequence):
    '''
    quest to go to a certain tile

    Parameters:
        description: the description to be shown in the UI
        creator: the entitiy creating this quest (obsolete?)
        targetPosition: the position to go to
        lifetime: how long the quest will stay valid
        paranoid: be very carful
        showCoordinates: unclear (obsolete?)
        reason: the reason for assigning the quest shown in the UI
        abortHealthPercentage: abort quest on this threshold
        story: optional story text for the description
        allowMapMenu: allow solver to use the map menu
    '''
    type = "GoToTile"
    def __init__(self, description="go to tile", creator=None, targetPosition=None, lifetime=None, paranoid=False, showCoordinates=True,reason=None,abortHealthPercentage=0, story=None, allowMapMenu=True):
        if targetPosition:
            if targetPosition[0] < 1 or targetPosition[0] > 13:
                raise ValueError(f"target position {targetPosition} out of range")
            if targetPosition[1] < 1 or targetPosition[1] > 13:
                raise ValueError(f"target position {targetPosition} out of range")

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
        self.story = story
        self.allowMapMenu = allowMapMenu

    def handleChangedTile(self):
        '''
        handle the charactar having moved from tile to tile
        '''
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
        '''
        handle the character having moved
        '''
        if not self.active:
            return

        if self.completed:
            1/0

        if not self.character:
            return

        #self.generateSubquests(self.character)

    def getQuestMarkersTile(self,character):
        '''
        return quest markers for the minimap
        '''
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
        '''
        assign quest to character
        '''
        if self.character:
            return None

        self.startWatching(character,self.handleChangedTile, "changedTile")
        self.startWatching(character,self.handleMoved, "moved")

        return super().assignToCharacter(character)

    def generateTextDescription(self):
        '''
        generate a description of this quest
        '''
        reason = ""
        if self.reason:
            reason = f", to {self.reason}"
        storyString = ""
        if self.story:
            storyString = f"{self.story}"

        text = f"""{storyString}
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
        '''
        check if the quest is completed and end it
        '''
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
        '''
        check if path is still ok
        '''
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
        '''
        generate the next step towards solving the quest
        '''

        # do nothing on weird state
        if character is None:
            return (None,None)

        # validate the boundaries
        if self.targetPosition[0] < 1 or self.targetPosition[0] > 13:
            if not dryRun:
                self.fail("target position out of range")
            return (None,None)
        if self.targetPosition[1] < 1 or self.targetPosition[1] > 13:
            if not dryRun:
                self.fail("target position out of range")
            return (None,None)

        # move using the room menu
        if character.macroState["submenue"] and isinstance(character.macroState["submenue"],src.menuFolder.mapMenu.MapMenu) and not ignoreCommands:
            if self.targetPosition == (7,7,0):
                return (None,("c","auto move to tile"))

            submenue = character.macroState["submenue"]
            command = ""
            if submenue.cursor[0] > self.targetPosition[0]:
                command += "a"*(submenue.cursor[0]-self.targetPosition[0])
            if submenue.cursor[0] < self.targetPosition[0]:
                command += "d"*(self.targetPosition[0]-submenue.cursor[0])
            if submenue.cursor[1] > self.targetPosition[1]:
                command += "w"*(submenue.cursor[1]-self.targetPosition[1])
            if submenue.cursor[1] < self.targetPosition[1]:
                command += "s"*(self.targetPosition[1]-submenue.cursor[1])
            command += "j"
            return (None,(command,"auto move to tile"))

        # close other menus
        if not ignoreCommands and character.macroState.get("submenue"):
            return (None,(["esc"],"exit submenu"))

        # abort quest when too hurt
        if character.health < character.maxHealth*self.abortHealthPercentage:
            if not dryRun:
                self.fail("low health")
            return (None,None)

        # enter terrains properly
        bigPos = character.getBigPosition()
        if bigPos[0] == 0:
            return (None,("d","enter terrain"))
        if bigPos[0] == 14:
            return (None,("a","enter terrain"))
        if bigPos[1] == 0:
            return (None,("s","enter terrain"))
        if bigPos[1] == 14:
            return (None,("w","enter terrain"))

        # generate path
        if not self.path:
            self.generatePath(character)

        # do nothing on invalid path. (performance issue?)
        if not self.path:
            return (None,None)

        # open map menu
        if self.allowMapMenu and len(self.path) > 3:
            menuCommand = "g"
            if "runaction" in character.interactionState:
                menuCommand = ""

            if self.targetPosition == (7,7,0):
                return (None,(menuCommand+"mc","use fast travel to reach your destination"))
            currentPos = character.getBigPosition()
            offset = (self.targetPosition[0]-currentPos[0], self.targetPosition[1]-currentPos[1], 0)
            return (None,(menuCommand+"m"+"d"*offset[0]+"a"*(-offset[0])+"s"*offset[1]+"w"*(-offset[1])+"j","use fast travel to reach your destination"))

        # do nothing if there is a suqbquest
        if self.subQuests:
            return (None,None)

        # handle the actual movement
        if isinstance(character.container,src.rooms.Room):
            # TODO: reenable random

            # fight nearby enemies
            if not self.paranoid:
                if random.random() < 1.5 and "fighting" in self.character.skills:
                    for otherCharacter in character.container.characters:
                        if otherCharacter.faction == character.faction:
                            continue
                        quest = src.quests.questMap["Fight"]()
                        return ([quest],None)

                for otherCharacter in character.container.characters:
                    if otherCharacter.faction == character.faction:
                        continue
                    if character.health < character.maxHealth//5:
                        quest = src.quests.questMap["Flee"]()
                        return ([quest],None)
                    else:
                        quest = src.quests.questMap["Fight"]()
                        return ([quest],None)

            # check path and fail if appropriate
            if not self.isPathSane(character):
                self.generatePath(character)
                if not self.path:
                    if not dryRun:
                        self.fail()
                    return (None,None)

            # exit the room
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

            # fail if path was invalid
            if not dryRun:
                self.fail("invalid step in tile path")
            return (None,None)
        else:
            # actually enter the tile
            if character.xPosition%15 == 7 and character.yPosition%15 == 14:
                return (None,("w","enter the tile"))
            if character.xPosition%15 == 7 and character.yPosition%15 == 0:
                return (None,("s","enter the tile"))
            if character.xPosition%15 == 14 and character.yPosition%15 == 7:
                return (None,("a","enter the tile"))
            if character.xPosition%15 == 0 and character.yPosition%15 == 7:
                return (None,("d","enter the tile"))

            # fight nearby enemies
            # TODO: reenable random
            if not self.paranoid:
                if random.random() < 1.5 and "fighting" in self.character.skills:
                    if character.container.getEnemiesOnTile(character):
                        quest = src.quests.questMap["Fight"]()
                        return ([quest],None)

                    if character.container.getEnemiesOnTile(character):
                        if character.health < character.maxHealth//5:
                            quest = src.quests.questMap["Flee"]()
                            return ([quest],None)
                        else:
                            quest = src.quests.questMap["Fight"]()
                            return ([quest],None)

            # chack and regenerate path
            if not self.isPathSane(character):
                self.generatePath(character)
                if not self.path:
                    self.fail()
                    return (None,None)

            # go to tile edge
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

            # fail if path was invalid
            if not dryRun:
                self.fail("invalid step in tile path")
            return (None,None)

    def generatePath(self,character):
        '''
        generate a new path to the targets
        '''
        self.path = character.getTerrain().getPath(character.getBigPosition(),self.targetPosition,character=character,avoidEnemies=True,outsideOnly=character.outsideOnly)

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
            quest = src.quests.questMap["ClearPathToPosition"](targetPosition=extraParam["quest"].targetPosition)
            self.addQuest(quest)
            self.startWatching(quest,self.handleQuestFailure,"failed")
            return

        # call superclass
        self.fail(extraParam["reason"])

# register quest
src.quests.addType(GoToTile)

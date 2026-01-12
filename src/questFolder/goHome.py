import src

import random

class GoHome(src.quests.MetaQuestSequence):
    '''
    quest to go home
    '''
    type = "GoHome"
    def __init__(self, description="go home", creator=None, paranoid=False,reason=None,endOnHomeTerrain=False):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        self.baseDescription = description
        # save initial state and register
        self.type = "GoHome"
        self.addedSubQuests = False
        self.paranoid = paranoid
        self.reason = reason
        self.endOnHomeTerrain = endOnHomeTerrain

    def generateTextDescription(self):
        '''
        generate a textual description of this quest
        '''
        reason = ""
        if self.reason:
            reason = f", to {self.reason}"

        text = f"""
Go home{reason}.

You consider the command centre of the base your home.
That command centre holds the assimilator and
other important artworks like the quest artwork.

Many activities can be started from the command centre.
Go there and be ready for action.
"""
        try:
            self.endOnHomeTerrain
        except:
            self.endOnHomeTerrain = False
        if self.endOnHomeTerrain:
            text += "\nThis quest will end once you reach the home terrain."
        return text

    def triggerCompletionCheck(self, character=None, dryRun=True):
        '''
        check if the quest is completed
        '''
        if not character:
            return False

        if character.getTerrainPosition() != self.getHomeLocation():
            return False

        if self.endOnHomeTerrain:
            if not dryRun:
                self.postHandler()
            return True

        homeRoom = character.getHomeRoom()
        if homeRoom:
            if character.container == homeRoom:
                if not dryRun:
                    self.postHandler()
                return True
        else:
            if character.container.isRoom:
                if not dryRun:
                    self.postHandler()
                return True
        return False

    def wrapedTriggerCompletionCheck(self, extraInfo):
        '''
        indirection to call the actual fuction
        '''
        if not self.active:
            return
        self.reroll()

        self.triggerCompletionCheck(extraInfo[0],dryRun=False)

    def assignToCharacter(self, character):
        '''
        assign this quest to a character
        '''
        if self.character:
            return

        self.recalcDescription()

        self.startWatching(character,self.wrapedTriggerCompletionCheck, "moved")

        super().assignToCharacter(character)

    def getCityLocation(self):
        '''
        get the coordinate of where the city should be
        '''
        return (self.character.registers["HOMEx"],self.character.registers["HOMEy"],0)

    def getHomeLocation(self):
        '''
        get the coordinate of where the home terrain should be
        '''
        return (self.character.registers["HOMETx"],self.character.registers["HOMETy"],0)

    def recalcDescription(self):
        '''
        reset the description
        '''
        if self.character:
            cityLocation = self.getCityLocation()
            terrainLocation = self.getHomeLocation()
            self.metaDescription = self.baseDescription+f" {cityLocation[0]}/{cityLocation[1]} on {terrainLocation[0]}/{terrainLocation[1]}"

    def getNextStep(self, character=None, ignoreCommands=False, dryRun=True):
        '''
        get the next step towards solving the quest
        '''

        # handle weird edge cases
        if self.subQuests:
            return (None,None)
        if not character:
            return (None,None)

        # navigate menues
        submenue = character.macroState.get("submenue")
        if submenue and not ignoreCommands:
            if submenue.tag == "applyOptionSelection" and submenue.extraInfo.get("item").type == "Shrine":
                command = submenue.get_command_to_select_option("teleport")
                if command:
                    return (None,(command,"teleport home"))
            if submenue.tag not in ("advancedInteractionSelection",):
                return (None,(["esc"],"close menu"))

        # enter rooms/tiles properly
        if not character.container.isRoom:
            pos = character.getSpacePosition()
            if pos == (14,7,0):
                return (None,("a","enter room"))
            if pos == (0,7,0):
                return (None,("d","enter room"))
            if pos == (7,14,0):
                return (None,("w","enter room"))
            if pos == (7,0,0):
                return (None,("s","enter room"))
        if character.getBigPosition()[0] == 0:
            return (None, ("d","enter the terrain"))
        if character.getBigPosition()[0] == 14:
            return (None, ("a","enter the terrain"))
        if character.getBigPosition()[1] == 0:
            return (None, ("s","enter the terrain"))
        if character.getBigPosition()[1] == 14:
            return (None, ("w","enter the terrain"))

        # activate item when marked
        action = self.generate_confirm_interaction_command(allowedItems=["Shrine"])
        if action:
            return action

        # set up helper variables
        currentTerrain = character.getTerrain()

        if character.getTerrainPosition() != self.getHomeLocation():

            # find nearby shrine
            foundShrine = None
            if isinstance(character.container, src.rooms.Room):
                items = character.container.getItemsByType("Shrine")
                if items:
                    for item in items:
                        if character.getDistance(item.getPosition()) <= 1:

                            direction = "."
                            if character.getPosition(offset=(1, 0, 0)) == item.getPosition():
                                direction = "d"
                            if character.getPosition(offset=(-1, 0, 0)) == item.getPosition():
                                direction = "a"
                            if character.getPosition(offset=(0, 1, 0)) == item.getPosition():
                                direction = "s"
                            if character.getPosition(offset=(0, -1, 0)) == item.getPosition():
                                direction = "w"

                            interactionCommand = "J"
                            if submenue:
                                if submenue.tag == "advancedInteractionSelection":
                                    interactionCommand = ""
                                else:
                                    return (None,(["esc"],"close menu"))
                            return (None, (interactionCommand + direction, "activate the Shrine"))
                    foundShrine = items[0]
                    quest = src.quests.questMap["GoToPosition"](
                        targetPosition=foundShrine.getPosition(), reason="get to a shrine", ignoreEndBlocked=True
                    )
                    return ([quest], None)
                roomsToSearch = character.container.container.rooms
            else:
                roomsToSearch = character.container.rooms

            # teleport home
            for room in roomsToSearch:
                items = room.getItemsByType("Shrine")
                if not items:
                    continue
                foundShrine = items[0]
            if foundShrine:
                quest = src.quests.questMap["GoToTile"](
                    paranoid=self.paranoid, targetPosition=foundShrine.container.getPosition(), reason="get to a shrine"
                )
                return ([quest], None)

            # check for closest point to return
            candidates = []
            extraWeight = {}
            for x in range(1,14):
                for y in range(1,14):
                    coordinate = (x, y, 0)
                    extraWeight[coordinate] = 30000
                    if coordinate in character.terrainInfo:
                        info = character.terrainInfo[coordinate]
                        if coordinate == character.getHomeTerrain().getPosition():
                            extraWeight[coordinate] = 0
                        if info.get("tag") == "shrine":
                            extraWeight[coordinate] = 1
                    if coordinate == (7,7,0): # avoid endgame dungeon
                        extraWeight[coordinate] = 32000
                    candidates.append(coordinate)

            # sort nearest target candidate skewed by desirebility with slight random
            best_candidate = None
            best_distance = None
            current_pos = character.getTerrainPosition()
            for candidate in candidates:
                distance = src.helpers.distance_between_points(current_pos, candidate)
                distance += extraWeight[candidate]
                distance += random.random()
                if best_candidate is None or distance < best_distance:
                    print(best_distance)
                    best_distance = distance
                    best_candidate = candidate
            targetTerrain = best_candidate

            # move to selected target
            reason = "have to opportunity to teleport home"
            if targetTerrain == character.getHomeTerrain().getPosition():
                reason = "get home any way possible"
            quest = src.quests.questMap["GoToTerrain"](targetTerrain=targetTerrain,reason=reason)
            return ([quest], None)

        # workaround missing home rooms
        homeRoom = character.getHomeRoom()
        if not homeRoom:
            if currentTerrain.rooms:
                homeRoom = random.choice(currentTerrain.rooms)
            else:
                return self._solver_trigger_fail(dryRun,"no home")

        # make character go into the home room
        if character.getBigPosition() != homeRoom.getPosition():
            quest = src.quests.questMap["GoToTile"](
                paranoid=self.paranoid, targetPosition=homeRoom.getPosition(), reason="go to the command center"
            )
            return ([quest], None)

        # enter rooms properly
        charPos = (character.xPosition % 15, character.yPosition % 15, 0)
        move = ""
        if charPos in ((0, 7, 0), (0, 6, 0)):
            move = "d"
        if charPos in ((7, 14, 0), (6, 12, 0)):
            move = "w"
        if charPos in ((7, 0, 0), (6, 0, 0)):
            move = "s"
        if charPos in ((14, 7, 0), (12, 6, 0)):
            move = "a"
        if move != "":
            return (None, (move, "move into room"))

        # soft fail
        return (None, (".","stand around confused"))

    def getQuestMarkersTile(self, character):
        '''
        generate quest markers for this quest
        '''
        result = super().getQuestMarkersTile(character)
        if character.isOnHomeTerrain():
            result.append(((self.getCityLocation()[0],self.getCityLocation()[1]),"target"))
        return result

    def handleQuestFailure(self,extraParam):
        '''
        handle a subquest failing
        '''

        # set up helper variables
        quest = extraParam.get("quest")
        reason = extraParam.get("reason")

        if reason:
            if reason == "no tile path":
                self.fail(reason)
                return

        super().handleQuestFailure(extraParam)

# register the quest type
src.quests.addType(GoHome)

import src


class ScheduleRoomBuilding(src.quests.MetaQuestSequence):
    '''
    quest to schedule building a new room
    '''
    type = "ScheduleRoomBuilding"
    def __init__(self, description="schedule room building", creator=None, roomPosition=None,reason=None,priorityBuild=False):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        self.roomPosition = roomPosition
        self.reason = reason
        self.priorityBuild = priorityBuild

    def generateTextDescription(self):
        '''
        generate a description of the quest
        '''
        out = []
        reason = ""
        if self.reason:
            reason = f",\nto {self.reason}"
        text = f"""
Schedule a room to be built on tile{self.roomPosition}{reason}.

Use a CityPlaner to do this.

"""
        out.append(text)
        return out

    def getNextStep(self,character=None,ignoreCommands=False, dryRun = True):
        '''
        generate instructions on what to do next
        uses the city planer to schedule building a room
        '''

        # do nothing if there are subquests
        if self.subQuests:
            return (None,None)

        # fail on weird states
        terrain = character.getTerrain()
        if self.roomPosition in terrain.forests or self.roomPosition in terrain.scrapFields:
            return self._solver_trigger_fail(dryRun,"target position blocked")
        if terrain.getRoomByPosition(self.roomPosition):
            return self._solver_trigger_fail(dryRun,"room already build")

        # set up helper variables
        terrain = character.getTerrain()

        # navigate the build-menu and schedule building the room
        submenue = character.macroState["submenue"]
        if submenue and not ignoreCommands:

            # open map
            if submenue.tag == "applyOptionSelection":
                command = submenue.get_command_to_select_option("showMap")
                return (None,(command,"show the map"))

            # build the build site from map
            if isinstance(submenue,src.menuFolder.mapMenu.MapMenu) and not ignoreCommands:
                selection_command = "r"
                if self.priorityBuild:
                    selection_command = "R"
                command = submenue.get_command_to_select_position(coordinate=self.roomPosition,selectionCommand=selection_command)
                if command:
                    return (None,(command,"schedule building a room"))

        if not character.getTerrain() == character.getHomeTerrain():
            quest = src.quests.questMap["GoHome"](reason="get back to base")
            return  ([quest],None)

        terrain = character.getTerrain()
        for room in terrain.rooms:
            items = room.getItemsByType("CityPlaner",needsBolted=True)
            if not items:
                continue
            item = items[0]
            quest = src.quests.questMap["ActivateItem"](targetPosition=item.getPosition(),targetPositionBig=item.getBigPosition(),reason="get promoted")
            return ([quest],None)

        return self._solver_trigger_fail(dryRun,"no CityPlaner found")

    def triggerCompletionCheck(self,character=None,dryRun=True):
        '''
        check and end a quest if it is completed
        '''

        # abort on weird states
        if not character:
            return False

        # fetch the city planer
        terrain = character.getTerrain()
        for room in terrain.rooms:
            cityPlaner = room.getItemByType("CityPlaner")
            if cityPlaner:
                break
        if not cityPlaner:
            1/0
            return False

        # end the quest if room was planned
        if self.roomPosition in cityPlaner.plannedRooms:
            if not dryRun:
                self.postHandler()
            return True

        # continue working
        return False

    def handleScheduledRoom(self,extraParams):
        '''
        callback that ends this quest
        '''
        if self.completed:
            1/0
        if not self.active:
            return
        self.postHandler()

    def assignToCharacter(self, character):
        '''
        assign the quest to the character
        '''
        # ignore if character was already assigned
        if self.character:
            return None

        # start listening for the event indicating completion
        self.startWatching(character,self.handleScheduledRoom, "scheduled room")

        # call superclass
        return super().assignToCharacter(character)

    def getQuestMarkersSmall(self,character,renderForTile=False):
        '''
        return the quest markers for the normal map
        '''
        if isinstance(character.container,src.rooms.Room):
            if renderForTile:
                return []
        else:
            if not renderForTile:
                return []

        result = super().getQuestMarkersSmall(character,renderForTile=renderForTile)
        if not renderForTile:
            if isinstance(character.container,src.rooms.Room):
                for item in character.container.getItemsByType("CityPlaner"):
                    result.append((item.getPosition(),"target"))
        return result

    def getQuestMarkersTile(self,character):
        result = super().getQuestMarkersTile(character)
        result.append(((self.roomPosition[0],self.roomPosition[1]),"target"))
        return result

# register quest
src.quests.addType(ScheduleRoomBuilding)

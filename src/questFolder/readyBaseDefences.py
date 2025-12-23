import src


class ReadyBaseDefences(src.quests.MetaQuestSequence):
    type = "ReadyBaseDefences"

    def __init__(self, description="ready base defences", creator=None, reason=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        self.reason = reason

    def triggerCompletionCheck(self,character=None,dryRun=True):
        if not character:
            return False

        terrain = character.getTerrain()

        if not terrain.alarm:
            return False
        for room in terrain.rooms:
            if not room.getItemsByType("AlarmBell"):
                continue
            if room.alarm:
                continue
            return False

        if not dryRun:
            self.postHandler()
        return True

    def getNextStep(self,character,ignoreCommands=False,dryRun=True):

        # handle weird edge cases
        if self.subQuests:
            return (None,None)
        
        # set up helper variables
        terrain = character.getTerrain()

        # navigate menues
        submenue = character.macroState.get("submenue")
        if submenue and not ignoreCommands:
            if submenue.tag == "applyOptionSelection" and submenue.extraInfo.get("item").type == "SiegeManager":
                if terrain.alarm == False:
                    menuEntry = ("restrict outside","enable the outside restrictions")
                else:
                    menuEntry = ("soundAlarms","sound the alarms")

                command = submenue.get_command_to_select_option(menuEntry[0])
                if command:
                    return (None,(command,menuEntry[1]))
            return (None,(["esc"],"to close menu"))

        # activate production item when marked
        if character.macroState.get("itemMarkedLast"):
            item = character.macroState["itemMarkedLast"]
            if item.type == "SiegeManager":
                return (None,("j","activate SiegeManager"))
            else:
                return (None,(".","undo selection"))

        siegeManager = None
        for room in terrain.rooms:
            item = room.getItemByType("SiegeManager",needsBolted=True)
            if not item:
                continue
            
            siegeManager = item

        if not siegeManager:
            return self._solver_trigger_fail(dryRun,"no siege manager")

        if character.getBigPosition() != siegeManager.container.getPosition():
            quest = src.quests.questMap["GoToTile"](targetPosition=siegeManager.container.getPosition(),description="go to the command centre",reason="to reach the SiegeManager")
            return ([quest],None)

        if character.getDistance(siegeManager.getPosition()) > 1:
            quest = src.quests.questMap["GoToPosition"](targetPosition=siegeManager.getPosition(),ignoreEndBlocked=True,description="go to the SiegeManager",reason="to be able to activate the SiegeManager")
            return ([quest],None)
        
        target_pos = siegeManager.getPosition()
        pos = character.getPosition()
        direction = "."
        if (pos[0]-1,pos[1],pos[2]) == target_pos:
            direction = "a"
        if (pos[0]+1,pos[1],pos[2]) == target_pos:
            direction = "d"
        if (pos[0],pos[1]-1,pos[2]) == target_pos:
            direction = "w"
        if (pos[0],pos[1]+1,pos[2]) == target_pos:
            direction = "s"

        interactionCommand = "J"
        if "advancedInteraction" in character.interactionState:
            interactionCommand = ""
        if terrain.alarm == False:
            return (None,(interactionCommand+direction+"j","enable the outside restrictions"))
        return (None,(interactionCommand+direction+"ssj","sound the alarms"))

    def generateTextDescription(self):
        reasonString = ""
        if self.reason:
            reasonString = ", to "+self.reason
        text = [f"""
Prepare the base for an attack{reasonString}.
"""]
        return text

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
                for item in character.container.itemsOnFloor:
                    if not item.type == "SiegeManager":
                        continue
                    if not item.bolted:
                        continue
                    result.append((item.getPosition(),"target"))
        return result

src.quests.addType(ReadyBaseDefences)

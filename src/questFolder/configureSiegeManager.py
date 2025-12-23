import src


class ConfigureSiegeManager(src.quests.MetaQuestSequence):
    '''
    a quest to configure the siege manager with a typical configuration
    '''
    type = "ConfigureSiegeManager"
    def __init__(self, description="configure siege manager", creator=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description

    def triggerCompletionCheck(self,character=None,dryRun=True):
        '''
        check if the quest can be considered completed and end the quest if is can be considered completed
        '''

        # abort on weird states
        if not character:
            return False
        
        # get siege manager
        terrain = character.getTerrain()
        siegeManager = None
        for room in terrain.rooms:
            item = room.getItemByType("SiegeManager",needsBolted=True)
            if not item:
                continue
            siegeManager = item

        # abort if no siege manager was found
        if not siegeManager:
            return False

        # get the actions already scheduled
        existingActions = []
        for scheduledAction in siegeManager.getActionList():
            existingActions.append(scheduledAction[2]["type"])

        # check if the needed actions were scheduled
        if "restrict outside" not in existingActions:
            return False
        if "sound alarms" not in existingActions:
            return False
        if "unrestrict outside" not in existingActions:
            return False
        if "silence alarms" not in existingActions:
            return False

        # end the quest
        if not dryRun:
            self.postHandler()
        return True

    def getNextStep(self,character,ignoreCommands=False,dryRun=True):
        '''
        calculate the next step to do to solve this quest
        '''

        # do nothing if there is a subquest
        if self.subQuests:
            return (None,None)
        
        # get siege manager
        terrain = character.getTerrain()
        siegeManager = None
        for room in terrain.rooms:
            item = room.getItemByType("SiegeManager",needsBolted=True)
            if not item:
                continue
            siegeManager = item

        # handle open menues
        submenue = character.macroState.get("submenue")
        if submenue:

            # open the scheduling menu
            if submenue.tag == "applyOptionSelection" and submenue.extraInfo.get("item").type == "SiegeManager":
                command = submenue.get_command_to_select_option("setSchedule")
                if command:
                    return (None,(command,"open the scheduling menu"))

            # navigate the scheduling menu
            if submenue.tag == "configure siege manager main":
                actionList = siegeManager.getActionList()
                if actionList:

                    # get the basic data
                    scheduledAction = actionList[submenue.followUp["params"]["cursor"]]
                    upperTarget = 2800
                    lowerTarget = 1500
                    tick = scheduledAction[1]
                    command = None

                    # determine where to move the cursor to
                    target = None
                    if scheduledAction[2]["type"] == "restrict outside":
                        target = upperTarget
                    if scheduledAction[2]["type"] == "sound alarms":
                        target = upperTarget
                    if scheduledAction[2]["type"] == "unrestrict outside":
                        target = lowerTarget
                    if scheduledAction[2]["type"] == "silence alarms":
                        target = lowerTarget

                    # get keystrokes to move slider to the right place
                    if target:
                        if tick <= target-250:
                            jommand = "D"
                            description = "move the event left 250 ticks"
                        elif tick <= target-100:
                            command = "E"
                            description = "move the event left 100 ticks"
                        elif tick <= target-10:
                            command = "e"
                            description = "move the event left 10 ticks"
                        elif tick <= target-1:
                            command = "d"
                            description = "move the event left 1 ticks"
                        if tick >= target+250:
                            command = "A"
                            description = "move the event right 250 ticks"
                        elif tick >= target+100:
                            command = "Q"
                            description = "move the event right 100 ticks"
                        elif tick >= target+10:
                            command = "q"
                            description = "move the event right 10 ticks"
                        elif tick >= target+1:
                            command = "a"
                            description = "move the event right 1 ticks"

                    # run the keystrokes to move slider to the right place
                    if command:
                        return (None,(command,description))

                # open the menu to schedule a new action
                command = "c"
                return (None,(command,"add a new action"))

            # select the action to configure
            if submenue.tag == "configure siege manager task selection":
                existingActions = []
                for scheduledAction in siegeManager.getActionList():
                    existingActions.append(scheduledAction[2]["type"])

                desiredActions = ["restrict outside","sound alarms","unrestrict outside","silence alarms"]

                toSelect = None
                for desiredAction in desiredActions:
                    if desiredAction not in existingActions:
                        toSelect = desiredAction
                        break

                command = submenue.get_command_to_select_option(toSelect)
                if command:
                    return (None,(command,"add "+toSelect+" action"))

            # close generic menues
            return (None,(["esc"],"to close menu"))

        # do nothing if no siege manager was found
        if not siegeManager:
            return self._solver_trigger_fail(dryRun,"no siege manager")

        # go to the tile the siege manager is on
        if character.getBigPosition() != siegeManager.container.getPosition():
            quest = src.quests.questMap["GoToTile"](targetPosition=siegeManager.container.getPosition(),description="go to the command centre",reason="to reach the SiegeManager")
            return ([quest],None)

        # go to the siege manager
        if character.getDistance(siegeManager.getPosition()) > 1:
            quest = src.quests.questMap["GoToPosition"](targetPosition=siegeManager.getPosition(),ignoreEndBlocked=True,description="go to the SiegeManager",reason="to be able to activate the SiegeManager")
            return ([quest],None)
        
        # get the direction the siege manager is in
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

        # generate the actual command to start using the siege manager
        interactionCommand = "J"
        if "advancedInteraction" in character.interactionState:
            interactionCommand = ""
        return (None,(interactionCommand+direction,"open the configuration menu"))

    def generateTextDescription(self):
        '''
        generate text description
        '''
        text = ["""
Waves of enemies appear at the start of each epoch.
Handling those repeating waves can be automated.

The siege manager allows to do actions at certain points in time.

For example the alarms can always be rang 1000 ticks before the epoch ends.
That should ensure all Clones are safe when the waves comes ate the end of the epoch.
The alarms can automatically turned off 1000 ticks into the epoch.
At that point the wave should be dead and the NPC are safe to go outside.

Configure the siege manager to defend against the waves.
You can set any trigger times for the actions as long the actions scheduled.
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

# register the quest
src.quests.addType(ConfigureSiegeManager)

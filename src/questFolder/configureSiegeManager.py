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

    def triggerCompletionCheck(self,character=None):
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
            if submenue.tag == None:
                menuEntry = "setSchedule"
                counter = 1
                for option in submenue.options.values():
                    if option == menuEntry:
                        index = counter
                        break
                    counter += 1
                command = ""
                if submenue.selectionIndex > counter:
                    command += "w"*(submenue.selectionIndex-counter)
                if submenue.selectionIndex < counter:
                    command += "s"*(counter-submenue.selectionIndex)
                command += "j"
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

                    # get keystrokes to move slider to the right place
                    if scheduledAction[2]["type"] == "restrict outside":
                        if tick <= upperTarget-250:
                            command = "D"
                        elif tick <= upperTarget-100:
                            command = "E"
                        elif tick <= upperTarget-10:
                            command = "e"
                        elif tick <= upperTarget-1:
                            command = "d"
                        if tick >= upperTarget+250:
                            command = "A"
                        elif tick >= upperTarget+100:
                            command = "Q"
                        elif tick >= upperTarget+10:
                            command = "q"
                        elif tick >= upperTarget+1:
                            command = "a"

                    # get keystrokes to move slider to the right place
                    if scheduledAction[2]["type"] == "sound alarms":
                        if tick <= upperTarget-250:
                            command = "D"
                        elif tick <= upperTarget-100:
                            command = "E"
                        elif tick <= upperTarget-10:
                            command = "e"
                        elif tick <= upperTarget-1:
                            command = "d"
                        if tick >= upperTarget+250:
                            command = "A"
                        elif tick >= upperTarget+100:
                            command = "Q"
                        elif tick >= upperTarget+10:
                            command = "q"
                        elif tick >= upperTarget+1:
                            command = "a"

                    # get keystrokes to move slider to the right place
                    if scheduledAction[2]["type"] == "unrestrict outside":
                        if tick <= lowerTarget-250:
                            command = "D"
                        elif tick <= lowerTarget-100:
                            command = "E"
                        elif tick <= lowerTarget-10:
                            command = "e"
                        elif tick <= lowerTarget-1:
                            command = "d"
                        if tick >= lowerTarget+250:
                            command = "A"
                        elif tick >= lowerTarget+100:
                            command = "Q"
                        elif tick >= lowerTarget+10:
                            command = "q"
                        elif tick >= lowerTarget+1:
                            command = "a"

                    # get keystrokes to move slider to the right place
                    if scheduledAction[2]["type"] == "silence alarms":
                        if tick <= lowerTarget-250:
                            command = "D"
                        elif tick <= lowerTarget-100:
                            command = "E"
                        elif tick <= lowerTarget-10:
                            command = "e"
                        elif tick <= lowerTarget-1:
                            command = "d"
                        if tick >= lowerTarget+250:
                            command = "A"
                        elif tick >= lowerTarget+100:
                            command = "Q"
                        elif tick >= lowerTarget+10:
                            command = "q"
                        elif tick >= lowerTarget+1:
                            command = "a"

                    # run the keystrokes to move slider to the right place
                    if command:
                        return (None,(command,"select when the action should happen"))

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

                menuEntry = toSelect
                counter = 1
                for option in submenue.options.values():
                    if option == menuEntry:
                        index = counter
                        break
                    counter += 1
                command = ""
                if submenue.selectionIndex > counter:
                    command += "w"*(submenue.selectionIndex-counter)
                if submenue.selectionIndex < counter:
                    command += "s"*(counter-submenue.selectionIndex)
                command += "j"
                return (None,(command,"add "+toSelect+" action"))

            # close generic menues
            return (None,(["esc"],"to close menu"))

        # do nothing if no siege manager was found
        if not siegeManager:
            if not dryRun:
                self.fail("no siege manager")
            return (None,None)

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
        return (None,(interactionCommand+direction+"sssssj","open the configuration menu"))

    def generateTextDescription(self):
        '''
        generate text description
        '''
        text = ["""
configure the siege manager
"""]
        return text

# register the quest
src.quests.addType(ConfigureSiegeManager)

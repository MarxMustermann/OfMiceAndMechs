import src


class ConfigureSiegeManager(src.quests.MetaQuestSequence):
    type = "ConfigureSiegeManager"

    def __init__(self, description="configure siege manager", creator=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description

    def triggerCompletionCheck(self,character=None):
        if not character:
            return False
        
        terrain = character.getTerrain()
        siegeManager = None
        for room in terrain.rooms:
            item = room.getItemByType("SiegeManager",needsBolted=True)
            if not item:
                continue
            
            siegeManager = item

        if not siegeManager:
            return False

        existingActions = []
        for actionDefintion in siegeManager.schedule.values():
            existingActions.append(actionDefintion["type"])

        if "restrict outside" not in existingActions:
            return False
        if "sound alarms" not in existingActions:
            return False
        if "unrestrict outside" not in existingActions:
            return False
        if "silence alarms" not in existingActions:
            return False

        self.postHandler()
        return True

    def getNextStep(self,character,ignoreCommands=False,dryRun=True):
        if self.subQuests:
            return (None,None)
        
        terrain = character.getTerrain()
        siegeManager = None
        for room in terrain.rooms:
            item = room.getItemByType("SiegeManager",needsBolted=True)
            if not item:
                continue
            
            siegeManager = item

        submenue = character.macroState.get("submenue")
        if submenue:
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

            if submenue.tag == "configure siege manager main":
                menuEntry = "add"
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
                return (None,(command,"add a new action"))

            if submenue.tag == "configure siege manager task selection":
                existingActions = []
                for actionDefintion in siegeManager.schedule.values():
                    existingActions.append(actionDefintion["type"])

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
            if submenue.tag == "configure siege manager time selection":
                targetValue = 0
                if submenue.followUp["params"].get("actionType") == "restrict outside":
                    targetValue = 2800
                if submenue.followUp["params"].get("actionType") == "sound alarms":
                    targetValue = 2801
                if submenue.followUp["params"].get("actionType") == "unrestrict outside":
                    targetValue = 1500
                if submenue.followUp["params"].get("actionType") == "silence alarms":
                    targetValue = 1501
                
                if submenue.value <= targetValue-100:
                    return (None,( "D",f"move the slider to tick {targetValue}"))
                if submenue.value <= targetValue-10:
                    return (None,( "d",f"move the slider to tick {targetValue}"))
                if submenue.value <= targetValue-1:
                    return (None,( ["right"],f"move the slider to tick {targetValue}"))
                if submenue.value >= targetValue+100:
                    return (None,( "A",f"move the slider to tick {targetValue}"))
                if submenue.value >= targetValue+10:
                    return (None,( "a",f"move the slider to tick {targetValue}"))
                if submenue.value >= targetValue+1:
                    return (None,( ["left"],f"move the slider to tick {targetValue}"))
                return (None,( ["enter"],"actually schedule the action"))
            return (None,(["esc"],"to close menu"))

        if not siegeManager:
            if not dryRun:
                self.fail("no siege manager")
            return (None,None)

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
        return (None,(interactionCommand+direction+"sssssj","open the configuration menu"))

    def generateTextDescription(self):
        text = ["""
configure the siege manager
"""]
        return text


src.quests.addType(ConfigureSiegeManager)

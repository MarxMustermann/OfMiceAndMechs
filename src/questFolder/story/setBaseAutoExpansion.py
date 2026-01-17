import src


class SetBaseAutoExpansion(src.quests.MetaQuestSequence):
    '''
    quest to set the amount of rooms the NPCs should build automatically
    '''
    type = "SetBaseAutoExpansion"
    def __init__(self, description="set base expansion parameter", creator=None, targetLevel=2, reason=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        self.targetLevel = targetLevel
        self.reason = reason

    def triggerCompletionCheck(self,character=None, dryRun=True):
        '''
        check and end quest if completed
        '''
        if not character:
            return False

        foundCityPlaner = None
        for room in character.getTerrain().rooms:
            items = room.getItemsByType("CityPlaner",needsBolted=True)
            if not items:
                continue
            foundCityPlaner = items[0]
            break

        if foundCityPlaner:
            if foundCityPlaner.autoExtensionThreashold:
                if not dryRun:
                    self.postHandler()
                return True
        
        return False

    def getNextStep(self,character,ignoreCommands=False,dryRun=True):
        '''
        generate next step towards solving the quest
        '''
        if self.subQuests:
            return (None,None)
        
        if character.macroState["submenue"] and not ignoreCommands:
            submenue = character.macroState["submenue"]
            if submenue.tag == "configurationSelection":
                return (None,("a","to select configuring the auto extension threashold"))
            if submenue.tag == "autoExtensionThreasholdInput":
                if submenue.text == str(self.targetLevel):
                    return (None,(["enter"],"to set the auto extension threashold"))

                if len(submenue.text) > len(str(self.targetLevel)):
                    return (None,(["backspace"],"remove input"))

                counter = 0
                while counter < len(submenue.text):
                    if submenue.text[counter] != str(self.targetLevel)[counter]:
                        return (None,(["backspace"],"remove input"))
                    counter += 1

                return (None,(str(self.targetLevel),"to enter the auto extension threashold"))

            return (None,(["esc"],"to close menu"))
        
        terrain = character.getTerrain()
        cityPlaner = None
        for room in terrain.rooms:
            item = room.getItemByType("CityPlaner",needsBolted=True)
            if not item:
                continue
            
            cityPlaner = item
            break

        if not cityPlaner:
            return self._solver_trigger_fail(dryRun,"no city planer")

        if character.getBigPosition() != cityPlaner.container.getPosition():
            quest = src.quests.questMap["GoToTile"](targetPosition=cityPlaner.container.getPosition(),description="go to the command centre",reason="to reach the CityPlaner")
            return ([quest],None)

        if character.getDistance(cityPlaner.getPosition()) > 1:
            quest = src.quests.questMap["GoToPosition"](targetPosition=cityPlaner.getPosition(),ignoreEndBlocked=True,description="go to the CityPlaner",reason="to be able to activate the CityPlaner")
            return ([quest],None)
        
        target_pos = cityPlaner.getPosition()
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

        interactionCommand = "C"
        if "advancedConfigure" in character.interactionState:
            interactionCommand = ""
        return (None,(list(interactionCommand+direction+"a"+"2")+["enter"],"disable the outside restrictions"))

    def generateTextDescription(self):
        '''
        generate a text description to show on the UI
        '''
        reason_string = ""
        if self.reason:
            reason_string = f", to {self.reason}"

        text = [f"""
Configure the base expansion threashold{reason_string}.

To set up new production lines or facilities a base needs empty rooms.
Clones can ensure there are always new rooms to build it.

The city planner has a entry that determines how many empty rooms there should be.
If there are less empty rooms than that entry indicates the NPC will start building a new room.
You will not designate build sites for that.
"""]
        return text

# register quest type
src.quests.addType(SetBaseAutoExpansion)

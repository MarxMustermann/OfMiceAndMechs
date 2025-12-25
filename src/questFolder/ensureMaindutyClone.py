import src


class EnsureMaindutyClone(src.quests.MetaQuestSequence):
    '''
    a quest to ensure 
    '''
    type = "EnsureMaindutyClone"
    def __init__(self, description="ensure duty", creator=None, dutyType="cleaning"):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = f"ensure {dutyType} duty"
        self.dutyType = dutyType

    def triggerCompletionCheck(self,character=None,dryRun=True):
        '''
        check if the quest can be considered completed and end the quest if is can be considered completed
        '''

        # abort on weird states
        if not character:
            return False
        
        # ensure at least one Clone has the required duty as highest prio
        foundClone = False
        for candidate in character.getTerrain().getAllCharacters():
            if not candidate.faction == character.faction:
                continue
            if candidate == character:
                continue
            if not candidate.duties:
                continue
            if not self.dutyType in candidate.duties:
                continue
            duty_priority = candidate.dutyPriorities.get(self.dutyType,1)
            if duty_priority == 1 and len(candidate.duties) > 1:
                continue
            not_highest = False
            for (check_duty,check_priority) in candidate.dutyPriorities.items():
                if check_duty == self.dutyType:
                    continue
                if check_priority >= duty_priority:
                    not_highest = True
            if not_highest:
                continue
            print(candidate.name)
            foundClone = True
        if not foundClone:
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
        dutyArtwork = None
        for room in terrain.rooms:
            item = room.getItemByType("DutyArtwork",needsBolted=True)
            if not item:
                continue
            dutyArtwork = item

        # fail if no character is available
        found_npc = None
        for check_character in terrain.getAllCharacters():
            if check_character == character:
                continue
            if check_character.faction != character.faction:
                continue
            if check_character.burnedIn:
                continue
            found_npc = character
        if not found_npc:
            return self._solver_trigger_fail(dryRun,"no suitable clone found")

        # handle open menues
        submenue = character.macroState.get("submenue")
        if submenue:

            # open the duty menu
            if submenue.tag == "applyOptionSelection":
                menuEntry = "showMatrix"
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
                return (None,(command,"open the duty menu"))

            # navigate the duty menu
            if isinstance(submenue,src.menuFolder.jobAsMatrixMenu.JobAsMatrixMenu):
                if submenue.index[0] > -1:
                    return (None,("w","move cursor to duty line"))

                command = None
                counter = -1
                for duty in submenue.get_duties():
                    counter += 1
                    if duty != self.dutyType:
                        continue
                    if counter == submenue.index[1]:
                        command = "j"
                        return (None,(command,"increase duty priority"))
                    elif counter < submenue.index[1]:
                        command = "a"
                        return (None,(command,"move cursor left"))
                    else:
                        command = "d"
                        return (None,(command,"move cursor right"))
                    break

                return self._solver_trigger_fail(dryRun,"duty not found")

            # close generic menues
            return (None,(["esc"],"to close menu"))

        # do nothing if no duty artwork was found
        if not dutyArtwork:
            return self._solver_trigger_fail(dryRun,"no duty artwork")

        # go to the tile the duty artwork is on
        if character.getBigPosition() != dutyArtwork.container.getPosition():
            quest = src.quests.questMap["GoToTile"](targetPosition=dutyArtwork.container.getPosition(),description="go to the command centre",reason="to reach the DutyArtwork")
            return ([quest],None)

        # go to the siege manager
        if character.getDistance(dutyArtwork.getPosition()) > 1:
            quest = src.quests.questMap["GoToPosition"](targetPosition=dutyArtwork.getPosition(),ignoreEndBlocked=True,description="go to the DutyArtwork",reason="to be able to activate the DutyArtwork")
            return ([quest],None)
        
        # get the direction the duty artwork is in
        target_pos = dutyArtwork.getPosition()
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
        return (None,(interactionCommand+direction+"j","open the configuration menu"))

    def generateTextDescription(self):
        '''
        generate text description
        '''
        text = [f"""
Ensure at least one Clone has {self.dutyType} as highest duty.
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
                    if not item.type == "DutyArtwork":
                        continue
                    if not item.bolted:
                        continue
                    result.append((item.getPosition(),"target"))
        return result

# register the quest
src.quests.addType(EnsureMaindutyClone)

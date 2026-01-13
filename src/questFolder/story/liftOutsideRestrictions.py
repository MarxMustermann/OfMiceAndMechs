import src


class LiftOutsideRestrictions(src.quests.MetaQuestSequence):
    type = "LiftOutsideRestrictions"

    def __init__(self, description="lift outside restrictions", creator=None, reason=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        self.reason = reason

    def handleSiegeDisabled(self, extraInfo):
        self.postHandler()

    def assignToCharacter(self, character):
        if self.character:
            return None

        self.startWatching(character,self.handleSiegeDisabled, "did unrestricted outside")

        return super().assignToCharacter(character)

    def triggerCompletionCheck(self,character=None,dryRun=True):
        if not character:
            return False

        terrain = character.getTerrain()
        if not terrain.alarm:
            if not dryRun:
                self.postHandler()
            return True
        
        return False

    def getNextStep(self,character,ignoreCommands=False,dryRun=True):
        if self.subQuests:
            return (None,None)
        
        submenue = character.macroState.get("submenue")
        if submenue and not ignoreCommands:
            if isinstance(submenue,src.menuFolder.selectionMenu.SelectionMenu):
                foundOption = False
                rewardIndex = 0
                if rewardIndex == 0:
                    counter = 1
                    for option in submenue.options.items():
                        if option[1] == "unrestrict outside":
                            foundOption = True
                            break
                        counter += 1
                    rewardIndex = counter

                if not foundOption:
                    return (None,(["esc"],"to close menu"))

                offset = rewardIndex-submenue.selectionIndex
                command = ""
                if offset > 0:
                    command += "s"*offset
                else:
                    command += "w"*(-offset)
                command += "j"
                return (None,(command,"contact command"))
            
            if submenue.tag not in ("advancedInteractionSelection",):
                return (None,(["esc"],"to close menu"))

        # activate production item when marked
        action = self.generate_confirm_interaction_command(allowedItems=["SiegeManager"])
        if action:
            return action
        
        terrain = character.getTerrain()
        siegeManager = None
        for room in terrain.rooms:
            item = room.getItemByType("SiegeManager",needsBolted=True)
            if not item:
                continue
            
            siegeManager = item

        if not siegeManager:
            return self._solver_trigger_fail(dryRun,"no siege manager")

        if character.getBigPosition() != siegeManager.container.getPosition():
            quest = src.quests.questMap["GoToTile"](targetPosition=siegeManager.container.getPosition(),description="go to the command centre",reason="reach the SiegeManager")
            return ([quest],None)

        if character.getDistance(siegeManager.getPosition()) > 1:
            quest = src.quests.questMap["GoToPosition"](targetPosition=siegeManager.getPosition(),ignoreEndBlocked=True,description="go to the SiegeManager",reason="be able to activate the SiegeManager")
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
        if submenue:
            if submenue.tag == "advancedInteractionSelection":
                interactionCommand = ""
            else:
                return (None,(["esc"],"close menu"))
        return (None,(interactionCommand+direction,"disable the outside restrictions"))

    def generateTextDescription(self):
        reasonSring = ""
        if self.reason:
            reasonSring = f", {self.reasonString}"
        text = [f"""
There are many enemies left outside the base{reasonSring}.
But all enemies left will only attack when somebody enters the tile they are on.
So they can be easily avoided by you and your clone.

This means that the restriction of the outside movement can be lifted now.
Use the SiegeManager to lift the restriction of the outside movement.
Once you do that, your clone will start to gather scrap and to produce items.
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

src.quests.addType(LiftOutsideRestrictions)

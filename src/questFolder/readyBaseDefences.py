import src


class ReadyBaseDefences(src.quests.MetaQuestSequence):
    type = "ReadyBaseDefences"

    def __init__(self, description="ready base defences", creator=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description

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
        if self.subQuests:
            return (None,None)
        
        terrain = character.getTerrain()

        if character.macroState["submenue"] and isinstance(character.macroState["submenue"],src.menuFolder.selectionMenu.SelectionMenu) and not ignoreCommands:
            submenue = character.macroState["submenue"]

            if not submenue.extraInfo.get("item"):
                return (None,(["esc"],"exit submenu"))

            if terrain.alarm == False:
                menuEntry = "restrict outside"
            else:
                menuEntry = "soundAlarms"

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

            if terrain.alarm == False:
                return (None,(command,"enable the outside restrictions"))
            else:
                return (None,(command,"sound the alarms"))

        if character.macroState["submenue"] and not ignoreCommands:
            return (None,(["esc"],"to close menu"))

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
        text = ["""
Prepare the base for an attack.
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

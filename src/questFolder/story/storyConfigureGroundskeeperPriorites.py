import src


class StoryConfigureGroundskeeperPriorites(src.quests.MetaQuestSequence):
    type = "StoryConfigureGroundskeeperPriorites"
    def __init__(self, description="configure groundskeeper priorities", creator=None, lifetime=None):
        questList = []
        super().__init__(questList, creator=creator, lifetime=lifetime)
        self.metaDescription = description

    def triggerCompletionCheck(self,character=None,dryRun=True):
        '''
        checks if the quest has completed
        '''
        if not character:
            return False
        keeper = self.getGroundsKeeper()
        if keeper and keeper.dutyPriorities.get("scrap hammering",0) < 3:
            if not dryRun:
                self.postHandler()
            return True
        return False

    def getGroundsKeeper(self):
        '''
        get the groundskeeper NPC
        '''
        keeper = None
        terrain = self.character.getHomeTerrain()
        for candidate in terrain.getAllCharacters():
            if not isinstance(candidate,src.characters.characterMap["GroundsKeeper"]):
                continue
            keeper = candidate
        return keeper

    def getNextStep(self,character,ignoreCommands=False,dryRun=True):
        '''
        calculate the next step towards solving the quest
        '''

        # no actions with sub quests
        if self.subQuests:
            return (None,None)

        # find the groundskeeper
        keeper = self.getGroundsKeeper()
        if not keeper:
            return self._solver_trigger_fail(dryRun,"keeper not found")
        keeper_position = keeper.getBigPosition()

        # take care of enemies
        if character.getNearbyEnemies():
            found_serious_enemy = False
            for enemy in character.getNearbyEnemies():
                if isinstance(enemy,src.characters.characterMap["Spiderling"]):
                    continue
                found_serious_enemy = True
            if character.is_low_health():
                if found_serious_enemy or character.health < 20:
                    quest = src.quests.questMap["Flee"]()
                    return ([quest],None)
                quest = src.quests.questMap["Fight"](suicidal=True)
                return ([quest],None)
            else:
                quest = src.quests.questMap["Fight"]()
                return ([quest],None)

        # go near the groundskeeper
        if not character.getBigPosition() == keeper_position:
            quest = src.quests.questMap["GoToTile"](targetPosition=keeper_position,disallowQ=True)
            return ([quest],None)
        
        # handle open menues
        submenue = character.macroState.get("submenue")
        if submenue and not ignoreCommands:
            if isinstance(submenue,src.menues.menuMap["ChatPartnerselection"]):
                if submenue.options is None:
                    return (None,("j","start conversation"))
                command = submenue.get_command_to_select_option(keeper)
                if command:
                    return (None,(command,"start conversation"))
                else:
                    return (None,(["esc"],"close menu"))
            if isinstance(submenue,src.chats.Chat):
                command = submenue.subMenu.get_command_to_select_option("set priorities")
                if not command:
                    command = ""
                return (None,(command+"j","continue conversation"))
            if submenue.tag == "groundskeeper_priority_configuration":
                if submenue.selected_duty == "scrap hammering":
                    return (None,("a","lower duty priority"))
                command = submenue.get_command_to_select_duty("scrap hammering")
                return (None,(command,"select duty"))
            return (None,(["esc"],"to close menu"))

        # open chat menu
        if character.container != keeper.container:
            return (None,(".","stand around confused"))
        return (None,("h","start talking"))

    def generateTextDescription(self):
        '''
        generates a text description of the text
        '''
        text = ["""
""",(src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"Talk to the groundskeeper and configure its duty priorities."),"""
Those duties determine what work the groundskeeper is doing.
Higher priorities mean tasks of that type will be done first.

Currently the "scrap hammering" duty has a high priority.
This means that the groundskeeper is spending much on that task.
Reduce priority of that duty to ensure the groundskeeper is focussing on more important duties.

"""]

        keeper = self.getGroundsKeeper()
        if keeper:
            keeper_position = keeper.getBigPosition()
            character_position = self.character.getBigPosition()
            direction_string = self.character.getTerrain().getDistanceDescription(character_position,keeper_position)
            direction_string = f"The groundskeeper is {direction_string}.\n"
            if character_position == keeper_position:
                direction_string = "You are in the room with the groundskeeper"

            text.append(f"""
{direction_string}
""")

        text.extend(["""
""",(src.pseudoUrwid.AttrSpec(src.interaction.ui_hint_color,"black"),"""Press h to talk to nearby clones or left click on a clone to talk to it.""")])
        return text

    def handleChangedDuty(self,extraInfo):
        '''
        handle the character having picked up an item
        '''
        self.triggerCompletionCheck(self.character,dryRun=False)

    def assignToCharacter(self, character):
        '''
        make the quest listen to character events
        '''
        if self.character:
            return None

        result = super().assignToCharacter(character)
        keeper = self.getGroundsKeeper()
        if keeper:
            self.startWatching(keeper,self.handleChangedDuty, "changedDutyPriority")
        return result

# register quest
src.quests.addType(StoryConfigureGroundskeeperPriorites)

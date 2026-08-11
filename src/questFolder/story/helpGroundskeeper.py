import src


class HelpGroundskeeper(src.quests.MetaQuestSequence):
    type = "HelpGroundskeeper"

    def __init__(self, description="help groundskeeper", creator=None, lifetime=None):
        questList = []
        super().__init__(questList, creator=creator, lifetime=lifetime)
        self.metaDescription = description

    def triggerCompletionCheck(self,character=None,dryRun=True):
        if not character:
            return False
        return False

    def getGroundsKeeper(self):
        keeper = None
        terrain = self.character.getHomeTerrain()
        for candidate in terrain.getAllCharacters():
            if not isinstance(candidate,src.characters.characterMap["GroundsKeeper"]):
                continue
            keeper = candidate
        return keeper

    def getNextStep(self,character,ignoreCommands=False,dryRun=True):

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
                try:
                    if submenue.subMenu.selectionIndex > 1:
                        return (None,("w"*(submenue.subMenu.selectionIndex-1),"move cursor"))
                except:
                    pass
                return (None,("j","continue conversation"))
            if submenue.tag == "builder_task_selection":
                return (None,("j","select task"))
            if submenue.tag == "builder_accept_quest":
                return (None,("j","accept quest"))
            if submenue.tag == "builder_task_confirm":
                if submenue.selectionIndex > 1:
                    return (None,("w","move cursor"))
                return (None,("j","answer"))
            return (None,(["esc"],"to close menu"))

        # open chat menu
        if character.container != keeper.container:
            return (None,(".","stand around confused"))
        return (None,("h","start talking"))

    def generateTextDescription(self):
        text = ["""
Talk to the groundskeeper and see what it needs help with.
""",(src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"""Help the groundskeeper with its work.""")]
        if self.lifetime:
            text.append(f"\nDo this for {self.lifetime} ticks. {self.getRemainingLifetime()} ticks remaining.\n")

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

    def handleNoBuilderQuest(self,extraInfo=None):
        self.postHandler()

    def handleNoConfirm(self,extraInfo=None):
        self.postHandler()

    def assignToCharacter(self,character):
        if self.character:
            return None

        self.startWatching(character,self.handleNoBuilderQuest,"no_builder_quest")
        self.startWatching(character,self.handleNoConfirm,"builder_task_noconfirm")
        return super().assignToCharacter(character)

src.quests.addType(HelpGroundskeeper)

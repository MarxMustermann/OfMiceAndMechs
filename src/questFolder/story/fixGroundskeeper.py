import src


class FixGroundskeeper(src.quests.MetaQuestSequence):
    type = "FixGroundskeeper"

    def __init__(self, description="fix groundskeeper", creator=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description

    def triggerCompletionCheck(self,character=None,dryRun=True):
        if not character:
            return False
        return False

    def getNextStep(self,character,ignoreCommands=False,dryRun=True):

        # no actions with sub quests
        if self.subQuests:
            return (None,None)
        
        # close open menues
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
            return (None,(["esc"],"to close menu"))

        # find the groundskeeper
        keeper_position = None
        keeper = None
        terrain = character.getHomeTerrain()
        for candidate in terrain.getAllCharacters():
            if not isinstance(candidate,src.characters.characterMap["GroundsKeeper"]):
                continue
            keeper_position = candidate.getBigPosition()
            keeper = candidate
        if not keeper_position:
            return self._solver_trigger_fail(dryRun,"keeper not found")

        # go to the groundskeeper
        if not character.getBigPosition() == keeper_position:
            quest = src.quests.questMap["GoToTile"](targetPosition=keeper_position)
            return ([quest],None)
        
        # open chat menu
        return (None,("h","start talking"))

    def generateTextDescription(self):
        text = ["""
Talk to the groundskeeper and ask why it is """,(src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"not working"),""".

""",(src.pseudoUrwid.AttrSpec(src.interaction.ui_hint_color,"black"),"""Press h to talk to nearby clones or left click on a clone to talk to it.""")]
        return text

    def handleFixedGroundskeeper(self,extraInfo=None):
        self.postHandler()

    def assignToCharacter(self,character):
        if self.character:
            return None

        self.startWatching(character,self.handleFixedGroundskeeper,"fixed groundskeeper")
        return super().assignToCharacter(character)

src.quests.addType(FixGroundskeeper)

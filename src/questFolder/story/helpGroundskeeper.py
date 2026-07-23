import src


class HelpGroundskeeper(src.quests.MetaQuestSequence):
    type = "HelpGroundskeeper"

    def __init__(self, description="help groundskeeper", creator=None):
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

        # go near the groundskeeper
        if not character.getBigPosition() == keeper_position:
            quest = src.quests.questMap["GoToTile"](targetPosition=keeper_position)
            return ([quest],None)
        
        # handle open menues
        submenue = character.macroState.get("submenue")
        if submenue and not ignoreCommands:
            if isinstance(submenue,src.menues.menuMap["ChatPartnerselection"]):
                if submenue.options is None:
                    return (None,("j","start conversation"))
                groundskeeper_index = None
                counter = 1
                for option in submenue.options.values():
                    if isinstance(option,src.characters.characterMap["GroundsKeeper"]):
                        groundskeeper_index = counter
                    counter += 1

                command = None
                if groundskeeper_index is not None:
                    command = ""
                    command += "s"*(submenue.selectionIndex-groundskeeper_index)
                    command += "w"*(groundskeeper_index-submenue.selectionIndex)
                    command += "j"
                if command:
                    return (None,(command,"start conversation"))
                else:
                    return (None,(["esc"],"close menu"))
            if isinstance(submenue,src.chats.Chat):
                return (None,("j","continue conversation"))
            if submenue.tag == "builder_task_selection":
                return (None,("j","continue conversation"))
            if submenue.tag == "builder_accept_quest":
                return (None,("j","accept quest"))
            return (None,(["esc"],"to close menu"))

        # open chat menu
        if character.container != keeper.container:
            return (None,(".","stand around confused"))
        return (None,("h","start talking"))

    def generateTextDescription(self):
        text = ["""
Talk to the groundskeeper and ask why it is not working.

Press h to talk to nearby clones or left click on a clone to talk to it."""]
        return text

    def handleNoBuilderQuest(self,extraInfo=None):
        self.postHandler()

    def assignToCharacter(self,character):
        if self.character:
            return None

        self.startWatching(character,self.handleNoBuilderQuest,"no_builder_quest")
        return super().assignToCharacter(character)

src.quests.addType(HelpGroundskeeper)

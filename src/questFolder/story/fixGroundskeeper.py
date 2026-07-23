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
                return (None,("j","start conversation"))
            if isinstance(submenue,src.chats.Chat):
                return (None,("j","continue conversation"))
            return (None,(["esc"],"to close menu"))

        keeper_position = (7,4,0)
        if not character.getBigPosition() == keeper_position:
            quest = src.quests.questMap["GoToTile"](targetPosition=keeper_position)
            return ([quest],None)
        
        # open chat menu
        return (None,("h","start talking"))

    def generateTextDescription(self):
        text = ["""
Talk to the groundskeeper and ask why it is not working.

Press h to talk to nearby clones or left click on a clone to talk to it."""]
        return text

    def handleFixedGroundskeeper(self,extraInfo=None):
        self.postHandler()

    def assignToCharacter(self,character):
        if self.character:
            return None

        self.startWatching(character,self.handleFixedGroundskeeper,"fixed groundskeeper")
        return super().assignToCharacter(character)

src.quests.addType(FixGroundskeeper)

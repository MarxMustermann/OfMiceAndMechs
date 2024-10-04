import src


class ReachOutStory(src.quests.MetaQuestSequence):
    type = "ReachOutStory"

    def __init__(self, description="reach out to implant", creator=None):
        questList = []
        super().__init__(creator=creator)
        self.metaDescription = description

    def triggerCompletionCheck(self,character=None):
        return

    def handleQuestsOpened(self,extraInfo=None):
        self.postHandler()

    def assignToCharacter(self,character):
        if self.character:
            return None

        self.startWatching(character,self.handleQuestsOpened,"opened quest menu")
        return super().assignToCharacter(character)

    def getNextStep(self,character=None,ignoreCommands=False, dryRun = True):
        if character.autoExpandQ:
            self.postHandler()
            character.runCommandString("q",nativeKey=True)
            return (None,(".",""))
        if not ignoreCommands and character.macroState.get("submenue"):
            return (None, (["esc"],"close submenu"))
        else:
            return (None, ("q","reach implant"))

src.quests.addType(ReachOutStory)

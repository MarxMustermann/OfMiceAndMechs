import src


class ReachOutStory(src.quests.MetaQuestSequence):
    type = "ReachOutStory"

    def __init__(self, description="reach out to implant", creator=None, reason=None):
        questList = []
        super().__init__(creator=creator)
        self.metaDescription = description
        self.type = "ReachOutStory"
        self.reason = reason

    def triggerCompletionCheck(self,character=None,dryRun=True):
        return False

    def generateTextDescription(self):
        '''
        get a long text description to show on the UI
        '''
        reasonString = ""
        if self.reason:
            reasonString = ", to "+self.reason
        text = [f"""
Contact your implant for further advice.

""",(src.interaction.urwid.AttrSpec(src.interaction.highlighted_ui_color,"default"),"""You can contact the implant by pressing tab after closing this menu."""),"""

Right now you are looking at the quest menu.
The quest menu shows you general instructions on how to do things.
Currently you are looking at the quest to reach out to you implant.

Once you contacted the implant this menu will hold more useful information.
"""]
        return text

    def handleQuestsOpened(self,extraInfo=None):
        return
        if self.character.quests[0] == self:
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
            return (None, (["tab"],"reach out to implant"))

src.quests.addType(ReachOutStory)

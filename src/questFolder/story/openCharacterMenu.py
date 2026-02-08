import src


class OpenCharacterMenu(src.quests.MetaQuestSequence):
    type = "OpenCharacterMenu"

    def __init__(self, description="open character menu", creator=None, lifetime=None, targetPosition=None, paranoid=False, showCoordinates=True,direction=None,reason=None):
        questList = []
        super().__init__(questList, creator=creator,lifetime=lifetime)
        self.metaDescription = description
        self.reason = reason

    def getNextStep(self,character=None,ignoreCommands=False,dryRun=True):

        if self.subQuests:
            return (None,None)

        if not character:
            return (None,None)

        submenue = character.macroState["submenue"]
        if submenue and not ignoreCommands:
            return (None,(["esc",],"close the menu"))

        return (None,("v","open character menu"))

    def generateTextDescription(self):
        text = []
        reason_string = ""
        if self.reason:
            reason_string = ", to "

        text.extend([f"""
Open the character menu by pressing v{reason_string}.
"""])
        return text

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.openedHelp, "opened character menu")
        super().assignToCharacter(character)

    def triggerCompletionCheck(self,character=None,dryRun=True):
        return False

    def openedHelp(self,extraInfo=None):
        self.postHandler()

src.quests.addType(OpenCharacterMenu)

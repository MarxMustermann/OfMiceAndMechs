import src


class OpenObserveMenu(src.quests.MetaQuestSequence):
    type = "OpenObserveMenu"

    def __init__(self, description="open observe menu", creator=None, lifetime=None, targetPosition=None, paranoid=False, showCoordinates=True,direction=None):
        questList = []
        super().__init__(questList, creator=creator,lifetime=lifetime)
        self.metaDescription = description

    def getNextStep(self,character=None,ignoreCommands=False,dryRun=True):

        if self.subQuests:
            return (None,None)

        if not character:
            return (None,None)

        submenue = character.macroState["submenue"]
        if submenue and not ignoreCommands:
            if not submenue.tag == "open observe info":
                return (None,(["esc",],"close the menu"))

        return (None,("o","open observe menu"))

    def generateTextDescription(self):
        text = []
        text.extend(["""
Open the help menu by pressing o after closing this menu.
"""])
        return text

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.openedObserve, "opened observe menu")
        super().assignToCharacter(character)

    def triggerCompletionCheck(self,character=None,dryRun=True):
        return False

    def openedObserve(self,extraInfo=None):
        self.postHandler()

src.quests.addType(OpenObserveMenu)

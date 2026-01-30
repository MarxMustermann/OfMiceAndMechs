import src


class OpenHelpMenu(src.quests.MetaQuestSequence):
    type = "OpenHelpMenu"

    def __init__(self, description="open help menu", creator=None, lifetime=None, targetPosition=None, paranoid=False, showCoordinates=True,direction=None):
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
            if submenue.tag not in ("configurationSelection",):
                return (None,(["esc",],"close the menu"))

        return (None,("?","open help menu"))

    def generateTextDescription(self):
        door = src.items.itemMap["Door"]()
        door.open = True
        door.walkable = False
        door.blocked = False

        text = []
        text.extend(["""
Open the help menu by pressing.
"""])
        return text

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.openedHelp, "opened help menu")
        super().assignToCharacter(character)

    def triggerCompletionCheck(self,character=None,dryRun=True):
        return False

    def openedHelp(self,extraInfo=None):
        self.postHandler()

src.quests.addType(OpenHelpMenu)

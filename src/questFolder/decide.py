import src
import random

class Decide(src.quests.MetaQuestSequence):
    type = "Decide"
    lowLevel = True

    def __init__(self, description="decide",reason=None):
        super().__init__()
        self.metaDescription = description
        self.reason = reason

    def generateTextDescription(self):
        reasonString = ""
        if self.reason:
            reasonString = ", to "+self.reason
        text = f"""
Decide{reasonString}.

"""
        return text

    def getNextStep(self,character=None,ignoreCommands=False,dryRun=True):

        # handle weird edge cases
        if self.subQuests:
            return (None,None)
        if not character:
            return (None,None)

        # handle menus
        submenue = character.macroState["submenue"]
        if not submenue or submenue.tag != "player_quest_selection":
            if not dryRun:
                self.postHandler()
            return (None,("+","end quest"))

        if submenue.selectionIndex > 1+submenue.shift:
            return (None,("w","move cursor up"))
        if submenue.selectionIndex < 1+submenue.shift:
            return (None,("s","move cursor down"))


        # select current option
        return (None,("j","select current option"))


    def triggerCompletionCheck(self,character=None,dryRun=True):
        if not character:
            return False

        submenue = character.macroState["submenue"]
        if not submenue or submenue.tag != "player_quest_selection":
            if not dryRun:
                self.postHandler()
            return True

        return False

src.quests.addType(Decide)

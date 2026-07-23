import src


class DoGroundskeeping(src.quests.MetaQuestSequence):
    type = "DoGroundskeeping"

    def __init__(self, description="do groundskeeping", creator=None):
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

        # be useful
        quest1 = src.quests.questMap["BeUsefull"](strict=True,endOnIdle=True)
        quest2 = src.quests.questMap["GoToPosition"](targetPosition=(6,6,0))
        quest3 = src.quests.questMap["WaitQuest"](lifetime=10)
        return ([quest3,quest2,quest1],None)

    def generateTextDescription(self):
        text = ["""
Do some groundskeeping."""]
        return text

src.quests.addType(DoGroundskeeping)

import src

class EpochQuest(src.quests.MetaQuestSequence):
    type = "EpochQuest"

    def __init__(self, description="epoch quest", creator=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description

        # save initial state and register
        quest = src.quests.questMap["DoEpochChallenge"]()
        self.subQuests.append(quest)
        quest.activate()

    def generateTextDescription(self):
        text = """
When you were promoted to commander of this base you recieved the burden of the epoch quest.

This means you will have to complete the tasks the epoch artwork gives you.

Completing tasks will reward you with glass tears.
Those glass tears can be used to upgrade your character or your base.


Use the epoch artwork to get tasks and collect your rewards.
"""
        return text

    """
    never complete
    """
    def triggerCompletionCheck(self,character=None):
        return

src.quests.addType(EpochQuest)

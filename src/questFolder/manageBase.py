import src

class ManageBase(src.quests.MetaQuestSequence):
    def __init__(self, description="manage base", creator=None, command=None, lifetime=None):
        questList = []
        super().__init__(questList, creator=creator, lifetime=lifetime)
        self.metaDescription = description
        self.type = "ManageBase"
        self.shortCode = "M"

        self.addQuest(src.quests.questMap["ReloadTraps"]())
        self.addQuest(src.quests.questMap["CleanTraps"]())

    def solver(self, character):
        return super().solver(character)

src.quests.addType(ManageBase)

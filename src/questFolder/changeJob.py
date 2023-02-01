import src

class ChangeJob(src.quests.MetaQuestSequence):
    type = "ChangeJob"

    def __init__(self, description="take on new duty"):
        super().__init__()
        self.metaDescription = description

        self.addQuest(src.quests.questMap["Assimilate"](description="set new duties"))
        self.addQuest(src.quests.questMap["TrainSkill"]())

    def generateTextDescription(self):
        return """
Retrain for a different duty.

Use the basic trainer to learn a new skill.
Reset your duties at the assimilator aftwerward.
"""

src.quests.addType(ChangeJob)

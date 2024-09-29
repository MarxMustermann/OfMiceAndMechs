import src


class Vanish(src.quests.MetaQuestSequenceV2):
    type = "Vanish"

    def __init__(self, description="vanish", creator=None, reason=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        self.reason = reason

    def getNextStep(self,character=None,ignoreCommands=False, dryRun = True):
        if character.container:
            character.container.removeCharacter(character)
            self.postHandler()
            return (None,None)
        return (None,None)


src.quests.addType(Vanish)

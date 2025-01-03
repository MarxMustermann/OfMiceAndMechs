import src


class Vanish(src.quests.MetaQuestSequence):
    type = "Vanish"

    def __init__(self, description="vanish", creator=None, reason=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        self.reason = reason

    def getNextStep(self,character=None,ignoreCommands=False, dryRun = True):
        if not character:
            return (None,None)

        if character.container:
            character.container.removeCharacter(character)
            self.postHandler()
            return (None,None)

        return (None,None)


src.quests.addType(Vanish)

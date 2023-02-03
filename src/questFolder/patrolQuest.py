import src

class PatrolQuest(src.quests.MetaQuestSequence):
    type = "PatrolQuest"

    def __init__(self, description="patrol", waypoints=None, lifetime=None):
        questList = []
        super().__init__(questList, lifetime=lifetime)

        self.metaDescription = description

        # save initial state and register
        self.waypointIndex = 0
        self.waypoints = waypoints

    def triggerCompletionCheck(self, character=None):
        return False

    def solver(self,character):
        if not self.subQuests:
            """
            quest = src.quests.questMap["GoToTile"](targetPosition=self.waypoints[self.waypointIndex],paranoid=True)
            quest.assignToCharacter(character)
            quest.activate()
            self.addQuest(quest)
            """

            quest = src.quests.questMap["SecureTile"](toSecure=self.waypoints[self.waypointIndex],endWhenCleared=True)
            quest.assignToCharacter(character)
            quest.activate()
            self.addQuest(quest)


            self.waypointIndex += 1
            if self.waypointIndex >= len(self.waypoints):
                self.waypointIndex = 0
            return
        super().solver(character)

src.quests.addType(PatrolQuest)

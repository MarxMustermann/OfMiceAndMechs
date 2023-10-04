import src


class ReduceFoodConsumption(src.quests.MetaQuestSequence):
    type = "ReduceFoodConsumption"

    def __init__(self, description="reduce food consumption",reason=None):
        questList = []
        super().__init__(questList)
        self.metaDescription = description
        self.reason = reason

    def generateTextDescription(self):
        reason = ""
        if self.reason:
            reason = f", to {self.reason}"
        text = [f"""
reduce the food consumption on the base{reason}.

"""]
        return text

    def solver(self, character):
        (nextQuests,nextCommand) = self.getNextStep(character)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
            return

        if nextCommand:
            character.runCommandString(nextCommand)
            return
        super().solver(character)

    def getSolvingCommandString(self, character, dryRun=True):
        nextStep = self.getNextStep(character)
        if nextStep == (None,None):
            return super().getSolvingCommandString(character)
        return self.getNextStep(character)[1]

    def generateSubquests(self, character=None):
        (nextQuests,nextCommand) = self.getNextStep(character,ignoreCommands=True)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
            return

    def unhandledSubQuestFail(self,extraParam):
        self.fail(extraParam["reason"])

    def getNextStep(self,character=None,ignoreCommands=False):
        if not self.subQuests:
            npcs = []
            if character.container.isRoom:
                npcs.extend(character.container.characters)
            npcs.extend(character.getTerrain().characters)
            for room in character.getTerrain().rooms:
                if room == character.container:
                    continue
                npcs.extend(room.characters)

            for npc in npcs:
                if npc == character:
                    continue

                if character.container != npc.container:
                    if character.getBigPosition() == npc.getBigPosition():
                        return (None,(".","wait"))
                    quest = src.quests.questMap["GoToTile"](targetPosition=npc.getBigPosition(),reason=f"get near {npc.name}")
                    return ([quest],None)

                if character.getDistance(npc.getPosition()) > 1:
                    quest = src.quests.questMap["GoToPosition"](targetPosition=npc.getPosition(),reason=f"get in reach of {npc.name}")
                    return ([quest],None)

                return (None,("M",f"attack {npc.name}"))

            self.postHandler()
            return (None,None)

        return (None,None)

    def triggerCompletionCheck(self,character=None):
        return False

src.quests.addType(ReduceFoodConsumption)

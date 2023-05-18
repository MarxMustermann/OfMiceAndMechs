import src
import random

class ReduceFoodConsumption(src.quests.MetaQuestSequence):
    type = "ReduceFoodConsumption"

    def __init__(self, description="reduce food consumption"):
        questList = []
        super().__init__(questList)
        self.metaDescription = description

    def generateTextDescription(self):
        text = """
reduce the food consumption on the base.

"""
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

                if npc.dead:
                    input("dead npcs")
                    continue
                if not character.container == npc.container:
                    quest = src.quests.questMap["GoToTile"](targetPosition=npc.getBigPosition())
                    return ([quest],None)

                if character.getDistance(npc.getPosition()) > 1:
                    quest = src.quests.questMap["GoToPosition"](targetPosition=npc.getPosition())
                    return ([quest],None)

                return (None,"M")

            self.postHandler()
            return (None,None)

        return (None,None)
    
    def triggerCompletionCheck(self,character=None):
        return False

src.quests.addType(ReduceFoodConsumption)

import src

class TakeOverBase(src.quests.MetaQuestSequence):
    def __init__(self, description="join base"):
        super().__init__()
        self.metaDescription = description

    def getSolvingCommandString(self,character,dryRun=True):
        if not self.subQuests:
            if character.macroState["submenue"]:
                return ["esc"]
        return super().getSolvingCommandString(character,dryRun=dryRun)

    def generateTextDescription(self):
        return """
There is no commander. This is a problem.

Insects are growing within the hives in the abbandoned farms.
Without a commander the hives will continue growing.
Sooner or later their attacks will break the bases defences.

Also the base is in maintenance mode.
So leaving is not an option. You are stuck here. 
It is not safe here, but it is safer in the base than outside.

So stay here until those issues are resolved.
Join the crew of this base and help defend it against the insects.
The harder you work the safer you will be.


press d to get a description on how to join the base
"""

    def generateSubquests(self,character=None):
        if not self.subQuests:
            if self.character.rank == None:
                quest = src.quests.questMap["Assimilate"]()
                quest.assignToCharacter(self.character)
                quest.activate()
                self.addQuest(quest)
                quest.generateSubquests(character)
                return
        super().generateSubquests()

    def solver(self,character):
        if not self.subQuests:
            self.generateSubquests(character)
            return
        return super().solver(character)

    def triggerCompletionCheck(self):
        return

src.quests.addType(TakeOverBase)

import src


class EpochQuest(src.quests.MetaQuestSequence):
    type = "EpochQuest"

    def __init__(self, description="epoch quest", creator=None, storyText=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        self.storyText = storyText

    def getNextStep(self,character=None,ignoreCommands=False):
        if not self.subQuests:
            quest = src.quests.questMap["DoEpochChallenge"](reason="further the cause and gain glass tears")
            return ([quest],None)
        return (None,None)

    def generateTextDescription(self):
        out = []

        if self.storyText:
            storyText = self.storyText
        else:
            storyText = """
When you were promoted to commander of this base you received the burden of the epoch quest.
This means you will have to complete the tasks the epoch artwork gives you.
"""
        text = f"""
{storyText}
"""
        out.append(text)

        if not self.subQuests:
            out.append((src.interaction.urwid.AttrSpec("#f00", "black"),"""
Use the epoch artwork to get a task to complete.
Press r to generate the subquest that will help you do that.

"""))
        else:
            out.append((src.interaction.urwid.AttrSpec("#080", "black"),"""
Completing tasks will reward you with glass tears.
Those glass tears can be used to upgrade your character or your base.


This quest has a subquest.
press d to see the subtasks description.
"""))

        return out

    """
    never complete
    """
    def triggerCompletionCheck(self,character=None):
        return

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

    def solver(self, character):
        if self.triggerCompletionCheck(character):
            return

        (nextQuests,nextCommand) = self.getNextStep(character)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
            return

        if nextCommand:
            character.runCommandString(nextCommand[0])
            return
        super().solver(character)

src.quests.addType(EpochQuest)

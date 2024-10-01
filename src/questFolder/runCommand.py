import src


class RunCommand(src.quests.MetaQuestSequenceV2):
    type = "RunCommand"

    def __init__(self, description="press ", creator=None, command=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.command = None
        self.ranCommand = False
        self.metaDescription = description+" "+"".join(command)

        self.shortCode = "c"

        if command:
            self.setParameters({"command":command})

    def generateTextDescription(self):
        return f"""
This quest wants you to press the following keys:

{self.command}

To be honest:
This quest is deprecated and should be removed.
If you see this that means that did not happen, yet.
This stuff does not work very well, so just do exactly that.
Do nothing else like moving around.

good luck!
"""

    def setParameters(self,parameters):
        if "command" in parameters:
            self.command = parameters["command"]
        return super().setParameters(parameters)

    def triggerCompletionCheck(self,character=None):
        if self.ranCommand:
            self.postHandler()
            return

        return

    def getNextStep(self,character,ignoreCommands=False, dryRun = True):
        if not dryRun:
            self.ranCommand = True
        return (None,(self.command,"Running Command"))


src.quests.addType(RunCommand)

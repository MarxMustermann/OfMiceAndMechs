import src

class RunCommand(src.quests.MetaQuestSequence):
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
        return """
This quest wants you to press the following keys:

%s

To be honest:
This quest is deprecated and should be removed.
If you see this that means that did not happen, yet.
This stuff does not work very well, so just do exactly that.
Do nothing else like moving around.

good luck!
"""%(self.command,)

    def setParameters(self,parameters):
        if "command" in parameters:
            self.command = parameters["command"]
        return super().setParameters(parameters)

    def triggerCompletionCheck(self,character=None):
        if self.ranCommand:
            self.postHandler()
            return

        return

    def getSolvingCommandString(self,character,dryRun=True):
        return self.command

    def solver(self, character):
        self.activate()
        self.triggerCompletionCheck(character)

        if not self.ranCommand:
            character.runCommandString(self.command)
            self.ranCommand = True
        self.triggerCompletionCheck(character)

src.quests.addType(RunCommand)

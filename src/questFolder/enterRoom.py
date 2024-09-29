import src


class EnterRoom(src.quests.MetaQuestSequenceV2):
    type = "EnterRoom"

    def __init__(self, description="enter room", creator=None, command=None, lifetime=None):
        super().__init__([], creator=creator, lifetime=lifetime)
        self.metaDescription = description

    def generateTextDescription(self):
        return """
Enter the room.

This quest is a workaround quest.
This means it is needed for other quests to work,
but has no purpose on its own.

So just complete the quest and don't think about it too much."""

    def triggerCompletionCheck(self,character=None):
        return

    def enteredRoom(self,character=None):
        self.postHandler()

    def getNextStep(self, character=None, ignoreCommands=False, dryRun = True): 
        if character.xPosition%15 == 0:
            return (None,("d","enter room"))
        if character.xPosition%15 == 14:
            return (None,("a","enter room"))
        if character.yPosition%15 == 0:
            return (None,("s","enter room"))
        if character.yPosition%15 == 14:
            return (None,("w","enter room"))
        
        return (None,None)


    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.enteredRoom, "entered room")

        super().assignToCharacter(character)

src.quests.addType(EnterRoom)

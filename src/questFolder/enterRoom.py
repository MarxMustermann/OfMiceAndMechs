import src

class EnterRoom(src.quests.MetaQuestSequence):
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
        return

    def solver(self,character):
        if character.xPosition%15 == 0:
            character.runCommandString("d")
        if character.xPosition%15 == 14:
            character.runCommandString("a")
        if character.yPosition%15 == 0:
            character.runCommandString("s")
        if character.yPosition%15 == 14:
            character.runCommandString("w")

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.enteredRoom, "entered room")

        super().assignToCharacter(character)

src.quests.addType(EnterRoom)

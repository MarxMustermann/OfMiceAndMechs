import src

class GetQuestFromQuestArtwork(src.quests.MetaQuestSequence):
    type = "GetQuestFromQuestArtwork"

    def __init__(self, description="get quest from quest artwork"):
        super().__init__()
        self.metaDescription = description

    def generateTextDescription(self):
        return """
Get a quest from the quest artwork.
The quest artwork looks like this: QA
You can find it in the command center.

Activate the quest artwork to fetch a quest."""

    def triggerCompletionCheck(self,character=None):
        if not character:
            return

        for quest in character.quests:
            if quest.type == "BeUsefull":
                if len(quest.subQuests) > 1:
                    self.postHandler()
                    self.completed = True
                    return True
        return False

    def handleQuestAssigned(self):
        self.postHandler()
        self.completed = True

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.handleQuestAssigned, "got quest assigned")

        super().assignToCharacter(character)

    def solver(self, character):
        if not self.subQuests:
            self.generateSubquests(character)
            if self.subQuests:
                return

            command = self.getSolvingCommandString(character,dryRun=False)
            if command:
                character.runCommandString(command)
                return

        super().solver(character)

    def getSolvingCommandString(self,character,dryRun=True):
        if self.subQuests:
            return

        submenue = character.macroState.get("submenue")
        if submenue:
            if isinstance(submenue,src.interaction.SelectionMenu):
                return ["enter"]
            return ["esc"]

        if isinstance(character.container, src.rooms.Room):
            room = character.container
            for item in room.itemsOnFloor:
                if not item.bolted:
                    continue
                if item.type == "QuestArtwork":
                    direction = None
                    if item.getPosition() == (character.xPosition-1,character.yPosition,0):
                        direction = "a"
                    if item.getPosition() == (character.xPosition+1,character.yPosition,0):
                        direction = "d"
                    if item.getPosition() == (character.xPosition,character.yPosition-1,0):
                        direction = "w"
                    if item.getPosition() == (character.xPosition,character.yPosition+1,0):
                        direction = "s"
                    
                    if direction:
                        return "J"+direction
        return super().getSolvingCommandString(character,dryRun=dryRun)

    def generateSubquests(self,character):
        if self.subQuests:
            return

        room = character.container

        if not isinstance(character.container, src.rooms.Room):
            quest = src.quests.questMap["GoHome"]()
            quest.active = True
            quest.assignToCharacter(character)
            self.addQuest(quest)
            return

        for item in room.itemsOnFloor:
            if not item.bolted:
                continue
            if item.type == "QuestArtwork":
                direction = None
                if item.getPosition() == (character.xPosition-1,character.yPosition,0):
                    direction = "a"
                if item.getPosition() == (character.xPosition+1,character.yPosition,0):
                    direction = "d"
                if item.getPosition() == (character.xPosition,character.yPosition-1,0):
                    direction = "w"
                if item.getPosition() == (character.xPosition,character.yPosition+1,0):
                    direction = "s"
                
                if direction:
                    return 

                quest = src.quests.questMap["GoToPosition"](targetPosition=item.getPosition(),ignoreEndBlocked=True,description="go to quest artwork ")
                quest.active = True
                quest.assignToCharacter(character)
                self.addQuest(quest)
                return

        self.addQuest(src.quests.questMap["GoToTile"](targetPosition=(7,7,0),description="go to command centre"))
        return

src.quests.addType(GetQuestFromQuestArtwork)

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
        self.triggerCompletionCheck(self.character)

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.handleQuestAssigned, "got quest assigned")

        super().assignToCharacter(character)

    def solver(self,character):
        if not self.subQuests:
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
                        quest = src.quests.questMap["RunCommand"](command=list("J"+direction+".j")+3*["enter"],description="activate quest artwork ")
                        self.addQuest(quest)
                        quest.assignToCharacter(character)
                        quest.activate()
                        return 

                    quest = src.quests.questMap["GoToPosition"](targetPosition=item.getPosition(),ignoreEndBlocked=True,description="go to quest artwork ")
                    quest.active = True
                    quest.assignToCharacter(character)
                    self.addQuest(quest)
                    return

            if not "Questing" in character.duties:
                directions = [(-1,0),(1,0),(0,-1),(0,1)]
                random.shuffle(directions)
                for direction in directions:
                    newPos = (room.xPosition+direction[0],room.yPosition+direction[1])
                    if room.container.getRoomByPosition(newPos):
                        self.addQuest(src.quests.questMap["GoToTile"](targetPosition=newPos))
                        return
                return
            else:
                self.addQuest(src.quests.questMap["GoToTile"](targetPosition=(7,7,0),description="go to command centre"))
                return
        super().solver(character)

src.quests.addType(GetQuestFromQuestArtwork)

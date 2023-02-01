import src

class GetPromotion(src.quests.MetaQuestSequence):
    type = "GetPromotion"

    def __init__(self, targetRank, description="get promotion"):
        super().__init__()
        self.metaDescription = description
        self.targetRank = targetRank

    def generateTextDescription(self):
        text = """
You have gained enough reputation to be promoted.
Promotions are handled by the assimilator.

Getting promoted has several advantages:

* Your implant will be upgraded and you will be faster and hit harder.
* You can take on more duties. Each extra duty gives you some extra reputation."""
        if self.character.rank == 6:
            text += """
* You will be able to get subordinates."""
        else:
            text += """
* You will be able to handle more subordinates.

Use the assimilator to fetch your promottion.
You need to reach rank %s to complete the quest.
"""%(self.character.rank-1,)

        return text

    def wrapedTriggerCompletionCheck(self, extraInfo):
        if not self.active:
            return

        self.triggerCompletionCheck(extraInfo)

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.wrapedTriggerCompletionCheck, "got promotion")

        super().assignToCharacter(character)

    def triggerCompletionCheck(self,character=None):
        if not character:
            return

        if character.reputation == 0:
            self.fail()
            return True

        if character.rank <= self.targetRank:
            self.postHandler()
            return True
        return False

    def generateSubquests(self,character):
        if not self.active:
            return

        if self.subQuests:
            return

        room = character.container

        if not isinstance(character.container, src.rooms.Room):
            quest = src.quests.questMap["GoHome"](description="go to command centre")
            self.addQuest(quest)
            quest.assignToCharacter(character)
            quest.activate()
            return

        for item in room.itemsOnFloor:
            if not item.bolted:
                continue
            if not item.type == "Assimilator":
                continue

            if item.getPosition() == (character.xPosition-1,character.yPosition,0):
                quest = src.quests.questMap["RunCommand"](command=list("Ja.")+["enter"]*10,description="activate the assimilator \nby pressing")
                quest.activate()
                self.addQuest(quest)
                return
            if item.getPosition() == (character.xPosition+1,character.yPosition,0):
                quest = src.quest.questMap["RunCommand"](command=list("Jd.")+["enter"]*10,description="activate the assimilator \nby pressing")
                quest.activate()
                self.addQuest(quest)
                return
            if item.getPosition() == (character.xPosition,character.yPosition-1,0):
                quest = src.quest.questMap["RunCommand"](command=list("Jw.")+["enter"]*10,description="activate the assimilator \nby pressing")
                quest.activate()
                self.addQuest(quest)
                return
            if item.getPosition() == (character.xPosition,character.yPosition+1,0):
                quest = src.quests.questMap["RunCommand"](command=list("Js.")+["enter"]*10,description="activate the assimilator \nby pressing")
                quest.activate()
                self.addQuest(quest)
                return
            quest = GoToPosition(targetPosition=item.getPosition(),ignoreEndBlocked=True,description="go to assimilator ")
            quest.active = True
            quest.assignToCharacter(character)
            self.addQuest(quest)
            return
        quest = src.quests.questMap["GoToTile"](targetPosition=(7,7,0),description="go to command centre")
        self.addQuest(quest)
        quest.assignToCharacter(character)
        quest.activate()
        return

    def solver(self,character):
        self.triggerCompletionCheck(character)
        if not self.subQuests:
            self.generateSubquests(character)
            return
        super().solver(character)

src.quests.addType(GetPromotion)

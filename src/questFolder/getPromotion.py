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
            text += f"""
* You will be able to handle more subordinates.

Use the assimilator to fetch your promotion.
You need to reach rank {self.character.rank-1} to complete the quest.
"""

        return text

    def handleGotPromotion(self, extraInfo):
        self.postHandler()

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.handleGotPromotion, "got promotion")

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

    def getSolvingCommandString(self,character,dryRun=True):
        if self.subQuests:
            return

        submenue = character.macroState.get("submenue")
        if submenue:
            if isinstance(submenue,src.interaction.SelectionMenu):
                return ["enter"]
            return ["esc"]

        room = character.container
        if not isinstance(character.container, src.rooms.Room):
            return

        for item in room.itemsOnFloor:
            if not item.bolted:
                continue
            if not item.type == "Assimilator":
                continue

            if item.getPosition() == (character.xPosition-1,character.yPosition,0):
                return "Ja"
            if item.getPosition() == (character.xPosition+1,character.yPosition,0):
                return "Jd"
            if item.getPosition() == (character.xPosition,character.yPosition-1,0):
                return "Jw"
            if item.getPosition() == (character.xPosition,character.yPosition+1,0):
                return "Js"
        return super().getSolvingCommandString(character,dryRun=dryRun)

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
                return
            if item.getPosition() == (character.xPosition+1,character.yPosition,0):
                return
            if item.getPosition() == (character.xPosition,character.yPosition-1,0):
                return
            if item.getPosition() == (character.xPosition,character.yPosition+1,0):
                return
            quest = src.quests.questMap["GoToPosition"](targetPosition=item.getPosition(),ignoreEndBlocked=True,description="go to assimilator ")
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

            if self.subQuests:
                return

            command = self.getSolvingCommandString(character,dryRun=False)
            if command:
                character.runCommandString(command)
                return

        super().solver(character)

src.quests.addType(GetPromotion)

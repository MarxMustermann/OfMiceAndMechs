import src

class TrainSkill(src.quests.MetaQuestSequence):
    type = "TrainSkill"

    def __init__(self, description="train skill",skillToTrain=None):
        super().__init__()
        self.metaDescription = description
        self.skillToTrain = skillToTrain

    def generateTextDescription(self):
        if not self.character.skills:
            return """
Without skills you are useless to the base.
Train a skill or the base won't accept you.

Activate the basic trainer in the command centre to start training a skill"""
        else:
            return """
Skills are what part of what makes you useful to the base.
Train an additional skill.
This will allow you to do a different duty.

Activate the basic trainer in the command centre to start training a skill"""


    def triggerCompletionCheck(self,character=None):
        if not character:
            return False

        return False

    def handleSkillLearned(self,extraInfo):
        self.postHandler()

    def generateSubquests(self,character):
        if not self.active:
            return
        if self.completed:
            1/0

        if self.subQuests:
            return

        if not isinstance(character.container, src.rooms.Room):
            quest = src.quests.questMap["GoHome"](description="go back to command centre")
            self.addQuest(quest)
            quest.activate()
            quest.assignToCharacter(character)
            return

        room = character.container

        for item in room.getItemsByType("BasicTrainer",needsBolted=True):
            if item.getPosition() == (character.xPosition-1,character.yPosition,0):
                return
            if item.getPosition() == (character.xPosition+1,character.yPosition,0):
                return
            if item.getPosition() == (character.xPosition,character.yPosition-1,0):
                return
            if item.getPosition() == (character.xPosition,character.yPosition+1,0):
                return
            quest = src.quests.questMap["GoToPosition"](targetPosition=item.getPosition(),ignoreEndBlocked=True,description="go to basic trainer  ")
            quest.activate()
            quest.assignToCharacter(character)
            self.addQuest(quest)
            quest.generatePath(character)
            return
        quest = src.quests.questMap["GoHome"](description="go to command centre")
        self.addQuest(quest)
        quest.assignToCharacter(character)
        quest.activate()
        return

    def getSolvingCommandString(self,character,dryRun=True):
        if not self.subQuests:
            submenue = character.macroState.get("submenue")
            if submenue:
                if isinstance(submenue,src.interaction.SelectionMenu):
                    if self.skillToTrain:
                        counter = 0
                        for option in submenue.options.items():
                            counter += 1
                            if option[1] == self.skillToTrain:
                                break
                        offset = counter-submenue.selectionIndex
                        if offset > 0:
                            return "s"*offset
                        if offset < 0:
                            return "w"*(-offset)
                    return ["enter"]
                return ["esc"]
            room = character.container

            if not isinstance(character.container, src.rooms.Room):
                return super().getSolvingCommandString(character,dryRun=dryRun)

            for item in room.itemsOnFloor:
                if not item.bolted:
                    continue
                if not item.type == "BasicTrainer":
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

    def solver(self,character):
        self.triggerCompletionCheck(character)
        if not self.subQuests:
            self.generateSubquests(character)
            if self.subQuests:
                return

        if not self.subQuests:
            command = self.getSolvingCommandString(character)
            if command:
                character.runCommandString(command)
                return
            
        super().solver(character)

    def handleMovement(self, extraInfo):
        if not self.active:
            return

        self.generateSubquests(extraInfo[0])

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.handleMovement, "moved")
        self.startWatching(character,self.handleSkillLearned, "learnedSkill")

        super().assignToCharacter(character)

src.quests.addType(TrainSkill)

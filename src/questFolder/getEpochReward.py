import src

class GetEpochReward(src.quests.MetaQuestSequence):
    type = "GetEpochReward"

    def __init__(self, description="get epoch reward", creator=None,rewardType=None,reason=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description + " (" + rewardType + ")"
        self.rewardType = rewardType
        self.reason = reason

    def generateTextDescription(self):
        out = []
        reason = ""
        if self.reason:
            reason = ",\nto %s"%(self.reason,)
        text = """
Claim a reward for completing the epoch challenge%s.

You accumulated some glass tears.
Spend them to claim the actual reward (%s).
"""%(reason,self.rewardType,)

        if self.rewardType == "room building":
            text += """
Spawn a room builder. A room building clone will build rooms.
This will allow you to focus on getting more building materials.
"""
        if self.rewardType == "scavenging":
            text += """
Spawn a scavenger. A scavenging clone will collect items from outside.
This will allow you to focus on producing walls.
"""
        if self.rewardType == "machine operating":
            text += """
Spawn a machine operator. A machine operating clone will operate machines and produce items.
This will allow you to focus on supplying materials for producing walls.
"""

        if self.rewardType == "resource fetching":
            text += """
Spawn a resource fetcher. A resource fetching clone will carry items from room to room.
This will allow you to focus on other tasks.
"""

        if self.rewardType == "resource gathering":
            text += """
Spawn a resource gatherer. A resource gathering clone will collect scrap from scrap field.
This will allow you to focus on other tasks.
"""

        if self.rewardType == "painting":
            text += """
Spawn a painter. A painting clone will draw stock piles and build sites.
This will allow you to focus on other tasks.
"""

        if self.rewardType == "machine placing":
            text += """
Spawn a machine placer. A machine placing clone will produce and place machines.
This will allow you to focus on other tasks.
"""

        if self.rewardType == "hauling":
            text += """
Spawn a hauler. A hauling clone will carry items withins rooms.
This will allow you to focus on other tasks.
"""

        text += """
(buying the wrong reward may break the tutorial, but is FUN)
"""

        out.append(text)
        return out

    def getNextStep(self,character=None,ignoreCommands=False):
        
        while self.subQuests:
            if not self.subQuests[-1].completed:
                break
            self.subQuests.pop()

        if self.subQuests:
            return (None,None)

        if character.macroState["submenue"] and isinstance(character.macroState["submenue"],src.interaction.SelectionMenu) and not ignoreCommands:
            submenue = character.macroState["submenue"]
            if submenue.tag == "rewardSelection":
                rewardIndex = 0
                if self.rewardType == "room building":
                    rewardIndex = 8
                if self.rewardType == "scavenging":
                    rewardIndex = 10
                if self.rewardType == "machine operating":
                    rewardIndex = 3
                if self.rewardType == "resource fetching":
                    rewardIndex = 4
                if self.rewardType == "resource gathering":
                    rewardIndex = 2
                if self.rewardType == "painting":
                    rewardIndex = 6

                if rewardIndex == 0:
                    counter = 1
                    for option in submenue.options.items():
                        if option[1] == self.rewardType:
                            break
                        counter += 1
                    rewardIndex = counter

                offset = rewardIndex-submenue.selectionIndex
                if offset > 0:
                    return (None,("s"*offset+"j","to get your reward"))
                else:
                    return (None,("w"*(-offset)+"j","to get your reward"))
            else:
                submenue = character.macroState["submenue"]
                counter = 2
                command = ""
                if submenue.selectionIndex > counter:
                    command += "w"*(submenue.selectionIndex-counter)
                if submenue.selectionIndex < counter:
                    command += "s"*(counter-submenue.selectionIndex)
                command += "j"
                return (None,(command,"to get your reward"))

        if character.macroState["submenue"] and not ignoreCommands:
            return (None,(["esc"],"to exit submenu"))

        pos = character.getBigPosition()

        if pos == (7,7,0):
            if not character.container.isRoom:
                quest = src.quests.questMap["EnterRoom"]()
                return ([quest],None)

            epochArtwork = character.container.getItemsByType("EpochArtwork")[0]
            command = None
            if character.getPosition(offset=(1,0,0)) == epochArtwork.getPosition():
                command = "d"
            if character.getPosition(offset=(-1,0,0)) == epochArtwork.getPosition():
                command = "a"
            if character.getPosition(offset=(0,1,0)) == epochArtwork.getPosition():
                command = "s"
            if character.getPosition(offset=(0,-1,0)) == epochArtwork.getPosition():
                command = "w"

            if command:
                return (None,("J"+command,"to activate the epoch artwork"))

            quest = src.quests.questMap["GoToPosition"](targetPosition=epochArtwork.getPosition(), description="go to epoch artwork",ignoreEndBlocked=True)
            return ([quest],None)

        quest = src.quests.questMap["GoHome"](description="go to command centre")
        return ([quest],None)

    def handleGotEpochReward(self, extraInfo):
        if self.completed:
            1/0
        if not self.active:
            return

        self.postHandler()
        return

    def assignToCharacter(self, character):
        if self.character:
            return
        
        self.startWatching(character,self.handleGotEpochReward, "got epoch reward")

        return super().assignToCharacter(character)

    """
    never complete
    """
    def triggerCompletionCheck(self,character=None):
        return False

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


src.quests.addType(GetEpochReward)

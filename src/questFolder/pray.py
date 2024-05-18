import src


class Pray(src.quests.MetaQuestSequence):
    type = "Pray"

    def __init__(self, description="pray", creator=None, targetPosition=None, targetPositionBig=None,reason=None,shrine=True):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        self.targetPosition = targetPosition
        self.targetPositionBig = targetPositionBig
        self.reason = reason
        self.shrine = shrine

    def handlePrayed(self, extraInfo):
        if self.completed:
            1/0
        if not self.active:
            return

        self.postHandler()
        return

    def assignToCharacter(self, character):
        if self.character:
            return None

        self.startWatching(character,self.handlePrayed, "prayed")

        return super().assignToCharacter(character)

    def generateTextDescription(self):
        reason = ""
        if self.reason:
            reason = f", to {self.reason}"
        return f"""
pray on {self.targetPosition}{reason}.
"""

    def triggerCompletionCheck(self,character=None):
        if not character:
            return False

        if self.targetPositionBig and character.getBigPosition() != self.targetPositionBig:
            return False

        if not character.container.isRoom:
            self.fail()
            return True

        return False

    def getNextStep(self,character,ignoreCommands=False):
        if self.subQuests:
            return (None,None)

        if character.macroState["submenue"] and isinstance(character.macroState["submenue"],src.interaction.SelectionMenu) and not ignoreCommands:

            submenue = character.macroState["submenue"]
            rewardIndex = 0
            if rewardIndex == 0:
                counter = 1
                for option in submenue.options.items():
                    if option[1] == "challenge":
                        break
                    counter += 1
                rewardIndex = counter

            offset = rewardIndex-submenue.selectionIndex
            command = ""
            if offset > 0:
                command += "s"*offset
            else:
                command += "w"*(-offset)
            command += "j"
            return (None,(command,"pray for favour"))

        if self.targetPositionBig and character.getBigPosition() != self.targetPositionBig:
            quest = src.quests.questMap["GoToTile"](targetPosition=self.targetPositionBig,reason="get to the tile the machine is on")
            return ([quest],None)

        pos = character.getPosition()
        if self.targetPosition not in (pos,(pos[0],pos[1]+1,pos[2]),(pos[0]-1,pos[1],pos[2]),(pos[0]+1,pos[1],pos[2]),(pos[0],pos[1]-1,pos[2])):
            quest = src.quests.questMap["GoToPosition"](targetPosition=self.targetPosition,ignoreEndBlocked=True,reason="get near the machine")
            return ([quest],None)

        if self.shrine:
            description = "pray at the shrine"
            activationCommand = "ssj"
        else:
            description = "pray at statue"
            activationCommand = "sj"
        if (pos[0],pos[1],pos[2]) == self.targetPosition:
            return (None,("j"+activationCommand,description))
        if (pos[0]-1,pos[1],pos[2]) == self.targetPosition:
            return (None,("Ja"+activationCommand,description))
        if (pos[0]+1,pos[1],pos[2]) == self.targetPosition:
            return (None,("Jd"+activationCommand,description))
        if (pos[0],pos[1]-1,pos[2]) == self.targetPosition:
            return (None,("Jw"+activationCommand,description))
        if (pos[0],pos[1]+1,pos[2]) == self.targetPosition:
            return (None,("Js"+activationCommand,description))
        return None

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
        (nextQuests,nextCommand) = self.getNextStep(character)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
            return

        if nextCommand:
            character.runCommandString(nextCommand[0])
            return
        super().solver(character)

src.quests.addType(Pray)

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

    def getNextStep(self,character,ignoreCommands=False, dryRun=True):
        if self.subQuests:
            return (None,None)

        if character.macroState["submenue"] and not ignoreCommands:
            submenue = character.macroState["submenue"]
            if isinstance(submenue,src.menuFolder.SelectionMenu.SelectionMenu):
                foundOption = False
                rewardIndex = 0
                if rewardIndex == 0:
                    counter = 1
                    for option in submenue.options.items():
                        if self.shrine:
                            if option[1] == "challenge":
                                foundOption = True
                                break
                        else:
                            if option[1] == "pray":
                                foundOption = True
                                break
                        counter += 1
                    rewardIndex = counter

                if not foundOption:
                    return (None,(["esc"],"to close menu"))

                offset = rewardIndex-submenue.selectionIndex
                command = ""
                if offset > 0:
                    command += "s"*offset
                else:
                    command += "w"*(-offset)
                command += "j"
                return (None,(command,"pray for favour"))
            else:
                return (None,(["esc"],"to close menu"))

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

    @staticmethod
    def generateDutyQuest(beUsefull,character,currentRoom, dryRun):
        for checkRoom in beUsefull.getRandomPriotisedRooms(character,currentRoom):
            glassStatues = checkRoom.getItemsByType("GlassStatue")
            foundStatue = None
            for checkStatue in glassStatues:
                if checkStatue.charges >= 5:
                    continue
                if not checkStatue.handleItemRequirements():
                    continue
                foundStatue = checkStatue

            if not foundStatue:
                continue

            quest = src.quests.questMap["Pray"](targetPosition=foundStatue.getPosition(),targetPositionBig=foundStatue.getBigPosition(),shrine=False)
            if not dryRun:
                beUsefull.idleCounter = 0
            return ([quest],None)

        for checkRoom in beUsefull.getRandomPriotisedRooms(character,currentRoom):
            shrines = checkRoom.getItemsByType("Shrine")
            foundShrine = None
            for checkShrine in shrines:
                if not checkShrine.isChallengeDone():
                    continue
                foundShrine = checkShrine

            if not foundShrine:
                continue

            quest = src.quests.questMap["Pray"](targetPosition=foundShrine.getPosition(),targetPositionBig=foundShrine.getBigPosition())
            if not dryRun:
                beUsefull.idleCounter = 0
            return ([quest],None)
        return (None,None)

src.quests.addType(Pray)

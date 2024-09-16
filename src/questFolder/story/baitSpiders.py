import src


class BaitSpiders(src.quests.MetaQuestSequence):
    type = "BaitSpiders"

    def __init__(self, description="bait spiders", creator=None, lifetime=None, targetPositionBig=None, paranoid=False, showCoordinates=True,direction=None,reason=None):
        questList = []
        super().__init__(questList, creator=creator,lifetime=lifetime)
        self.metaDescription = description
        self.reason = reason
        self.targetPositionBig = targetPositionBig
        self.phase = "bait"

    def getSolvingCommandString(self, character, dryRun=True):
        nextStep = self.getNextStep(character)
        if nextStep == (None,None):
            return super().getSolvingCommandString(character)
        return self.getNextStep(character)[1]

    def getNextStep(self,character=None,ignoreCommands=False, dryRun=True):

        if self.subQuests:
            return (None,None)

        if not character:
            return (None,None)

        phase = self.phase

        if phase == "bait":
            if character.getPosition() != self.targetPositionBig:
                quest = src.quests.questMap["GoToTile"](targetPosition=self.targetPositionBig,reason="be able to bait the spiders",description="go to spiders")
                return ([quest],None)

        if phase == "wait":
            for enemy in self.character.getNearbyEnemies():
                if not (enemy.getSpacePosition() in self.spiderPositions):
                    phase = "run"
                    if not dryRun:
                        self.phase = phase

        if phase == "wait":
            return (None,(".","wait for the spider to attack"))

        if phase == "run":
            if character.getPosition() != (6,7,0):
                quest = src.quests.questMap["GoToTile"](targetPosition=(6,7,0),reason="get to safety",description="run back to base",paranoid=True)
                phase = "end"
                if not dryRun:
                    self.phase = phase
                return ([quest],None)
        return (None,None)

        baseCommand = "d"
        nextPos = (character.xPosition+1,character.yPosition,0)
        if character.yPosition < 6:
            baseCommand = "s"
            nextPos = (character.xPosition,character.yPosition+1,0)
        elif character.yPosition > 6:
            baseCommand = "w"
            nextPos = (character.xPosition,character.yPosition-1,0)

        items = character.container.getItemByPosition(nextPos)
        
        # save to move
        if (not items) or (items[0].type != "TriggerPlate"):
            return (None,(baseCommand,"move"))

        # block trigger plates
        if character.inventory:
            return (None,("L"+baseCommand,"block TrickerPlate"))

        # check of traps are in cooldown
        foundActiveTrap = False
        for offset in ((1,0,0),(-1,0,0),(0,1,0),(0,-1,0)):
            checkPos = (nextPos[0]+offset[0],nextPos[1]+offset[1],nextPos[2]+offset[2])

            for item in character.container.getItemByPosition(checkPos):
                if item.type != "RodTower":
                    continue
                if item.isInCoolDown():
                    continue
                foundActiveTrap = True
                break

        if not foundActiveTrap:
            return (None,(baseCommand,"step on trap"))
        
        return (None,("J"+baseCommand,"trigger trap"))

    def solver(self, character):
        if self.triggerCompletionCheck(character):
            return

        (nextQuests,nextCommand) = self.getNextStep(character, dryRun=False)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
            return

        if nextCommand:
            character.runCommandString(nextCommand[0])
            return
        super().solver(character)

    def generateTextDescription(self):
        triggerPlate = src.items.itemMap["TriggerPlate"]()
        rodTower = src.items.itemMap["RodTower"]()

        result = [f"""
The outside is still a dangerous place.
There are groups of spiders lurking near the base entrance.
The spiders are very aggressive.

Use this to lead them to their deaths.
Enter the tile the spiders are on and wait until you have their attention.
Then run away and lead them into the bases defences.

The base is prepared to withstand the attack.
Guard the arena behind the trap room to ensure no spider slips through.

"""]
        if self.phase == "wait":
            result.append(f"The last known spider positions are:\n{self.spiderPositions}")
        return result

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.wrapedTriggerCompletionCheck, "moved")
        self.startWatching(character,self.changedTile, "changedTile")
        self.startWatching(character,self.hurt, "hurt")
        super().assignToCharacter(character)

    def hurt(self, extraInfo=None):
        if self.phase == "wait":
            self.phase = "run"

    def changedTile(self, extraInfo=None):
        if self.phase == "bait":
            if self.character.getBigPosition() == self.targetPositionBig:
                self.phase = "wait"

                self.spiderPositions = []
                for enemy in self.character.getNearbyEnemies():
                    self.spiderPositions.append(enemy.getSpacePosition())
        else:
            if self.phase == "wait":
                self.phase = "bait"

    def wrapedTriggerCompletionCheck(self, extraInfo):
        if self.completed:
            1/0
        if not self.active:
            return

        self.triggerCompletionCheck(extraInfo[0])

    def triggerCompletionCheck(self,character=None):
        if not character:
            return False

        if self.phase == "end" and not self.subQuests:
            self.postHandler()
            return True

        return False

src.quests.addType(BaitSpiders)

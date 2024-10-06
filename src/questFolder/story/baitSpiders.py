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
        self.spiderPositions = []


    def getNextStep(self,character=None,ignoreCommands=False, dryRun=True):

        if self.subQuests:
            return (None,None)

        if not character:
            return (None,None)

        if character.macroState["submenue"] and not ignoreCommands:
            return (None,(["esc"],"to close menu"))

        phase = self.phase

        if phase == "bait":
            if character.getBigPosition() != self.targetPositionBig:
                quest = src.quests.questMap["GoToTile"](targetPosition=self.targetPositionBig,reason="be able to bait the spiders",description="go to spiders")
                return ([quest],None)
            phase = "wait"

            if not dryRun:
                self.spiderPositions = []
                for enemy in self.character.getNearbyEnemies():
                    self.spiderPositions.append(enemy.getSpacePosition())
                self.phase = phase

        if phase == "wait":
            for enemy in self.character.getNearbyEnemies():
                if self.spiderPositions and not (enemy.getSpacePosition() in self.spiderPositions):
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

    def generateTextDescription(self):
        triggerPlate = src.items.itemMap["TriggerPlate"]()
        rodTower = src.items.itemMap["RodTower"]()

        result = [f"""
You reach out to the implant and it answers:

The outside is still a dangerous place.
There are groups of spiders lurking near the base entrance.
The spiders are very aggressive.

Use this to lead them to their deaths.
Enter the tile the spiders are on and wait until you have their attention.
Then run away and lead them into the bases defences.

The base is prepared to withstand the attack.
Guard the arena behind the trap room to ensure no spider slips through.

"""]
        result.append(f"phase: {self.phase}\n")
        result.append(f"target position: {self.targetPositionBig}\n")
        if self.phase == "wait":
            result.append(f"The last known spider positions are:\n{self.spiderPositions}")
        return result

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.wrapedTriggerCompletionCheck, "moved")
        self.startWatching(character,self.changedTile, "changedTile")
        self.startWatching(character,self.attacked, "attacked")
        super().assignToCharacter(character)

    def attacked(self, extraInfo=None):
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

        if self.phase == "bait" and not self.subQuests:
            foundEnemy = False
            for otherChar in self.character.getTerrain().charactersByTile.get(self.targetPositionBig,[]):
                if otherChar.faction == character.faction:
                    continue
                foundEnemy = True
                break
            if not foundEnemy:
                self.postHandler()
                return True

        if self.phase == "end" and not self.subQuests:
            self.postHandler()
            return True

        return False

src.quests.addType(BaitSpiders)

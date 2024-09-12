import src

class ResetFaction(src.quests.MetaQuestSequence):
    type = "ResetFaction"

    def __init__(self, description="reset faction", creator=None, lifetime=None, targetPosition=None, paranoid=False, showCoordinates=True,direction=None,reason=None):
        questList = []
        super().__init__(questList, creator=creator,lifetime=lifetime)
        self.metaDescription = description
        self.reason = reason

    def getSolvingCommandString(self, character, dryRun=True):
        nextStep = self.getNextStep(character)
        if nextStep == (None,None):
            return super().getSolvingCommandString(character)
        return self.getNextStep(character)[1]

    def getNextStep(self,character=None,ignoreCommands=False):

        if self.subQuests:
            return (None,None)

        if not character:
            return (None,None)

        if not character.getBigPosition() == (7,8,0):
            quest = src.quests.questMap["GoToTile"](targetPosition=(7,8,0),reason="go to spawning room",description="go to spawning room")
            return ([quest],None)

        if not character.container.isRoom:
            return (None,None)

        factionSetter = character.container.getItemByType("FactionSetter")
        if not factionSetter:
            self.fail(reason="no faction setter found")
            return (None,None)

        itemPos = factionSetter.getPosition()
        if character.getDistance(itemPos) > 1:
            quest = src.quests.questMap["GoToPosition"](targetPosition=factionSetter.getPosition(),reason="to be able to use the faction setter",description="go to faction setter",ignoreEndBlocked=True)
            return ([quest],None)

        direction = ""
        if character.getPosition(offset=(1,0,0)) == itemPos:
            direction = "d"
        if character.getPosition(offset=(-1,0,0)) == itemPos:
            direction = "a"
        if character.getPosition(offset=(0,1,0)) == itemPos:
            direction = "s"
        if character.getPosition(offset=(0,-1,0)) == itemPos:
            direction = "w"

        return (None,(direction+"j","reset faction"))

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

    def generateTextDescription(self):
        return ["""
You are safe for now, but there is a deeper problem with the base.
It fails to detect you as part of their faction.
Maybe your faction marker got corrupted during the meltdown. 

We need to reset it or we can't make use of this base.
Reset your faction marker to solve this.

The base has infrastructure for this.
New clones are integrated using a FactionSetter.
Use it to reset your faction marker.

"""]

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.wrapedTriggerCompletionCheck, "set faction")
        super().assignToCharacter(character)

    def wrapedTriggerCompletionCheck(self):
        if self.completed:
            1/0
        if not self.active:
            return

        self.triggerCompletionCheck(self.character)

    def triggerCompletionCheck(self,character=None):
        if not character:
            return False

        if not character.faction == "city #2":
            return False

        self.postHandler()

src.quests.addType(ResetFaction)

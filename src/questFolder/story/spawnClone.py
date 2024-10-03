import src

class SpawnClone(src.quests.MetaQuestSequence):
    type = "SpawnClone"

    def __init__(self, description="spawn clone", creator=None, lifetime=None, targetPosition=None, paranoid=False, showCoordinates=True,direction=None,reason=None):
        questList = []
        super().__init__(questList, creator=creator,lifetime=lifetime)
        self.metaDescription = description
        self.reason = reason

    def getNextStep(self,character=None,ignoreCommands=False,dryRun=True):

        if self.subQuests:
            return (None,None)

        if not character:
            return (None,None)

        if not character.getBigPosition() == (7,8,0):
            quest = src.quests.questMap["GoToTile"](targetPosition=(7,8,0),reason="go to spawning room",description="go to spawning room")
            return ([quest],None)

        if not character.container.isRoom:
            return (None,None)

        growthTank = character.container.getItemByType("GrowthTank")
        if not growthTank:
            self.fail(reason="no growth tank found")
            return (None,None)

        itemPos = growthTank.getPosition()
        if character.getDistance(itemPos) > 1:
            quest = src.quests.questMap["GoToPosition"](targetPosition=growthTank.getPosition(),reason="to be able to use the growth tank",description="go to growth tank",ignoreEndBlocked=True)
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

        if growthTank.filled:
            return (None,(direction+"j","spawn clone"))
        else:
            return (None,(direction+"j","refill growth tank"))

    def generateTextDescription(self):
        return ["""
You reach out to your implant and it answers:

The base is a safe place to be now.
But every base as small as it may be should have a crew of at least two.
That way the base can recover in case a fatalaty.

Spawn a clone to have a backup in case of emergencies.
"""]

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.handleSpawn, "spawned clone")
        self.startWatching(character,self.noFlask, "no flask")
        super().assignToCharacter(character)

    def noFlask(self,extraInfo=None):
        self.fail("no flask")

    def handleSpawn(self,extraInfo=None):
        if self.completed:
            1/0
        if not self.active:
            return

        self.postHandler()

    def wrapedTriggerCompletionCheck(self,character=None):
        pass

    def triggerCompletionCheck(self,character=None):
        if not character:
            return False

        return False
        self.postHandler()

src.quests.addType(SpawnClone)

import src

class ResetFaction(src.quests.MetaQuestSequence):
    type = "ResetFaction"

    def __init__(self, description="reset faction", creator=None, lifetime=None, targetPosition=None, paranoid=False, showCoordinates=True,direction=None,reason=None):
        questList = []
        super().__init__(questList, creator=creator,lifetime=lifetime)
        self.metaDescription = description
        self.reason = reason

    def getNextStep(self,character=None,ignoreCommands=False, dryRun = True):

        if self.subQuests:
            return (None,None)

        if not character:
            return (None,None)

        if not character.getBigPosition() == (7,8,0):
            quest = src.quests.questMap["GoToTile"](targetPosition=(7,8,0),reason="go to spawning room",description="go to spawning room")
            return ([quest],None)
        
        # find the spawning room
        rooms = character.getTerrain().getRoomByPosition((7,8,0))
        if not rooms:
            if not dryRun:
                self.fail("spawning room found")
            return True

        # find the faction setter
        items = rooms[0].getItemsByType("FactionSetter")
        if not items or items[0].type not in ("FactionSetter",):
            if not dryRun:
                self.fail("no faction setter found")
            return True

        # use the faction setter
        item = items[0]
        quest = src.quests.questMap["ActivateItem"](targetPosition=item.getPosition(),targetPositionBig=item.getBigPosition(),reason="reset your faction marker")
        return ([quest],None)

    def generateTextDescription(self):
        return ["""
You reach out to your implant and it answers:

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

    def wrapedTriggerCompletionCheck(self, extraInfo):
        if self.completed:
            1/0
        if not self.active:
            return

        self.triggerCompletionCheck(self.character,dryRun=False)

    def triggerCompletionCheck(self,character=None,dryRun=True):
        if not character:
            return False

        if not character.faction == "city #1":
            return False

        if not dryRun:
            self.postHandler()
        return True

src.quests.addType(ResetFaction)

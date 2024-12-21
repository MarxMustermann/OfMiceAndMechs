import src

class BecomeStronger(src.quests.MetaQuestSequence):
    type = "BecomeStronger"

    def __init__(self, description="become stronger", creator=None, lifetime=None, reason=None, targetStrength=1):
        questList = []
        super().__init__(questList, creator=creator,lifetime=lifetime)
        self.metaDescription = description
        self.reason = reason
        self.targetStrength = targetStrength

    def getNextStep(self,character=None,ignoreCommands=False, dryRun = True):

        if self.subQuests:
            return (None,None)

        if not character:
            return (None,None)

        terrain = character.getTerrain()

        if not character.weapon:
            pass
        else:
            shouldSharpen = False
            if character.weapon.baseDamage < 15:
                shouldSharpen = True
            else:
                if character.searchInventory("Grindstone"):
                    shouldSharpen = True

            if shouldSharpen:
                for room in terrain.rooms:
                    for item in room.getItemsByType("SwordSharpener",needsBolted=True):
                        quest = src.quests.questMap["SharpenPersonalSword"]()
                        return ([quest],None)

        if not character.armor:
            pass
        else:
            if character.armor.armorValue < 3:
                for room in terrain.rooms:
                    for item in room.getItemsByType("ArmorReinforcer",needsBolted=True):
                        quest = src.quests.questMap["ReinforcePersonalArmor"]()
                        return ([quest],None)

        if character.inventory:
            quest = src.quests.questMap["ClearInventory"]()
            return ([quest],None)

        quest = src.quests.questMap["Adventure"]()
        return ([quest],None)

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

    def generateTextDescription(self):
        return ["""
The dungeons are too hard for you. 
You need to be stronger, to take them on.

Get some upgrades to be stronger.
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

        if character.getStrengthSelfEstimate() < self.targetStrength:
            return False

        self.postHandler()
        return True

src.quests.addType(BecomeStronger)

import src


class StoryHeal(src.quests.MetaQuestSequence):
    type = "StoryHeal"

    def __init__(self, description="heal yourself", creator=None, lifetime=None):
        questList = []
        super().__init__(questList, creator=creator,lifetime=lifetime)
        self.metaDescription = description

    def getTargetRoom(self):
        terrain = self.character.getTerrain()
        for room in terrain.rooms:
            if room.getItemByType("SiegeManager"):
                return room
        return None

    def getNextStep(self,character=None,ignoreCommands=False,dryRun=True):

        if self.subQuests:
            return (None,None)

        if not character:
            return (None,None)

        # set up helper variables
        terrain = character.getTerrain()

        # heal conventionally
        if self.character.canHeal():
            quest = src.quests.questMap["Heal"](toSecure=targetposition,endWhenCleared=True)
            return ([quest],None)

        # try to use a Coalburner
        hasCoalburner = False
        for room in character.getTerrain().rooms:
            if room.getEnemies(character):
                continue
            coalBurners = room.getItemsByType("CoalBurner",needsBolted=True)
            if not coalBurners:
                continue
            hasCoalburner = True
            for coalBurner in coalBurners:
                if coalBurner.getMoldFeed(character):
                    quest = src.quests.questMap["ActivateItem"](targetPosition=coalBurner.getPosition(),targetPositionBig=coalBurner.getBigPosition(),reason="heal")
                    return ([quest],None)

        # abort
        return self._solver_trigger_fail(dryRun,"no way to heal")

    def generateTextDescription(self):
        text = ["""
""",(src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"Heal yourself."),f"""
"""]
        return text

    def triggerCompletionCheck(self,character=None,dryRun=True):
        if not character:
            return False
        if character.health >= character.adjustedMaxHealth:
            if not dryRun:
                self.postHandler()
            return False
        return False

src.quests.addType(StoryHeal)
